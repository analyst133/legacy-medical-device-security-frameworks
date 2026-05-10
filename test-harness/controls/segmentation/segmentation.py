#!/usr/bin/env python3
"""
Network segmentation control — sentinel.

In Docker, full network segmentation is most cleanly modelled by placing the
attacker on a different Docker network without a route to the protected target.
Toggling that requires structural changes to docker-compose.yml that are not
expressible as a runtime config — so this container is a sentinel that signals
"segmentation profile active" to the runner. The actual segmentation should be
applied by the operator via:

  docker network disconnect harness-pump-net harness-attacker

Or by using the alternate docker-compose-segmented.yml file (planned in
ROADMAP.md) that places the attacker on a separate network.

The runner detects this control's presence and labels the run accordingly.
"""

import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [seg] %(message)s")
log = logging.getLogger("seg")

log.info("Segmentation profile active — operator must enforce network isolation manually")
log.info("See controls/segmentation/README in the future for full segmentation workflow")

while True:
    log.info("heartbeat — segmentation profile active")
    time.sleep(30)
