# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Teaching material for a university lab (RDSV/SDNV, UPM) on YANG model-driven network management with NETCONF and gNMI. It is not a software project: there is no build, lint or test suite. It holds the lab statement (in Spanish) plus the scripts, topologies and templates students use. Students write the answers themselves, so several files are deliberately incomplete (see "Intentional gaps" below).

- `docs/enunciado.md`: the lab statement. This is the main document, and most commits edit it. It holds the TOC, numbered sections and "Pregunta N" questions that refer to files under `activities/`.
- `activities/module-N/`: resources for each module. Module 1 covers NETCONF/gNMI capabilities and GET with SR Linux. Module 2 covers gNMI SET config and topology. Module 3 covers model-driven telemetry with gNMIc, Kafka and Prometheus.

Write all user-facing text (docs, script messages, YAML comments) in Spanish, to match the existing content.

## Commands

Export the statement to Word. This needs pandoc and must be run from `docs/`; `*.docx` is gitignored:
```bash
cd docs && ./make-docx   # -> 'p1.4 enunciado.docx'
```

Lab runtime. These need the lab VM: containerlab, Docker, sudo, and for module 2 also OVS. They also need xfce4-terminal/wmctrl for the consoles, and Wireshark for captures:
```bash
cd activities/module-1 && ./deploy-srlinux-testbed.sh    # r1, r2 + pc1, pc2
cd activities/module-1 && ./destroy-srlinux-testbed.sh
cd activities/module-2 && ./deploy-routing-testbed.sh    # r1-r3, OVS bridges s1-s3, pc11..pc32
cd activities/module-2 && ./destroy-routing-testbed.sh
cd activities/module-3 && docker compose -f docker-compose.yaml up -d   # gnmic, kafka, zookeeper, consul, prometheus
./clab-consoles.sh open|close [container]
./clab-capture-traffic.sh <container> <iface>
python get-capabilities-srlinux.py clab-srlinux-testbed-r1   # same CLI for the other module-1 .py scripts
```

## Things that span several files

- **Deploy scripts fetch from GitHub, not from local files.** `deploy-*.sh` downloads `r*.cfg` and the topology YAML from `raw.githubusercontent.com/educaredes/yang-lab/refs/heads/main/...` into `/tmp/.clab/`. Local edits to router configs or topologies have no effect until they are pushed to `main`. `destroy-*.sh` uses the local topology file instead.
- **Container names are hardcoded** as `clab-<lab-name>-<node>` in several places: `clab-consoles.sh`, `clab-capture-traffic.sh`, and the `docker exec` lines in the deploy scripts. If you rename a node or lab in a topology YAML, update all of them. The same applies to host IPs and routes, which are set in the deploy scripts rather than in the topology.
- **Shared device credentials and ports**: SR Linux `admin` / `NokiaSrl1!`, NETCONF on 830, gNMI on 57400. They appear in the Python scripts, the gNMIc templates, `gnmic-get-routing-config.sh` and the statement.
- **Module 3 joins the containerlab management network**: `docker-compose.yaml` uses the external Docker network `clab`, so a containerlab topology must already be deployed. The compose file mounts `gnmic-subscription-kafka-prometheus.yaml`, which students create (it is not in the repo). Prometheus discovers gnmic through Consul (`prometheus/prometheus.yaml`).
- **The statement names specific YANG revisions** (for example `srl_nokia-interfaces@2026-07-31.yang`, `ietf-yang-library@2019-01-04.yang`), which come from `ghcr.io/nokia/srlinux:latest`. If the image changes, check these filenames in `enunciado.md`. `yang-models-srlinux/` (created by `download-yang-modules-schemas-srlinux.py`) is gitignored.
- `activities/module-2/topology-driver-1.0.jar` is a prebuilt binary (Java 11, OpenDaylight YANG Tools, RFC 8345). It reads `/tmp/.clab/clab-routing-testbed/topology-data.json`. Its source is not in this repo.

## Intentional gaps (do not "fix")

- `module-3/gnmic-subscription.yaml` has `"..."` paths and a `<container_name>` placeholder for students to fill in. Its content is also copied verbatim in `enunciado.md`, so keep the two in sync.
- `module-2/configure_ip_*.yaml` are gNMIc templated set-request files with `{{.Vars.*}}` placeholders. They are filled through `--request-vars`. The base `r*.cfg` in module 2 deliberately leaves inter-router addressing and routing unconfigured.

## Known quirks

- `module-2/clab-capture-traffic.sh` was copied from module 1 and still matches `clab-srlinux-testbed-*` patterns. As a result, interface validation never runs for routing-testbed containers.
- `clab-consoles.sh` opens `sr_cli` only for names containing `isp`, so SR Linux routers currently get `/bin/bash`.
- `.vscode/settings.json` holds the cSpell word list for the Spanish/technical vocabulary. Add new proper nouns there.
