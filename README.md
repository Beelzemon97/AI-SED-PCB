# AI-SED PCB: Embedded-AI Bearing-Fault Diagnosis

A 2-layer, 5 × 5 cm board that measures vibration with a digital accelerometer and runs a TinyML model to classify the state of a bearing (healthy, inner race, ball, outer race). Project of the **ITESCA PCB Lab** team for **AI-SED 2026** (AI Smart Electronic Design).

Team: Juan Alfonso Moroyoqui Delgadillo, Carlos Eduardo Tamayo Urrea, Alex Hiram Meza Esquer. Advisor: Dr. Marcos Alan Cota Leal.

## Status
- Done: routed 2-layer PCB (0 unrouted, 0 DRC errors, Pre-Production Check passed), Gerber files, bill of materials, TinyML classifier (100% on the unseen 3 HP load), C inference pipeline (identical to Python on 9,215 windows), and firmware simulated on the STM32F411CE in Proteus VSM (16/16 test windows correct).
- Pending: IIS3DWB SPI driver, ESP32-C3 communication firmware, board fabrication, on-board timing and validation on a real motor.

## Hardware
| Ref. | Part | Function |
|---|---|---|
| U1 | STM32F411CE | Microcontroller: reads the sensor and runs the model |
| U3 | IIS3DWB (LGA-14L, 2.5 × 3 mm) | Digital vibration accelerometer, SPI |
| U4 | ESP32-C3-MINI-1 | Wi-Fi / Bluetooth link |
| U2 | LM2596S-3.3 | 9-12 V to 3.3 V step-down regulator |
| L1 / D3 | SRN6045TA330M 33 µH / SS34 | Inductor and Schottky diode of the power stage |
| D2 | 1N5819H | Series reverse-polarity protection |

Main STM32 connections: SPI_CS / SCK / MISO / MOSI = PA4 / PA5 / PA6 / PA7, SENS_INT1 = PA1, UART_TX / RX = PA2 / PA3, USART1_TX / RX (ESP32 and J4) = PA9 / PA10, SWDIO / SWCLK = PA13 / PA14, TEST = PB0.

Design decisions: power stage far from the sensor and the antenna; ESP32 antenna at the board edge with a copper keepout on all layers; ground plane on the bottom layer; 0805 passives; minimum clearance 5 mil (the solder mask between sensor pads is very thin, about 0.05 mm: tell the manufacturer).

## Repository structure
- `hardware/proteus/`: Proteus project (official design + simulation copy), see its README
- `hardware/library/`: custom IIS3DWB device and footprint
- `hardware/gerber/`: fabrication files (Gerber + drill)
- `hardware/bom/`: bill of materials
- `docs/`: schematic PDF, images, layout drawings, competition document
- `firmware/`: C inference pipeline and demo firmware for the STM32F411CE
- `model/`: TinyML model (trained on CWRU) and training script

## Tools
Proteus 9 (ISIS, ARES, VSM), Python / TensorFlow, GNU Arm Embedded Toolchain.
