library ieee;
use ieee.std_logic_1164.all;

-- All inputs are symbolic primary inputs. Equivalence to the reference
-- equations proves every possible one-step state/input combination.
entity stream_step_formal is
  port (
    current_valid_i : in std_logic;
    current_match_i : in std_logic;
    rst_i           : in std_logic;
    in_valid_i      : in std_logic;
    in_match_i      : in std_logic;
    out_ready_i     : in std_logic
  );
end entity;

architecture formal of stream_step_formal is
  signal dut_ready_s     : std_logic;
  signal dut_next_valid_s : std_logic;
  signal dut_next_match_s : std_logic;
  signal ref_ready_s      : std_logic;
  signal ref_next_valid_s : std_logic;
  signal ref_next_match_s : std_logic;
begin
  dut : entity work.elastic_match_step
    port map (
      current_valid_i => current_valid_i,
      current_match_i => current_match_i,
      rst_i           => rst_i,
      in_valid_i      => in_valid_i,
      in_match_i      => in_match_i,
      out_ready_i     => out_ready_i,
      in_ready_o      => dut_ready_s,
      next_valid_o    => dut_next_valid_s,
      next_match_o    => dut_next_match_s
    );

  reference_model : process(all)
    variable ready_v : std_logic;
  begin
    ready_v := (not current_valid_i) or out_ready_i;
    ref_ready_s <= ready_v;
    ref_next_valid_s <= current_valid_i;
    ref_next_match_s <= current_match_i;

    if rst_i = '1' then
      ref_next_valid_s <= '0';
      ref_next_match_s <= '0';
    elsif ready_v = '1' then
      ref_next_valid_s <= in_valid_i;
      if in_valid_i = '1' then
        ref_next_match_s <= in_match_i;
      end if;
    end if;
  end process;

  ready_equivalence : assert dut_ready_s = ref_ready_s
    report "elastic_match_step ready equation mismatch" severity failure;
  valid_equivalence : assert dut_next_valid_s = ref_next_valid_s
    report "elastic_match_step next-valid mismatch" severity failure;
  match_equivalence : assert dut_next_match_s = ref_next_match_s
    report "elastic_match_step next-match mismatch" severity failure;
end architecture;
