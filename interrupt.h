#ifndef INTERRUPT_H
#define INTERRUPT_H

static inline void enable_interrupts(void) {
    __asm__ volatile("sti");
}

static inline void disable_interrupts(void) {
    __asm__ volatile("cli");
}

static inline unsigned int save_interrupts(void) {
    unsigned int flags;
    __asm__ volatile("pushfl; popl %0" : "=r"(flags));
    return flags;
}

static inline void restore_interrupts(unsigned int flags) {
    __asm__ volatile("pushl %0; popfl" : : "r"(flags));
}

#endif
