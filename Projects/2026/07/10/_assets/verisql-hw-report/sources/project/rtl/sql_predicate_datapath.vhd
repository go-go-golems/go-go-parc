library ieee;
use ieee.std_logic_1164.all;

use work.sql_pkg.all;

-- Pure combinational predicate datapath.  The streaming top level instantiates
-- this block unchanged, which lets the packed lane/slot semantics be proved
-- directly against the synthesized VHDL.
entity sql_predicate_datapath is
  port (
    cfg_enable_i : in  std_logic_vector(PREDICATE_COUNT - 1 downto 0);
    cfg_column_i : in  std_logic_vector(PREDICATE_COUNT * 2 - 1 downto 0);
    cfg_opcode_i : in  std_logic_vector(PREDICATE_COUNT * 3 - 1 downto 0);
    cfg_rhs_i    : in  std_logic_vector(PREDICATE_COUNT * DATA_WIDTH - 1 downto 0);

    in_row_i  : in  std_logic_vector(COLUMN_COUNT * DATA_WIDTH - 1 downto 0);
    in_null_i : in  std_logic_vector(COLUMN_COUNT - 1 downto 0);

    match_o : out std_logic
  );
end entity sql_predicate_datapath;

architecture rtl of sql_predicate_datapath is
  signal selected_value_s : word32_array_t(0 to PREDICATE_COUNT - 1);
  signal selected_null_s  : std_logic_vector(PREDICATE_COUNT - 1 downto 0);
  signal compare_s        : std_logic_vector(PREDICATE_COUNT - 1 downto 0);
  signal predicate_pass_s : std_logic_vector(PREDICATE_COUNT - 1 downto 0);
begin
  predicate_slots : for p in 0 to PREDICATE_COUNT - 1 generate
    select_column : process(all) is
    begin
      selected_value_s(p) <= (others => '0');
      selected_null_s(p)  <= '1';
      case cfg_column_i((p + 1) * 2 - 1 downto p * 2) is
        when "00" =>
          selected_value_s(p) <= in_row_i(DATA_WIDTH - 1 downto 0);
          selected_null_s(p)  <= in_null_i(0);
        when "01" =>
          selected_value_s(p) <= in_row_i(2 * DATA_WIDTH - 1 downto DATA_WIDTH);
          selected_null_s(p)  <= in_null_i(1);
        when "10" =>
          selected_value_s(p) <= in_row_i(3 * DATA_WIDTH - 1 downto 2 * DATA_WIDTH);
          selected_null_s(p)  <= in_null_i(2);
        when "11" =>
          selected_value_s(p) <= in_row_i(4 * DATA_WIDTH - 1 downto 3 * DATA_WIDTH);
          selected_null_s(p)  <= in_null_i(3);
        when others =>
          selected_value_s(p) <= (others => '0');
          selected_null_s(p)  <= '1';
      end case;
    end process select_column;

    comparator : entity work.sql_cmp32(rtl)
      port map (
        lhs_i       => selected_value_s(p),
        rhs_i       => cfg_rhs_i((p + 1) * DATA_WIDTH - 1 downto p * DATA_WIDTH),
        is_null_i   => selected_null_s(p),
        opcode_i    => cfg_opcode_i((p + 1) * 3 - 1 downto p * 3),
        predicate_o => compare_s(p)
      );

    predicate_pass_s(p) <= (not cfg_enable_i(p)) or compare_s(p);
  end generate predicate_slots;

  match_o <= predicate_pass_s(0) and predicate_pass_s(1)
             and predicate_pass_s(2) and predicate_pass_s(3);
end architecture rtl;
