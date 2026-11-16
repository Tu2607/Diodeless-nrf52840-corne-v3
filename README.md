# Diodeless nRF52840 Corne v3

A diodeless (direct-pin), Bluetooth variant of the [Corne Cherry v3.0.1](https://github.com/foostan/crkbd/tree/v3-final) by foostan.

![Top layout](images/layout-top.png)

**Status: revision 0.4. Routed and DRC clean for connectivity and clearance, but not yet fabricated or tested. Check the open items below before ordering boards.**

## What it is

- 3x6+3 keys per half, with the same outline, key positions and mounting holes as Corne v3
- nice!nano v2 (nRF52840) running ZMK, mounted face down like the stock Corne controller
- One GPIO per switch and no diodes. All 21 GPIOs per half are used, including the three inner pads P1.01, P1.02 and P1.07
- Every key takes either a Kailh MX hotswap socket or a Kailh Choc v1 hotswap socket
- OLED, RGB LEDs and the TRRS jack are removed
- C&K GT11MSCBE sealed surface-mount toggle as the power switch, where the TRRS jack was
- Two wire pads marked TOGGLE, in parallel with the power switch, for an off-board switch instead
- JST-PH 2-pin battery connector below the controller
- Reset button kept

## Files

| Path | Contents |
|---|---|
| `pcb/` | KiCad 7 board, project file and the local footprint library |
| `gerbers/` | Gerber and drill files, plus a zip of the same |
| `PINMAP.md` | Key to pin table and a ZMK direct key scan snippet for each half |
| `images/` | Renders of the top, bottom, power switch area and socket pads |
| `scripts/` | The scripts that generated the board from the stock v3 board |

There is no schematic yet. Nets were assigned directly on the board by `scripts/stage1.py`.

## Open items before ordering

- The GT11MSCBE pad layout comes from two community footprints that agree with each other, not from the datasheet land pattern. Check a real switch against a 1:1 print.
- The GT11MSCBE is rated 0.4 VA at up to 20 V, which is about 95 mA at battery voltage. The nice!nano charges at about 100 mA through the switch, so it is at its limit while charging.
- The position of the three inner nice!nano pads comes from community footprints. Check it against a real board.
- JST-PH battery polarity is not standardised. Check your battery lead against the + and - silkscreen.
- Corne v3 plates and cases are cut for MX. A Choc build needs a Choc plate or no plate.
- With the power switch off, the battery is disconnected and will not charge over USB.

## Switch sockets

The Choc socket sits on the opposite side of the switch centre from the MX socket. Fit one type per key. Left-half switches are turned 180 degrees relative to v3 (except SW20) so the Choc socket stays clear of the board edge.

![Socket pads](images/socket-pads-detail.png)

## Power switch

![Power switch area](images/power-switch-area.png)

## Regenerating the board

The board is generated, not hand drawn. The scripts need KiCad 7 with its Python API, plus shapely, scipy and matplotlib. They currently use fixed paths under `/home/user/work`, so adjust those first.

1. `scripts/strip.py` removes tracks, diodes, LEDs, OLED and TRRS from the stock v3 board
2. `scripts/stage1.py` adds the Choc pads, power switch, battery connector and extra pins, and assigns nets
3. `scripts/router.py` routes both halves with a small grid router
4. `scripts/stage3.py` adds the ground pours and labels
5. `scripts/drc.py` and `scripts/export.sh` check the board and export gerbers and renders

`scripts/build.sh` runs steps 2 to 5.

## Licence and credit

Based on the Corne keyboard by foostan, used under the MIT licence. See `LICENSE`.
