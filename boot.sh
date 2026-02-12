#!/bin/bash
# boot scutoidos in qemu

echo "booting ScutoidOS..."
echo "  ctrl+alt+g to release mouse"
echo "  ctrl+c to quit"
echo ""

qemu-system-i386 \
    -drive format=raw,file=neonpulse.img \
    -m 32M \
    -name "ScutoidOS"
