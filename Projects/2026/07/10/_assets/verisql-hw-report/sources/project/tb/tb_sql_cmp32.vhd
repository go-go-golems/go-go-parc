library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use std.env.all;
use work.sql_pkg.all;

entity tb_sql_cmp32 is
end entity;

architecture test of tb_sql_cmp32 is
  signal lhs_s       : word32_t := (others => '0');
  signal rhs_s       : word32_t := (others => '0');
  signal is_null_s   : std_logic := '0';
  signal opcode_s    : std_logic_vector(2 downto 0) := OP_EQ;
  signal predicate_s : std_logic;

  type integer_array_t is array (natural range <>) of integer;
  constant VALUES : integer_array_t := (-1000000, -100, -1, 0, 1, 100, 1000000);

  function reference_result(
    lhs_value : word32_t;
    rhs_value : word32_t;
    null_value : std_logic;
    operation : std_logic_vector(2 downto 0)
  ) return std_logic is
    variable result_v : boolean := false;
  begin
    if operation = OP_IS_NULL then
      result_v := null_value = '1';
    elsif operation = OP_IS_NOT_NULL then
      result_v := null_value = '0';
    elsif null_value = '1' then
      result_v := false;
    else
      case operation is
        when OP_EQ => result_v := signed(lhs_value) = signed(rhs_value);
        when OP_NE => result_v := signed(lhs_value) /= signed(rhs_value);
        when OP_LT => result_v := signed(lhs_value) < signed(rhs_value);
        when OP_LE => result_v := signed(lhs_value) <= signed(rhs_value);
        when OP_GT => result_v := signed(lhs_value) > signed(rhs_value);
        when OP_GE => result_v := signed(lhs_value) >= signed(rhs_value);
        when others => result_v := false;
      end case;
    end if;

    if result_v then
      return '1';
    end if;
    return '0';
  end function;
begin
  dut : entity work.sql_cmp32
    port map (
      lhs_i       => lhs_s,
      rhs_i       => rhs_s,
      is_null_i   => is_null_s,
      opcode_i    => opcode_s,
      predicate_o => predicate_s
    );

  stimulus : process
  begin
    for null_case in 0 to 1 loop
      if null_case = 0 then
        is_null_s <= '0';
      else
        is_null_s <= '1';
      end if;
      for opcode_value in 0 to 7 loop
        opcode_s <= std_logic_vector(to_unsigned(opcode_value, opcode_s'length));
        for lhs_index in VALUES'range loop
          lhs_s <= std_logic_vector(to_signed(VALUES(lhs_index), DATA_WIDTH));
          for rhs_index in VALUES'range loop
            rhs_s <= std_logic_vector(to_signed(VALUES(rhs_index), DATA_WIDTH));
            wait for 1 ns;
            assert predicate_s = reference_result(lhs_s, rhs_s, is_null_s, opcode_s)
              report "comparator mismatch"
              severity failure;
          end loop;
        end loop;
      end loop;
    end loop;

    report "tb_sql_cmp32 PASS" severity note;
    stop;
    wait;
  end process;
end architecture;
