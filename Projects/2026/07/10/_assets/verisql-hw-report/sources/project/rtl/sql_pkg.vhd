library ieee;
use ieee.std_logic_1164.all;

package sql_pkg is
  constant DATA_WIDTH      : positive := 32;
  constant COLUMN_COUNT    : positive := 4;
  constant PREDICATE_COUNT : positive := 4;

  subtype word32_t is std_logic_vector(DATA_WIDTH - 1 downto 0);
  type word32_array_t is array (natural range <>) of word32_t;

  -- Three-bit operation encoding shared with verisql/accelerator.py.
  constant OP_EQ          : std_logic_vector(2 downto 0) := "000";
  constant OP_NE          : std_logic_vector(2 downto 0) := "001";
  constant OP_LT          : std_logic_vector(2 downto 0) := "010";
  constant OP_LE          : std_logic_vector(2 downto 0) := "011";
  constant OP_GT          : std_logic_vector(2 downto 0) := "100";
  constant OP_GE          : std_logic_vector(2 downto 0) := "101";
  constant OP_IS_NULL     : std_logic_vector(2 downto 0) := "110";
  constant OP_IS_NOT_NULL : std_logic_vector(2 downto 0) := "111";
end package;
