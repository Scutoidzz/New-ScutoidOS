# ScutoidOS

A small operating system built from scratch — x86 assembly bootloader, C kernel, boots into a command shell.

## What it does

- Boots from a raw disk image
- 16-bit bootloader transitions to 32-bit protected mode
- Sets up keyboard interrupts with a shared ring buffer
- Drops you into a command shell

## Building

You need: `nasm`, `gcc` (32-bit), `ld`, `python3`, `qemu-system-i386`

```bash
make all    # build the image
make run    # build + boot in qemu
make clean  # cleanup
```

## Files

```
ScutoidOS/
├── bootloader.asm    # real mode -> protected mode
├── kernel.c          # C kernel with built-in shell
├── linker.ld         # loads kernel at 0x10000
├── build_image.py    # stitches boot + kernel into image
├── Makefile
├── main.py           # micropython shell (for later)
├── programs/         # apps (calculator, terminal, textedit)
├── installer/        # installs programs into Apps/
└── scutoid.img     # the bootable image
```

## Memory layout

| Address | What |
|---------|------|
| `0x7C00` | Bootloader |
| `0x9000` | Keyboard buffer (256 bytes) |
| `0x10000` | Kernel |
| `0x8C000-0x90000` | Stack (16KB) |
| `0xB8000` | VGA text buffer |

## Shell commands

Once booted you get a `scutoidos>` prompt. Available commands:

`help` `about` `mem` `clear` `colors` `echo` `reboot`

## License

MIT
