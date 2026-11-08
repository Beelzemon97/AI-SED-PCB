/* Minimal Cortex-M4F start-up: vector table, .data/.bss init, FPU enable. */
#include <stdint.h>
extern uint32_t _estack, _sidata, _sdata, _edata, _sbss, _ebss;
extern int main(void);
void Reset_Handler(void);
void Default_Handler(void) { for (;;) {} }

__attribute__((section(".isr_vector"), used))
void (*const vectors[16])(void) = {
    (void (*)(void))(&_estack), Reset_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    0, 0, 0, 0, Default_Handler, Default_Handler, 0, Default_Handler, Default_Handler };

void Reset_Handler(void)
{
    *(volatile uint32_t *)0xE000ED88 |= (0xFu << 20);            /* CPACR: enable FPU (CP10/CP11) */
    __asm volatile ("dsb\n isb");
    uint32_t *s = &_sidata, *d = &_sdata;
    while (d < &_edata) *d++ = *s++;
    for (d = &_sbss; d < &_ebss; ) *d++ = 0;
    main();
    for (;;) {}
}
