#!/bin/bash
# Full rebuild: place parts and nets, route, pour, check, export.
set -e
cd /home/user/work
python3.12 stage1.py > s1.log 2>&1
python3.12 chk.py stage1.kicad_pcb 2>/dev/null | tail -3
python3.12 router.py stage1.kicad_pcb stage2.kicad_pcb > route.log 2>&1
grep -E 'routed|vias|fail' route.log
python3.12 stage3.py > s3.log 2>&1
python3.12 drc.py proj/corne-diodeless.kicad_pcb drc.rpt > drc.log 2>&1
grep -E 'unconnected|violations' drc.rpt
grep -E '^\[' drc.rpt | sed -E 's/^\[([a-z_]+)\].*/\1/' | sort | uniq -c | tr '\n' ' '; echo
