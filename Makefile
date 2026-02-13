# ScutoidOS Makefile

ASM = nasm
CC = gcc
LD = ld
PYTHON = python3

ASMFLAGS = -f bin
CFLAGS = -m32 -ffreestanding -fno-pie -nostdlib -nostdinc -fno-builtin -fno-stack-protector -O2 -Wall -Wextra
LDFLAGS = -m elf_i386 -T linker.ld --oformat binary

BOOTLOADER_BIN = bootloader.bin
KERNEL_OBJ = kernel.o terminal.o
KERNEL_BIN = kernel.bin
OS_IMAGE = scutoid.img

BOOTLOADER_SRC = bootloader.asm
KERNEL_SRC = kernel.c
TERMINAL_SRC = terminal.c

.PHONY: all clean run debug

all: $(OS_IMAGE)
	@echo ""
	@echo "build done: $(OS_IMAGE)"
	@echo "run with: make run"

$(BOOTLOADER_BIN): $(BOOTLOADER_SRC)
	@echo "[asm] bootloader"
	$(ASM) $(ASMFLAGS) $(BOOTLOADER_SRC) -o $(BOOTLOADER_BIN)

kernel.o: $(KERNEL_SRC) terminal.h interrupt.h
	@echo "[cc] kernel"
	$(CC) $(CFLAGS) -c $(KERNEL_SRC) -o kernel.o

terminal.o: $(TERMINAL_SRC) terminal.h interrupt.h
	@echo "[cc] terminal"
	$(CC) $(CFLAGS) -c $(TERMINAL_SRC) -o terminal.o

$(KERNEL_BIN): $(KERNEL_OBJ) linker.ld
	@echo "[ld] kernel"
	$(LD) $(LDFLAGS) $(KERNEL_OBJ) -o $(KERNEL_BIN)

$(OS_IMAGE): $(BOOTLOADER_BIN) $(KERNEL_BIN) build_image.py
	@echo "[img] creating disk image"
	$(PYTHON) build_image.py $(BOOTLOADER_BIN) $(KERNEL_BIN) $(OS_IMAGE)

run: $(OS_IMAGE)
	@echo ""
	@echo "booting ScutoidOS..."
	@echo "ctrl+c to quit, ctrl+alt+g to release mouse"
	@echo ""
	qemu-system-i386 -drive format=raw,file=$(OS_IMAGE)

debug: $(OS_IMAGE)
	@echo "debug boot..."
	qemu-system-i386 -drive format=raw,file=$(OS_IMAGE) -d int,cpu_reset -no-reboot

clean:
	rm -f $(BOOTLOADER_BIN) kernel.o terminal.o $(KERNEL_BIN) $(OS_IMAGE)
	@echo "clean."

info:
	@echo "ScutoidOS build system"
	@echo "  make all   - build"
	@echo "  make run   - build + boot in qemu"
	@echo "  make debug - boot with debug"
	@echo "  make clean - remove artifacts"
