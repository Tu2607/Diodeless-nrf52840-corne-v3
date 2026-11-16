# Diodeless wireless Corne pin map

Each switch connects one nice!nano v2 GPIO to ground. The controller mounts face down, as on the stock Corne v3.
Key names: R = row (0 top), C = column (0 = outer pinky column on each half), T = thumb (0 = outermost thumb key).

The three inner pads P1.01, P1.02 and P1.07 need pins (or socket pins) between the nice!nano and the J1/J2 holes.

## Left half

| Key | Switch | Pro Micro pin (ZMK) | nRF52840 GPIO |
|---|---|---|---|
| R0C0 | SW1 | &pro_micro 21 | P0.31 |
| R0C1 | SW2 | &pro_micro 20 | P0.29 |
| R0C2 | SW3 | &pro_micro 1 | P0.06 |
| R0C3 | SW4 | &pro_micro 2 | P0.17 |
| R0C4 | SW5 | &pro_micro 0 | P0.08 |
| R0C5 | SW6 | &pro_micro 3 | P0.20 |
| R1C0 | SW7 | &pro_micro 15 | P1.13 |
| R1C1 | SW8 | &pro_micro 6 | P1.00 |
| R1C2 | SW9 | &pro_micro 19 | P0.02 |
| R1C3 | SW10 | &pro_micro 5 | P0.24 |
| R1C4 | SW11 | &pro_micro 4 | P0.22 |
| R1C5 | SW12 | &pro_micro 18 | P1.15 |
| R2C0 | SW13 | &pro_micro 10 | P0.09 |
| R2C1 | SW14 | &pro_micro 16 | P0.10 |
| R2C2 | SW15 | &pro_micro 9 | P1.06 |
| R2C3 | SW16 | inner pad | P1.07 |
| R2C4 | SW17 | inner pad | P1.02 |
| R2C5 | SW18 | &pro_micro 14 | P1.11 |
| T0 | SW19 | &pro_micro 8 | P1.04 |
| T1 | SW20 | inner pad | P1.01 |
| T2 | SW21 | &pro_micro 7 | P0.11 |

ZMK direct key scan (`input-gpios` in key order R0C0..R2C5, T0..T2):

```dts
kscan0: kscan {
    compatible = "zmk,kscan-gpio-direct";
    wakeup-source;
    input-gpios
        = <&pro_micro 21 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C0 P0.31 */
        , <&pro_micro 20 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C1 P0.29 */
        , <&pro_micro 1 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C2 P0.06 */
        , <&pro_micro 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C3 P0.17 */
        , <&pro_micro 0 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C4 P0.08 */
        , <&pro_micro 3 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C5 P0.20 */
        , <&pro_micro 15 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C0 P1.13 */
        , <&pro_micro 6 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C1 P1.00 */
        , <&pro_micro 19 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C2 P0.02 */
        , <&pro_micro 5 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C3 P0.24 */
        , <&pro_micro 4 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C4 P0.22 */
        , <&pro_micro 18 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C5 P1.15 */
        , <&pro_micro 10 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C0 P0.09 */
        , <&pro_micro 16 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C1 P0.10 */
        , <&pro_micro 9 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C2 P1.06 */
        , <&gpio1 7 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C3 P1.07 inner pad */
        , <&gpio1 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C4 P1.02 inner pad */
        , <&pro_micro 14 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C5 P1.11 */
        , <&pro_micro 8 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* T0 P1.04 */
        , <&gpio1 1 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* T1 P1.01 inner pad */
        , <&pro_micro 7 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* T2 P0.11 */
        ;
};
```

## Right half

| Key | Switch | Pro Micro pin (ZMK) | nRF52840 GPIO |
|---|---|---|---|
| R0C0 | SW22 | &pro_micro 2 | P0.17 |
| R0C1 | SW23 | &pro_micro 3 | P0.20 |
| R0C2 | SW24 | &pro_micro 0 | P0.08 |
| R0C3 | SW25 | &pro_micro 1 | P0.06 |
| R0C4 | SW26 | &pro_micro 20 | P0.29 |
| R0C5 | SW27 | &pro_micro 21 | P0.31 |
| R1C0 | SW28 | &pro_micro 8 | P1.04 |
| R1C1 | SW29 | inner pad | P1.07 |
| R1C2 | SW30 | &pro_micro 15 | P1.13 |
| R1C3 | SW31 | &pro_micro 5 | P0.24 |
| R1C4 | SW32 | &pro_micro 6 | P1.00 |
| R1C5 | SW33 | inner pad | P1.02 |
| R2C0 | SW34 | &pro_micro 9 | P1.06 |
| R2C1 | SW35 | inner pad | P1.01 |
| R2C2 | SW36 | &pro_micro 10 | P0.09 |
| R2C3 | SW37 | &pro_micro 16 | P0.10 |
| R2C4 | SW38 | &pro_micro 14 | P1.11 |
| R2C5 | SW39 | &pro_micro 7 | P0.11 |
| T0 | SW40 | &pro_micro 4 | P0.22 |
| T1 | SW41 | &pro_micro 18 | P1.15 |
| T2 | SW42 | &pro_micro 19 | P0.02 |

ZMK direct key scan (`input-gpios` in key order R0C0..R2C5, T0..T2):

```dts
kscan0: kscan {
    compatible = "zmk,kscan-gpio-direct";
    wakeup-source;
    input-gpios
        = <&pro_micro 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C0 P0.17 */
        , <&pro_micro 3 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C1 P0.20 */
        , <&pro_micro 0 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C2 P0.08 */
        , <&pro_micro 1 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C3 P0.06 */
        , <&pro_micro 20 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C4 P0.29 */
        , <&pro_micro 21 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R0C5 P0.31 */
        , <&pro_micro 8 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C0 P1.04 */
        , <&gpio1 7 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C1 P1.07 inner pad */
        , <&pro_micro 15 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C2 P1.13 */
        , <&pro_micro 5 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C3 P0.24 */
        , <&pro_micro 6 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C4 P1.00 */
        , <&gpio1 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R1C5 P1.02 inner pad */
        , <&pro_micro 9 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C0 P1.06 */
        , <&gpio1 1 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C1 P1.01 inner pad */
        , <&pro_micro 10 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C2 P0.09 */
        , <&pro_micro 16 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C3 P0.10 */
        , <&pro_micro 14 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C4 P1.11 */
        , <&pro_micro 7 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* R2C5 P0.11 */
        , <&pro_micro 4 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* T0 P0.22 */
        , <&pro_micro 18 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* T1 P1.15 */
        , <&pro_micro 19 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* T2 P0.02 */
        ;
};
```

## Switch sockets

Every key takes either a Kailh MX hotswap socket or a Kailh Choc v1 hotswap socket, both on the back. Fit one type per key.
The Choc socket sits on the opposite side of the switch centre from the MX socket. Left-half switches are turned 180 degrees relative to v3 (except SW20) so the Choc socket stays clear of the board edge.

## Power

- Battery + goes from the BAT connector (pin marked +) through the PWR toggle (C&K GT11MSCBE) to the nice!nano B+ (RAW) pin.
- Battery - goes to ground.
- With the switch off the battery is disconnected, so it will not charge over USB.
- Check your battery lead polarity against the + and - silkscreen before plugging in. JST-PH battery polarity is not standardised.
