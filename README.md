# AI-SED PCB — Diagnóstico de rodamientos con IA embebida

Placa de 2 capas y 5 × 5 cm que mide vibración con un acelerómetro digital y ejecuta un modelo TinyML para clasificar el estado de un rodamiento. Proyecto del equipo **ITESCA PCB Lab** para **AI-SED 2026** (AI Smart Electronic Design).

> **Estado:** diseño de PCB ruteado, DRC limpio y Pre-production Check en *Pass*. Pendientes: Gerber/BOM, firmware y modelo de IA.

## Hardware

| Ref. | Pieza | Función |
|---|---|---|
| U1 | STM32F411CE | Microcontrolador: lee el sensor y ejecuta el modelo |
| U3 | IIS3DWB (LGA-14L, 2.5 × 3 mm) | Acelerómetro digital de vibración, interfaz SPI |
| U4 | ESP32-C3-MINI | Comunicación inalámbrica (Wi-Fi / BLE) |
| U2 | LM2596S-3.3 | Regulador reductor de 9–12 V a 3.3 V |
| L1 / D3 | SRN6045TA330M 33 µH / SS34 | Inductor y diodo Schottky de la fuente |
| D2 | 1N5819H | Protección contra polaridad inversa en serie |
| J1 | Conector SWD | Programación y depuración del STM32 |
| J2 | Conector UART | Salida serie al PC (PA2 / PA3) |
| J3 | Entrada de alimentación | 9–12 V |
| J4 | Programación del ESP32 | Adaptador USB-serie (USART1) |

### Conexiones principales del STM32

| Señal | Pin |
|---|---|
| SPI_CS / SPI_SCK / SPI_MISO / SPI_MOSI (sensor) | PA4 / PA5 / PA6 / PA7 |
| SENS_INT1 (dato listo del sensor) | PA1 |
| UART_TX / UART_RX (J2) | PA2 / PA3 |
| USART1_TX / USART1_RX (ESP32 y J4) | PA9 / PA10 |
| SWDIO / SWCLK (J1) | PA13 / PA14 |
| TEST | PB0 |

### Decisiones de diseño

- **Fuente alejada** del sensor y de la antena: L1 y D3 quedan en la esquina opuesta.
- **Antena del ESP32** en el borde superior, con zona *Keepout* (sin cobre en ninguna capa).
- **Plano de tierra** en la cara inferior.
- Componentes pasivos en formato **0805**.
- Regla de separación mínima usada: 5 mil. Entre los pads del sensor la máscara de soldadura es muy delgada (~0.05 mm); avisar al fabricante.

## Estructura del repositorio

```
hardware/proteus/   Proyecto de Proteus (.pdsprj)
hardware/library/   Librería propia: dispositivo y huella del IIS3DWB
hardware/gerber/    Archivos de fabricación (Gerber + taladros)
hardware/bom/       Lista de materiales
docs/               Esquemático en PDF, imágenes, plano de acomodo
firmware/           Código del STM32
model/              Modelo TinyML (entrenado con CWRU)
```

## Pendientes

Firmware del ESP32-C3 (comunicación) sin escribir.
Controlador del sensor IIS3DWB por SPI.
Fabricación de la placa y pruebas en hardware real (el firmware solo se ha probado en emulador y en Proteus).

## Herramientas

Proteus 9 (ISIS y ARES).
