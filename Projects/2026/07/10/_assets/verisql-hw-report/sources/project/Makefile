PYTHON ?= python3
GHDL ?= ghdl
SBY ?= sby
BUILD_DIR ?= build
GHDL_WORK := $(BUILD_DIR)/ghdl

.PHONY: install check lint test prove vhdl-parse demo vhdl-test vhdl-synth formal-rtl clean

install:
	$(PYTHON) -m pip install -e '.[dev,formal]'

check: lint test prove vhdl-parse

lint:
	ruff check verisql tests formal tools
	ruff format --check verisql tests formal tools

test:
	PYTHONPATH=. $(PYTHON) -m pytest -q

prove:
	PYTHONPATH=. $(PYTHON) formal/prove.py

vhdl-parse:
	@command -v vsg >/dev/null || { echo "vsg is required (install .[dev])"; exit 1; }
	vsg -c .vsg-parse.yaml -f rtl/*.vhd tb/*.vhd formal/*.vhd -of summary

demo:
	rm -rf $(BUILD_DIR)/demo.db
	mkdir -p $(BUILD_DIR)
	PYTHONPATH=. $(PYTHON) -m verisql --db $(BUILD_DIR)/demo.db --file demo.sql

vhdl-test:
	@command -v $(GHDL) >/dev/null || { echo "ghdl is required"; exit 1; }
	mkdir -p $(GHDL_WORK)
	PYTHONPATH=. $(PYTHON) tools/generate_vhdl_vectors.py $(BUILD_DIR)/vhdl_vectors.txt --count 1000
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_pkg.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_cmp32.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/elastic_match_step.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_predicate_datapath.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_predicate_accel.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) tb/tb_sql_cmp32.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) tb/tb_sql_predicate_accel.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) tb/tb_sql_vector_file.vhd
	$(GHDL) -e --std=08 --workdir=$(GHDL_WORK) tb_sql_cmp32
	$(GHDL) -r --std=08 --workdir=$(GHDL_WORK) tb_sql_cmp32 --assert-level=error
	$(GHDL) -e --std=08 --workdir=$(GHDL_WORK) tb_sql_predicate_accel
	$(GHDL) -r --std=08 --workdir=$(GHDL_WORK) tb_sql_predicate_accel --assert-level=error
	$(GHDL) -e --std=08 --workdir=$(GHDL_WORK) tb_sql_vector_file
	$(GHDL) -r --std=08 --workdir=$(GHDL_WORK) tb_sql_vector_file -gVECTOR_FILE=$(abspath $(BUILD_DIR)/vhdl_vectors.txt) --assert-level=error

vhdl-synth:
	@command -v $(GHDL) >/dev/null || { echo "ghdl is required"; exit 1; }
	mkdir -p $(GHDL_WORK)
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_pkg.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_cmp32.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/elastic_match_step.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_predicate_datapath.vhd
	$(GHDL) -a --std=08 --workdir=$(GHDL_WORK) rtl/sql_predicate_accel.vhd
	$(GHDL) --synth --std=08 --workdir=$(GHDL_WORK) --out=none sql_predicate_accel

formal-rtl:
	@command -v $(SBY) >/dev/null || { echo "SymbiYosys (sby) is required"; exit 1; }
	cd formal && $(SBY) -f cmp_formal.sby
	cd formal && $(SBY) -f datapath_formal.sby
	cd formal && $(SBY) -f stream_formal.sby

clean:
	rm -rf $(BUILD_DIR) dist .pytest_cache verisql_hw.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
