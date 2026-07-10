library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.sql_pkg.all;

-- All ports are unconstrained primary inputs in the formal model.  The
-- reference process intentionally uses numeric_std signed comparisons rather
-- than the sign-bit lowering in sql_cmp32.
entity datapath_formal is
  port (
    cfg_enable_i : in std_logic_vector(PREDICATE_COUNT - 1 downto 0);
    cfg_column_i : in std_logic_vector(PREDICATE_COUNT * 2 - 1 downto 0);
    cfg_opcode_i : in std_logic_vector(PREDICATE_COUNT * 3 - 1 downto 0);
    cfg_rhs_i    : in std_logic_vector(PREDICATE_COUNT * DATA_WIDTH - 1 downto 0);
    in_row_i     : in std_logic_vector(COLUMN_COUNT * DATA_WIDTH - 1 downto 0);
    in_null_i    : in std_logic_vector(COLUMN_COUNT - 1 downto 0)
  );
end entity datapath_formal;

architecture formal of datapath_formal is
  signal dut_match_s : std_logic;
  signal ref_match_s : std_logic;
begin
  dut : entity work.sql_predicate_datapath(rtl)
    port map (
      cfg_enable_i => cfg_enable_i,
      cfg_column_i => cfg_column_i,
      cfg_opcode_i => cfg_opcode_i,
      cfg_rhs_i    => cfg_rhs_i,
      in_row_i     => in_row_i,
      in_null_i    => in_null_i,
      match_o      => dut_match_s
    );

  reference_model : process(all) is
    variable all_pass_v  : boolean;
    variable slot_pass_v : boolean;
    variable equal_v     : boolean;
    variable lhs_v       : word32_t;
    variable rhs_v       : word32_t;
    variable opcode_v    : std_logic_vector(2 downto 0);
    variable column_v    : natural range 0 to COLUMN_COUNT - 1;
    variable is_null_v   : boolean;
  begin
    all_pass_v := true;

    for p in 0 to PREDICATE_COUNT - 1 loop
      column_v := to_integer(unsigned(cfg_column_i((p + 1) * 2 - 1 downto p * 2)));
      lhs_v := in_row_i((column_v + 1) * DATA_WIDTH - 1 downto column_v * DATA_WIDTH);
      rhs_v := cfg_rhs_i((p + 1) * DATA_WIDTH - 1 downto p * DATA_WIDTH);
      opcode_v := cfg_opcode_i((p + 1) * 3 - 1 downto p * 3);
      is_null_v := in_null_i(column_v) = '1';
      equal_v := lhs_v = rhs_v;
      slot_pass_v := true;

      if cfg_enable_i(p) = '1' then
        if opcode_v = OP_IS_NULL then
          slot_pass_v := is_null_v;
        elsif opcode_v = OP_IS_NOT_NULL then
          slot_pass_v := not is_null_v;
        elsif is_null_v then
          slot_pass_v := false;
        else
          case opcode_v is
            when OP_EQ =>
              slot_pass_v := equal_v;
            when OP_NE =>
              slot_pass_v := not equal_v;
            when OP_LT =>
              slot_pass_v := signed(lhs_v) < signed(rhs_v);
            when OP_LE =>
              slot_pass_v := signed(lhs_v) <= signed(rhs_v);
            when OP_GT =>
              slot_pass_v := signed(lhs_v) > signed(rhs_v);
            when OP_GE =>
              slot_pass_v := signed(lhs_v) >= signed(rhs_v);
            when others =>
              slot_pass_v := false;
          end case;
        end if;
      end if;

      all_pass_v := all_pass_v and slot_pass_v;
    end loop;

    if all_pass_v then
      ref_match_s <= '1';
    else
      ref_match_s <= '0';
    end if;
  end process reference_model;

  equivalence : assert dut_match_s = ref_match_s
    report "sql_predicate_datapath differs from packed signed-SQL reference"
    severity failure;
end architecture formal;
