"""Step 0: strip the stock Corne Cherry v3 board down to outline, switches, controller and holes.

Removes every track and via, and the diode, LED, OLED and TRRS footprints.
Usage: python3 strip.py corne-cherry.kicad_pcb orig/stripped.kicad_pcb
"""
import re
import sys

import sx


def drop(s):
    if re.match(r'\((segment|via|arc)\b', s):
        return True
    if s.startswith('(footprint'):
        m = re.search(r'\(fp_text reference "([^"]*)"', s)
        return bool(m and re.match(r'^(D\d+|LED\d+|J\d+)$', m.group(1)))
    return False


if __name__ == '__main__':
    print('removed', sx.filter_top(sys.argv[1], sys.argv[2], drop), 'items')
