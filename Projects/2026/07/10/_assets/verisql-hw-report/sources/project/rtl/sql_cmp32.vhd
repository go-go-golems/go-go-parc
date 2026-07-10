library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.sql_pkg.all;

-- Combinational SQL scalar predicate cell.
--
-- Signed less-than is deliberately lowered to sign-bit selection plus an
-- unsigned comparison.  formal/prove.py proves that this implementation is
-- equivalent to mathematical signed INT32 comparison for every input pair.
entity sql_cmp32 is
  port (
    lhs_i       : in  word32_t;
    rhs_i       : in  word32_t;
    is_null_i   : in  std_logic;
    opcode_i    : in  std_logic_vector(2 downto 0);
    predicate_o : out std_logic
  );
end entity;

architecture rtl of sql_cmp32 is
begin
  evaluate : process(all)
    variable equal_v   : boolean;
    variable less_v    : boolean;
    variable greater_v : boolean;
    variable result_v  : boolean;
  begin
    equal_v := lhs_i = rhs_i;

    if lhs_i(DATA_WIDTH - 1) /= rhs_i(DATA_WIDTH - 1) then
      less_v := lhs_i(DATA_WIDTH - 1) = '1';
    else
      less_v := unsigned(lhs_i) < unsigned(rhs_i);
    end if;

    if rhs_i(DATA_WIDTH - 1) /= lhs_i(DATA_WIDTH - 1) then
      greater_v := rhs_i(DATA_WIDTH - 1) = '1';
    else
      greater_v := unsigned(rhs_i) < unsigned(lhs_i);
    end if;

    result_v := false;
    if opcode_i = OP_IS_NULL then
      result_v := is_null_i = '1';
    elsif opcode_i = OP_IS_NOT_NULL then
      result_v := is_null_i = '0';
    elsif is_null_i = '1' then
      -- SQL comparison with NULL is UNKNOWN; WHERE retains only TRUE.
      result_v := false;
    else
      case opcode_i is
        when OP_EQ =>
          result_v := equal_v;
        when OP_NE =>
          result_v := not equal_v;
        when OP_LT =>
          result_v := less_v;
        when OP_LE =>
          result_v := less_v or equal_v;
        when OP_GT =>
          result_v := greater_v;
        when OP_GE =>
          result_v := greater_v or equal_v;
        when others =>
          result_v := false;
      end case;
    end if;

    if result_v then
      predicate_o <= '1';
    else
      predicate_o <= '0';
    end if;
  end process;
end architecture;
