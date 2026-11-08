#include <stdint.h>
#define REG(a) (*(volatile uint32_t *)(a))
#define RCC_AHB1ENR REG(0x40023830u)
#define RCC_APB2ENR REG(0x40023844u)
#define GPIOA_MODER REG(0x40020000u)
#define GPIOA_AFRH  REG(0x40020024u)
#define USART1_SR   REG(0x40011000u)
#define USART1_DR   REG(0x40011004u)
#define USART1_BRR  REG(0x40011008u)
#define USART1_CR1  REG(0x4001100Cu)
#ifndef BRR_VAL
#define BRR_VAL ((8u<<4)|11u)   /* 16 MHz / (16 x 115200) = 8.68 */
#endif
int main(void){
  RCC_AHB1ENR |= 1u; RCC_APB2ENR |= (1u<<4);
  GPIOA_MODER = (GPIOA_MODER & ~(3u<<18)) | (2u<<18);
  GPIOA_AFRH  = (GPIOA_AFRH & ~(0xFu<<4)) | (7u<<4);
  USART1_BRR = BRR_VAL; USART1_CR1 = (1u<<13)|(1u<<3);
  const char *m="HELLO AI-SED\r\n";
  for(;;){ for(const char*p=m;*p;p++){ while(!(USART1_SR&(1u<<7))){} USART1_DR=(uint32_t)*p; } for(volatile uint32_t d=0; d<20000u; d++){} }
}
