# Test Harness Makefile
# Convenience targets for running the harness and the experimental matrix.

.PHONY: help build up down baseline ips pam segmentation all matrix clean logs

PROFILES := baseline ips pam segmentation all
SCENARIOS := \
	01-spoofing-arp-poisoning.py \
	02-tampering-firmware-injection.py \
	03-info-disclosure-cleartext-hl7.py \
	04-dos-protocol-flood.py \
	05-eop-default-credential.py

help:
	@echo "Test Harness — common targets"
	@echo ""
	@echo "  make build           # Build all images"
	@echo "  make up              # Bring up baseline (no controls)"
	@echo "  make down            # Tear down all containers"
	@echo "  make ips             # Bring up with IPS profile"
	@echo "  make pam             # Bring up with PAM profile"
	@echo "  make segmentation    # Bring up with segmentation profile"
	@echo "  make all             # Bring up with all controls"
	@echo "  make matrix          # Run all scenarios across all control profiles"
	@echo "  make logs            # Tail all container logs"
	@echo "  make clean           # Remove built images and results"

build:
	docker compose build
	docker compose --profile ips --profile pam --profile segmentation build

up: build
	docker compose up -d
	@echo "Waiting for healthchecks..."
	@sleep 8

down:
	-docker compose --profile ips --profile pam --profile segmentation --profile all down -v

ips:
	$(MAKE) down
	docker compose --profile ips up -d
	@sleep 8

pam:
	$(MAKE) down
	docker compose --profile pam up -d
	@sleep 8

segmentation:
	$(MAKE) down
	docker compose --profile segmentation up -d
	@sleep 8
	@echo "Note: for true segmentation, run: docker network disconnect harness-pump-net harness-attacker"

all:
	$(MAKE) down
	docker compose --profile all up -d
	@sleep 10
	@echo "Note: for true segmentation, run: docker network disconnect harness-pump-net harness-attacker"

# Single scenario, single profile
# Usage: make scenario S=05-eop-default-credential.py P=pam
scenario:
	docker compose exec -T attacker python runner.py $(S) --control-profile $(P)

# Run all scenarios against the currently-up profile
run-all:
	docker compose exec -T attacker python runner.py --all --control-profile $${PROFILE:-baseline}

# Run the full matrix: every scenario against every profile.
# Results aggregated into results/matrix-<timestamp>.csv.
matrix:
	@mkdir -p results
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	echo "Matrix run $${RUN_ID}"; \
	echo "timestamp,scenario,stride_hc,control_profile,outcome,detail" > results/matrix-$${RUN_ID}.csv; \
	for profile in $(PROFILES); do \
		echo ""; \
		echo "═══════════════════════════════════════════════════════════"; \
		echo "Profile: $${profile}"; \
		echo "═══════════════════════════════════════════════════════════"; \
		$(MAKE) -s down >/dev/null 2>&1; \
		if [ "$${profile}" = "baseline" ]; then \
			docker compose up -d >/dev/null 2>&1; \
		else \
			docker compose --profile $${profile} up -d >/dev/null 2>&1; \
		fi; \
		sleep 10; \
		docker compose exec -T attacker python runner.py --all --control-profile $${profile} || true; \
		docker compose exec -T attacker sh -c "cat /results/run-*.csv 2>/dev/null | grep -v '^timestamp' || true" >> results/matrix-$${RUN_ID}.csv; \
		docker compose exec -T attacker sh -c "rm -f /results/run-*.csv" 2>/dev/null || true; \
	done; \
	$(MAKE) -s down >/dev/null 2>&1; \
	echo ""; \
	echo "Matrix complete. Results: results/matrix-$${RUN_ID}.csv"; \
	echo ""; \
	cat results/matrix-$${RUN_ID}.csv

logs:
	docker compose logs -f --tail=50

clean: down
	-docker compose --profile ips --profile pam --profile segmentation --profile all rm -fsv 2>/dev/null
	-docker rmi -f $$(docker images -q 'harness-*') 2>/dev/null
	rm -rf results/run-* results/matrix-*
	@echo "Cleaned."
