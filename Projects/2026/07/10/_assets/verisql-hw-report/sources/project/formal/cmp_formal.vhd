library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.sql_pkg.all;

-- All entity inputs are unconstrained primary inputs in the formal model.
entity cmp_formal is
  port (
    lhs_i     : in word32_t;
    rhs_i     : in word32_t;
    is_null_i : in std_logic;
    opcode_i  : in std_logic_vector(2 downto 0)
  );
end entity;

architecture formal of cmp_formal is
  signal dut_result_s : std_logic;
  signal ref_result_s : std_logic;
begin
  dut : entity work.sql_cmp32
    port map (
      lhs_i       => lhs_i,
      rhs_i       => rhs_i,
      is_null_i   => is_null_i,
      opcode_i    => opcode_i,
      predicate_o => dut_result_s
    );

  reference_model : process(all)
    variable result_v : boolean;
  begin
    result_v := false;
    if opcode_i = OP_IS_NULL then
      result_v := is_null_i = '1';
    elsif opcode_i = OP_IS_NOT_NULL then
      result_v := is_null_i = '0';
    elsif is_null_i = '1' then
      result_v := false;
    else
      case opcode_i is
        when OP_EQ => result_v := signed(lhs_i) = signed(rhs_i);
        when OP_NE => result_v := signed(lhs_i) /= signed(rhs_i);
        when OP_LT => result_v := signed(lhs_i) < signed(rhs_i);
        when OP_LE => result_v := signed(lhs_i) <= signed(rhs_i);
        when OP_GT => result_v := signed(lhs_i) > signed(rhs_i);
        when OP_GE => result_v := signed(lhs_i) >= signed(rhs_i);
        when others => result_v := false;
      end case;
    end if;

    if result_v then
      ref_result_s <= '1';
    else
      ref_result_s <= '0';
    end if;
  end process;

  equivalence : assert dut_result_s = ref_result_s
    report "sql_cmp32 differs from signed SQL reference"
    severity failure;
end architecture;
