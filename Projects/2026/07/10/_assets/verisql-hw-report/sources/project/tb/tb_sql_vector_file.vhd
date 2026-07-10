library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_textio.all;

library std;
use std.env.all;
use std.textio.all;

use work.sql_pkg.all;

-- Cross-language packing test. Python generates packed hexadecimal vectors
-- using verisql.accelerator.pack_row/pack_config; this testbench applies those
-- exact buses to the synthesized datapath-facing VHDL interface.
entity tb_sql_vector_file is
  generic (
    VECTOR_FILE : string := "build/vhdl_vectors.txt"
  );
end entity tb_sql_vector_file;

architecture test of tb_sql_vector_file is
  signal cfg_enable_s : std_logic_vector(PREDICATE_COUNT - 1 downto 0);
  signal cfg_column_s : std_logic_vector(PREDICATE_COUNT * 2 - 1 downto 0);
  signal cfg_opcode_s : std_logic_vector(PREDICATE_COUNT * 3 - 1 downto 0);
  signal cfg_rhs_s    : std_logic_vector(PREDICATE_COUNT * DATA_WIDTH - 1 downto 0);
  signal in_row_s     : std_logic_vector(COLUMN_COUNT * DATA_WIDTH - 1 downto 0);
  signal in_null_s    : std_logic_vector(COLUMN_COUNT - 1 downto 0);
  signal match_s      : std_logic;

  file vectors_f : text open read_mode is VECTOR_FILE;
begin
  dut : entity work.sql_predicate_datapath(rtl)
    port map (
      cfg_enable_i => cfg_enable_s,
      cfg_column_i => cfg_column_s,
      cfg_opcode_i => cfg_opcode_s,
      cfg_rhs_i    => cfg_rhs_s,
      in_row_i     => in_row_s,
      in_null_i    => in_null_s,
      match_o      => match_s
    );

  stimulus : process is
    variable line_v        : line;
    variable enable_v      : std_logic_vector(PREDICATE_COUNT - 1 downto 0);
    variable column_v      : std_logic_vector(PREDICATE_COUNT * 2 - 1 downto 0);
    variable opcode_v      : std_logic_vector(PREDICATE_COUNT * 3 - 1 downto 0);
    variable rhs_v         : std_logic_vector(PREDICATE_COUNT * DATA_WIDTH - 1 downto 0);
    variable row_v         : std_logic_vector(COLUMN_COUNT * DATA_WIDTH - 1 downto 0);
    variable null_v        : std_logic_vector(COLUMN_COUNT - 1 downto 0);
    variable expected_v    : std_logic;
    variable vector_count_v : natural := 0;
  begin
    while not endfile(vectors_f) loop
      readline(vectors_f, line_v);
      hread(line_v, enable_v);
      hread(line_v, column_v);
      hread(line_v, opcode_v);
      hread(line_v, rhs_v);
      hread(line_v, row_v);
      hread(line_v, null_v);
      read(line_v, expected_v);

      cfg_enable_s <= enable_v;
      cfg_column_s <= column_v;
      cfg_opcode_s <= opcode_v;
      cfg_rhs_s    <= rhs_v;
      in_row_s     <= row_v;
      in_null_s    <= null_v;
      wait for 1 ns;

      vector_count_v := vector_count_v + 1;
      assert match_s = expected_v
        report "packed vector mismatch at vector " & natural'image(vector_count_v)
        severity failure;
    end loop;

    assert vector_count_v > 0
      report "vector file was empty"
      severity failure;
    report "tb_sql_vector_file PASS: " & natural'image(vector_count_v) & " vectors"
      severity note;
    stop;
    wait;
  end process stimulus;
end architecture test;
