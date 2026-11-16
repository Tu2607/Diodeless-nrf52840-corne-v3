#!/bin/bash
set -e
cd /home/user/work/proj
rm -rf gerbers && mkdir gerbers
kicad-cli pcb export gerbers -o gerbers/ -l "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" --subtract-soldermask corne-diodeless.kicad_pcb > /dev/null 2>&1
kicad-cli pcb export drill -o gerbers/ --format excellon --excellon-separate-th corne-diodeless.kicad_pcb > /dev/null 2>&1
cd ..
kicad-cli pcb export svg -o render/top.svg -l "F.Cu,F.SilkS,F.Mask,Edge.Cuts" --page-size-mode 2 --exclude-drawing-sheet proj/corne-diodeless.kicad_pcb >/dev/null
kicad-cli pcb export svg -o render/bottom.svg -l "B.Cu,B.SilkS,B.Mask,Edge.Cuts" --mirror --page-size-mode 2 --exclude-drawing-sheet proj/corne-diodeless.kicad_pcb >/dev/null
kicad-cli pcb export svg -o render/bottom_unmirrored.svg -l "B.Cu,B.Mask,Edge.Cuts" --page-size-mode 2 --exclude-drawing-sheet proj/corne-diodeless.kicad_pcb >/dev/null
for n in top bottom bottom_unmirrored; do rsvg-convert -w 5600 -b white render/$n.svg -o render/$n.png; done
python3.12 - <<'P'
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
im=Image.open('render/top.png'); w,h=im.size; sx=w/275.708
c=lambda im,x0,y0,x1,y1: im.crop((int((x0-10.5875)*sx),int((y0-11.9385)*sx),int((x1-10.5875)*sx),int((y1-11.9385)*sx)))
c(im,120,24,178,90).save('render/power-switch-area.png')
c(Image.open('render/bottom_unmirrored.png'),66,36,107,62).save('render/socket-pads-detail.png')
for n in ('top','bottom'):
    i=Image.open('render/%s.png'%n); i.resize((3600,int(3600*h/w))).save('render/layout-%s.png'%n)
P
D=/mnt/project-files/corne-diodeless; mkdir -p $D/source
rm -f proj/*.kicad_prl corne-diodeless-gerbers.zip corne-diodeless-kicad.zip
(cd proj && zip -qr ../corne-diodeless-gerbers.zip gerbers && zip -qr ../corne-diodeless-kicad.zip . -x 'gerbers/*')
cp corne-diodeless-gerbers.zip corne-diodeless-kicad.zip proj/PINMAP.md render/layout-top.png render/layout-bottom.png render/power-switch-area.png render/socket-pads-detail.png $D/
cp stage1.py stage3.py router.py geom.py sx.py chk.py drc.py pinmap_md.py build.sh export.sh $D/source/
ls $D
