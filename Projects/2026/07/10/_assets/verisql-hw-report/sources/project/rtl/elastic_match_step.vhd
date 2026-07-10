library ieee;
use ieee.std_logic_1164.all;

-- Pure next-state function for the accelerator's one-entry elastic output
-- register. Isolating this logic permits an unclocked, non-vacuous formal proof
-- of the exact state transition used by sql_predicate_accel.
entity elastic_match_step is
  port (
    current_valid_i : in  std_logic;
    current_match_i : in  std_logic;
    rst_i           : in  std_logic;
    in_valid_i      : in  std_logic;
    in_match_i      : in  std_logic;
    out_ready_i     : in  std_logic;

    in_ready_o  : out std_logic;
    next_valid_o : out std_logic;
    next_match_o : out std_logic
  );
end entity;

architecture rtl of elastic_match_step is
begin
  transition : process(all)
    variable ready_v : std_logic;
  begin
    ready_v := (not current_valid_i) or out_ready_i;
    in_ready_o <= ready_v;

    next_valid_o <= current_valid_i;
    next_match_o <= current_match_i;

    if rst_i = '1' then
      next_valid_o <= '0';
      next_match_o <= '0';
    elsif ready_v = '1' then
      next_valid_o <= in_valid_i;
      if in_valid_i = '1' then
        next_match_o <= in_match_i;
      end if;
    end if;
  end process;
end architecture;
