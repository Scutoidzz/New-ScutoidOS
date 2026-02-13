#!/usr/bin/env python3
# stitch bootloader + kernel into a bootable floppy image

import struct, sys, os

def build(boot_path, kern_path, out_path):
    print(f"reading bootloader: {boot_path}")
    try:
        with open(boot_path, 'rb') as f:
            boot = f.read()
    except FileNotFoundError:
        print(f"error: {boot_path} not found")
        sys.exit(1)

    if len(boot) > 512:
        print(f"bootloader too big: {len(boot)} bytes")
        sys.exit(1)

    # check for 0xAA55 signature
    if len(boot) >= 2:
        sig = struct.unpack('<H', boot[-2:])[0]
        if sig != 0xAA55:
            print(f"warning: bad boot sig 0x{sig:04X}")

    # pad to exactly one sector
    if len(boot) < 512:
        boot += b'\x00' * (512 - len(boot))

    print(f"reading kernel: {kern_path}")
    try:
        with open(kern_path, 'rb') as f:
            kern = f.read()
    except FileNotFoundError:
        print(f"error: {kern_path} not found")
        sys.exit(1)

    sectors = (len(kern) + 511) // 512
    print(f"kernel: {len(kern)} bytes ({sectors} sectors)")

    # pad kernel to sector boundary
    if len(kern) % 512:
        kern += b'\x00' * (512 - len(kern) % 512)

    img = boot + kern

    # pad to 1.44MB floppy
    floppy = 1474560
    if len(img) < floppy:
        img += b'\x00' * (floppy - len(img))

    with open(out_path, 'wb') as f:
        f.write(img)

    print(f"wrote {out_path} ({len(img)} bytes)")
    print(f"  boot: 512 bytes, kernel: sectors 1-{sectors}")
    print(f"  qemu-system-i386 -drive format=raw,file={out_path}")

if __name__ == "__main__":
    boot = sys.argv[1] if len(sys.argv) > 1 else "bootloader.bin"
    kern = sys.argv[2] if len(sys.argv) > 2 else "kernel.bin"
    out  = sys.argv[3] if len(sys.argv) > 3 else "scutoid.img"

    print("ScutoidOS image builder")
    print("=" * 40)
    build(boot, kern, out)
