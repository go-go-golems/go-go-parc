library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use std.env.all;
use work.sql_pkg.all;

entity tb_sql_predicate_accel is
end entity;

architecture test of tb_sql_predicate_accel is
  subtype row_bus_t is std_logic_vector(COLUMN_COUNT * DATA_WIDTH - 1 downto 0);
  subtype rhs_bus_t is std_logic_vector(PREDICATE_COUNT * DATA_WIDTH - 1 downto 0);

  signal clk_s : std_logic := '0';
  signal rst_s : std_logic := '1';

  signal cfg_enable_s : std_logic_vector(PREDICATE_COUNT - 1 downto 0) := (others => '0');
  signal cfg_column_s : std_logic_vector(PREDICATE_COUNT * 2 - 1 downto 0) := (others => '0');
  signal cfg_opcode_s : std_logic_vector(PREDICATE_COUNT * 3 - 1 downto 0) := (others => '0');
  signal cfg_rhs_s    : rhs_bus_t := (others => '0');

  signal in_valid_s : std_logic := '0';
  signal in_ready_s : std_logic;
  signal in_row_s   : row_bus_t := (others => '0');
  signal in_null_s  : std_logic_vector(COLUMN_COUNT - 1 downto 0) := (others => '0');

  signal out_valid_s : std_logic;
  signal out_ready_s : std_logic := '1';
  signal out_match_s : std_logic;

  function set_word(bus_value : row_bus_t; lane : natural; value : integer)
    return row_bus_t is
    variable result_v : row_bus_t := bus_value;
  begin
    result_v((lane + 1) * DATA_WIDTH - 1 downto lane * DATA_WIDTH) :=
      std_logic_vector(to_signed(value, DATA_WIDTH));
    return result_v;
  end function;

  function make_row(a : integer; b : integer; c : integer; d : integer)
    return row_bus_t is
    variable result_v : row_bus_t := (others => '0');
  begin
    result_v := set_word(result_v, 0, a);
    result_v := set_word(result_v, 1, b);
    result_v := set_word(result_v, 2, c);
    result_v := set_word(result_v, 3, d);
    return result_v;
  end function;

  function set_rhs(bus_value : rhs_bus_t; slot : natural; value : integer)
    return rhs_bus_t is
    variable result_v : rhs_bus_t := bus_value;
  begin
    result_v((slot + 1) * DATA_WIDTH - 1 downto slot * DATA_WIDTH) :=
      std_logic_vector(to_signed(value, DATA_WIDTH));
    return result_v;
  end function;
begin
  clk_s <= not clk_s after 5 ns;

  dut : entity work.sql_predicate_accel
    port map (
      clk_i         => clk_s,
      rst_i         => rst_s,
      cfg_enable_i  => cfg_enable_s,
      cfg_column_i  => cfg_column_s,
      cfg_opcode_i  => cfg_opcode_s,
      cfg_rhs_i     => cfg_rhs_s,
      in_valid_i    => in_valid_s,
      in_ready_o    => in_ready_s,
      in_row_i      => in_row_s,
      in_null_i     => in_null_s,
      out_valid_o   => out_valid_s,
      out_ready_i   => out_ready_s,
      out_match_o   => out_match_s
    );

  stimulus : process
    variable rhs_v : rhs_bus_t;
  begin
    -- slot 0: column 0 >= 10
    -- slot 1: column 1 < 20
    -- slot 2: column 2 IS NOT NULL
    cfg_enable_s <= "0111";
    cfg_column_s(1 downto 0) <= "00";
    cfg_column_s(3 downto 2) <= "01";
    cfg_column_s(5 downto 4) <= "10";
    cfg_opcode_s(2 downto 0) <= OP_GE;
    cfg_opcode_s(5 downto 3) <= OP_LT;
    cfg_opcode_s(8 downto 6) <= OP_IS_NOT_NULL;
    rhs_v := (others => '0');
    rhs_v := set_rhs(rhs_v, 0, 10);
    rhs_v := set_rhs(rhs_v, 1, 20);
    cfg_rhs_s <= rhs_v;

    wait until rising_edge(clk_s);
    wait until rising_edge(clk_s);
    rst_s <= '0';

    -- Matching row.
    in_row_s <= make_row(10, 19, 7, 0);
    in_null_s <= "0000";
    in_valid_s <= '1';
    wait until rising_edge(clk_s);
    wait for 1 ns;
    assert out_valid_s = '1' and out_match_s = '1'
      report "matching row was not accepted" severity failure;

    -- A NULL in selected column 2 must reject the row.
    in_row_s <= make_row(10, 19, 0, 0);
    in_null_s <= "0100";
    wait until rising_edge(clk_s);
    wait for 1 ns;
    assert out_valid_s = '1' and out_match_s = '0'
      report "NULL semantics mismatch" severity failure;

    -- Load a matching row, then stall it for two complete edges.
    in_row_s <= make_row(11, 1, 3, 0);
    in_null_s <= "0000";
    wait until rising_edge(clk_s);
    wait for 1 ns;
    assert out_valid_s = '1' and out_match_s = '1'
      report "expected matching payload before stall" severity failure;

    out_ready_s <= '0';
    in_row_s <= make_row(9, 1, 3, 0); -- non-match waiting at input
    wait for 1 ns;
    assert in_ready_s = '0' report "in_ready must deassert under stall" severity failure;
    wait until rising_edge(clk_s);
    wait for 1 ns;
    assert out_valid_s = '1' and out_match_s = '1' and in_ready_s = '0'
      report "payload changed during first stalled edge" severity failure;
    wait until rising_edge(clk_s);
    wait for 1 ns;
    assert out_valid_s = '1' and out_match_s = '1' and in_ready_s = '0'
      report "payload changed during second stalled edge" severity failure;

    -- Drain and replace in the same edge. The waiting row is non-matching.
    out_ready_s <= '1';
    wait until rising_edge(clk_s);
    wait for 1 ns;
    assert out_valid_s = '1' and out_match_s = '0'
      report "elastic replacement failed" severity failure;

    in_valid_s <= '0';
    wait until rising_edge(clk_s);
    wait for 1 ns;
    assert out_valid_s = '0' report "output valid did not drain" severity failure;

    report "tb_sql_predicate_accel PASS" severity note;
    stop;
    wait;
  end process;
end architecture;
