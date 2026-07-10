library ieee;
use ieee.std_logic_1164.all;

use work.sql_pkg.all;

-- Fixed contract used by the prototype database:
--   * four packed signed INT32 columns per input row;
--   * one NULL bit per column;
--   * four independently configured predicates reduced with AND;
--   * one-entry elastic output register using valid/ready flow control.
--
-- Lane 0 occupies bits 31 downto 0. Predicate slot 0 occupies the least
-- significant slice of each packed configuration bus.
entity sql_predicate_accel is
  port (
    clk_i : in std_logic;
    rst_i : in std_logic;

    cfg_enable_i : in std_logic_vector(PREDICATE_COUNT - 1 downto 0);
    cfg_column_i : in std_logic_vector(PREDICATE_COUNT * 2 - 1 downto 0);
    cfg_opcode_i : in std_logic_vector(PREDICATE_COUNT * 3 - 1 downto 0);
    cfg_rhs_i    : in std_logic_vector(PREDICATE_COUNT * DATA_WIDTH - 1 downto 0);

    in_valid_i : in  std_logic;
    in_ready_o : out std_logic;
    in_row_i   : in  std_logic_vector(COLUMN_COUNT * DATA_WIDTH - 1 downto 0);
    in_null_i  : in  std_logic_vector(COLUMN_COUNT - 1 downto 0);

    out_valid_o : out std_logic;
    out_ready_i : in  std_logic;
    out_match_o : out std_logic
  );
end entity sql_predicate_accel;

architecture rtl of sql_predicate_accel is
  signal match_comb_s : std_logic;

  signal valid_q      : std_logic;
  signal match_q      : std_logic;
  signal in_ready_s   : std_logic;
  signal next_valid_s : std_logic;
  signal next_match_s : std_logic;
begin
  predicate_datapath : entity work.sql_predicate_datapath(rtl)
    port map (
      cfg_enable_i => cfg_enable_i,
      cfg_column_i => cfg_column_i,
      cfg_opcode_i => cfg_opcode_i,
      cfg_rhs_i    => cfg_rhs_i,
      in_row_i     => in_row_i,
      in_null_i    => in_null_i,
      match_o      => match_comb_s
    );

  next_state : entity work.elastic_match_step(rtl)
    port map (
      current_valid_i => valid_q,
      current_match_i => match_q,
      rst_i           => rst_i,
      in_valid_i      => in_valid_i,
      in_match_i      => match_comb_s,
      out_ready_i     => out_ready_i,
      in_ready_o      => in_ready_s,
      next_valid_o    => next_valid_s,
      next_match_o    => next_match_s
    );

  output_register : process(clk_i) is
  begin
    if rising_edge(clk_i) then
      valid_q <= next_valid_s;
      match_q <= next_match_s;
    end if;
  end process output_register;

  in_ready_o  <= in_ready_s;
  out_valid_o <= valid_q;
  out_match_o <= match_q;
end architecture rtl;
