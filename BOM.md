# Bill of materials

Quantities are for one full keyboard, both halves. This is the standard build: MX switches, with the controller on low-profile sockets. Choc parts are listed as the alternative.

## Board and controller

| Item | Qty | Part | Notes |
|---|---|---|---|
| PCB | 1 | `gerbers/corne-diodeless-gerbers.zip` | Two layers, 1.6 mm. One order gives both halves |
| Controller | 2 | nice!nano v2 | nRF52840, runs ZMK |
| Controller socket, 12-pin low profile | 4 | Mill-Max 315-43-112-41-003000 | Two per controller. Solders to the keyboard PCB |
| Controller socket, single pin | 6 | One pin of the same Mill-Max 315 series | For the inner pads P1.01, P1.02 and P1.07. Cut from a spare strip if you cannot buy singles |
| Controller pins | 54 | Mill-Max 3320-0-00-15-00-00-03-0 | 27 per controller. Solder to the nice!nano and plug into the sockets |

## Keys, MX build

| Item | Qty | Part | Notes |
|---|---|---|---|
| Hotswap socket | 42 | Kailh CPG151101S11 | Gateron MX sockets also fit |
| Switch | 42 | Any MX-style switch | 3-pin or 5-pin |
| Keycap | 42 | 40 x 1u, 2 x 1.5u | MX stem |

## Keys, Choc build (alternative)

| Item | Qty | Part | Notes |
|---|---|---|---|
| Hotswap socket | 42 | Kailh CPG135001S30 | Choc v1 socket |
| Switch | 42 | Kailh Choc v1 (PG1350) | Choc v2 is not supported |
| Keycap | 42 | 40 x 1u, 2 x 1.5u | Choc stem |

You can mix the two per key, but each key takes one socket type.

## Power

| Item | Qty | Part | Notes |
|---|---|---|---|
| Power switch | 2 | C&K GT11MSCBE | Sealed SMD toggle, 0.4 VA |
| Battery connector | 2 | JST B2B-PH-K-S(LF)(SN) | 2-pin PH header, upright. Optional, you can solder the leads to the pads |
| Battery | 2 | 3.7 V LiPo with a JST-PH 2.0 mm plug | A 301230 cell (3 x 12 x 30 mm, about 110 mAh) is the usual size for under a nice!nano. Check the plug polarity against the + mark |
| Reset button | 2 | 2-pin tactile switch, as used on the Corne v3 | Usually sold as "Corne reset switch" |

## Case and hardware (optional)

The board keeps the Corne v3 outline and mounting holes, so Corne v3 cases and plates fit. For the standard sandwich case:

| Item | Qty | Part | Notes |
|---|---|---|---|
| Top plate | 2 | Corne v3 (Cherry) top plate | MX only. A Choc build needs a Choc plate or no plate |
| Bottom plate | 2 | Corne v3 bottom plate | |
| Spacer | 10 | M2, 7.5 mm | |
| Screw | 20 | M2, 4 mm | |
| Rubber feet | 8 | Small adhesive bumpers | |

## Not needed

Compared with a stock Corne v3, this board uses no diodes, no TRRS jacks or cable, no OLED modules or covers, and no LEDs.

## How these were checked

- The Mill-Max socket and pin numbers are the ones the Corne v3 build guide links for socketing a controller.
- The GT11MSCBE was checked against its C&K datasheet.
- The Kailh and JST part numbers were confirmed to exist at distributors.
- Not checked: the exact height of the Mill-Max sockets, the single-pin socket part number, and whether a 301230 battery clears the underside of a face-down nice!nano on these sockets. Test fit before committing to a battery size.
