/*
 * main.c - AI-SED 2026 bearing-fault diagnosis demo firmware (STM32F411CE)
 *
 * Runs the real pipeline (22 features + MLP 22-32-16-4) on 16 real CWRU windows
 * embedded in flash (the IIS3DWB sensor cannot be simulated), and reports each
 * diagnosis on USART1 (PA9, 115200 baud, 8N1), the same port that goes to the
 * ESP32-C3 on the board.
 */
#include <stdint.h>
#include "../src/ai_pipeline.h"
#include "test_data.h"

#define REG(a) (*(volatile uint32_t *)(a))
#define RCC_AHB1ENR  REG(0x40023830u)
#define RCC_APB2ENR  REG(0x40023844u)
#define GPIOA_MODER  REG(0x40020000u)
#define GPIOA_AFRH   REG(0x40020024u)
#define USART1_SR    REG(0x40011000u)
#define USART1_DR    REG(0x40011004u)
#define USART1_BRR   REG(0x40011008u)
#define USART1_CR1   REG(0x4001100Cu)
#define DEMCR        REG(0xE000EDFCu)
#define DWT_CTRL     REG(0xE0001000u)
#ifdef NO_DWT   /* simulators that do not model the debug block (e.g. Proteus VSM) */
#define DWT_CYCCNT   0u
#else
#define DWT_CYCCNT   REG(0xE0001004u)
#endif

static void uart_init(void)
{
    RCC_AHB1ENR |= 1u;                          /* GPIOA clock          */
    RCC_APB2ENR |= (1u << 4);                   /* USART1 clock         */
    GPIOA_MODER = (GPIOA_MODER & ~(3u << 18)) | (2u << 18);   /* PA9 alternate function */
    GPIOA_AFRH  = (GPIOA_AFRH  & ~(0xFu << 4)) | (7u << 4);   /* AF7 = USART1          */
    USART1_BRR  = (8u << 4) | 11u;              /* 16 MHz / (16 x 115200) = 8.68 -> 115107 baud (0.08 %) */
    USART1_CR1  = (1u << 13) | (1u << 3);       /* UE | TE              */
}
static void put_c(char c) { while (!(USART1_SR & (1u << 7))) {} USART1_DR = (uint32_t)c; }
static void put_s(const char *s) { while (*s) put_c(*s++); }
static void put_u(uint32_t v)
{
    char b[11]; int n = 0;
    do { b[n++] = (char)('0' + v % 10u); v /= 10u; } while (v);
    while (n) put_c(b[--n]);
}
static void put_pct(float p)        /* 0..1 -> "99.8" */
{
    uint32_t t = (uint32_t)(p * 1000.0f + 0.5f);
    put_u(t / 10u); put_c('.'); put_u(t % 10u);
}

int main(void)
{
    uart_init();
#ifndef NO_DWT
    DEMCR |= (1u << 24); DWT_CTRL |= 1u;        /* cycle counter */
#endif
    put_s("BOOT\r\n");

    for (;;) {
        put_s("\r\n=== AI-SED bearing diagnosis (STM32F411CE) ===\r\n");
        uint32_t ok = 0;
        for (uint32_t i = 0; i < N_TEST; i++) {
            float prob[4];
            uint32_t t0 = DWT_CYCCNT;
            ai_class_t c = ai_diagnose(TEST_WIN[i], prob);
            uint32_t cyc = DWT_CYCCNT - t0;
            put_s("W"); put_u(i + 1);
            put_s(" ["); put_s(TEST_TAG[i]); put_s("] true=");
            put_s(CLASS_NAME[TEST_TRUE[i]]);
            put_s(" pred="); put_s(CLASS_NAME[c]);
            put_s(" conf="); put_pct(prob[c]); put_s("%");
            if (cyc) { put_s(" cycles="); put_u(cyc); }
            put_s(c == TEST_TRUE[i] ? "  OK\r\n" : "  WRONG\r\n");
            ok += (c == TEST_TRUE[i]);
        }
        put_s("Result: "); put_u(ok); put_s("/"); put_u(N_TEST); put_s(" correct\r\n");
        for (volatile uint32_t d = 0; d < 4000000u; d++) {}
    }
}
