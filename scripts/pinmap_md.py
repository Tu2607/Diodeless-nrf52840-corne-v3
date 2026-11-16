import json
pm=json.load(open('pinmap.json'))
order=['R%dC%d'%(r,c) for r in range(3) for c in range(6)]+['T0','T1','T2']
L=['# Diodeless wireless Corne pin map','',
'Each switch connects one nice!nano v2 GPIO to ground. The controller mounts face down, as on the stock Corne v3.',
'Key names: R = row (0 top), C = column (0 = outer pinky column on each half), T = thumb (0 = outermost thumb key).','',
'The three inner pads P1.01, P1.02 and P1.07 need pins (or socket pins) between the nice!nano and the J1/J2 holes.','']
for side in ('left','right'):
    L+=['## %s half'%side.capitalize(),'','| Key | Switch | Pro Micro pin (ZMK) | nRF52840 GPIO |','|---|---|---|---|']
    for k in order:
        e=pm[side][k]
        L.append('| %s | %s | %s | %s |'%(k,e['switch'],('&pro_micro %s'%e['pro_micro'][2:]) if e['pro_micro'].startswith('pm') else 'inner pad',e['gpio']))
    L+=['','ZMK direct key scan (`input-gpios` in key order R0C0..R2C5, T0..T2):','','```dts','kscan0: kscan {','    compatible = "zmk,kscan-gpio-direct";','    wakeup-source;','    input-gpios']
    rows=[]
    for k in order:
        e=pm[side][k]; pre='= ' if not rows else ', '
        if e['pro_micro'].startswith('pm'): rows.append('        %s<&pro_micro %s (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* %s %s */'%(pre,e['pro_micro'][2:],k,e['gpio']))
        else:
            port,pin=e['gpio'][1:].split('.')
            rows.append('        %s<&gpio%s %d (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>  /* %s %s inner pad */'%(pre,port,int(pin),k,e['gpio']))
    L+=rows+['        ;','};','```','']
L+=['## Switch sockets','','Every key takes either a Kailh MX hotswap socket or a Kailh Choc v1 hotswap socket, both on the back. Fit one type per key.',
'The Choc socket sits on the opposite side of the switch centre from the MX socket. Left-half switches are turned 180 degrees relative to v3 (except SW20) so the Choc socket stays clear of the board edge.','',
'## Power','','- Battery + goes from the BAT connector (pin marked +) through the PWR toggle (C&K GT11MSCBE) to the nice!nano B+ (RAW) pin.','- Battery - goes to ground.','- With the switch off the battery is disconnected, so it will not charge over USB.','- Check your battery lead polarity against the + and - silkscreen before plugging in. JST-PH battery polarity is not standardised.','']
open('proj/PINMAP.md','w').write('\n'.join(L))
