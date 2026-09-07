BUILD_DIR ?= build

.PHONY: compiler simulation application web-assets web serve dev-frontend check
compiler:
	mkdir -p "$(BUILD_DIR)"
	cd compiler && go build -o "$(abspath $(BUILD_DIR))/servicec" ./cmd/servicec

simulation: compiler
	bash scripts/run-simulation.sh "$(BUILD_DIR)"

application: compiler
	bash scripts/run-simulation.sh "$(BUILD_DIR)" application

web-assets:
	pnpm --dir web install --frozen-lockfile
	cd compiler && go generate ./internal/webui/generate.go

web: web-assets
	mkdir -p "$(BUILD_DIR)"
	cd compiler && go build -o "$(abspath $(BUILD_DIR))/serviceweb" ./cmd/serviceweb

serve: web
	"$(BUILD_DIR)/serviceweb"

dev-frontend:
	pnpm --dir web run dev

# Local CI for this host-only lab; does not build or probe firmware.
check: simulation application web
	pnpm --dir web run check
	command -v g++ >/dev/null
	test -z "$$(gofmt -l compiler)"
	cd compiler && go vet ./... && go test ./... -count=1
