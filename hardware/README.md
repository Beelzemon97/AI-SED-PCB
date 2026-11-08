# AI-SED PCB: Embedded-AI Bearing-Fault Diagnosis

A 2-layer, 5 × 5 cm board that measures vibration with a digital accelerometer and runs a TinyML model to classify the state of a bearing. Project of the **ITESCA PCB Lab** team for **AI-SED 2026** (AI Smart Electronic Design).

> **Status:** routed PCB, DRC-clean, Pre-Production Check passed. Gerber files, bill of materials, trained model and firmware (simulated in Proteus VSM) are done. Pending: SPI driver for the IIS3DWB, ESP32-C3 firmware, fabrication and on-board validation.

## Hardware

| Ref. | Part | Function |
|---|---|---|
| U1 | STM32F411CE | Microcontroller: reads the sensor and runs the model |
| U3 | IIS3DWB (LGA-14L, 2.5 × 3 mm) | Digital vibration accelerometer, SPI interface |
| U4 | ESP32-C3-MINI-1 | Wireless communication (Wi-Fi / BLE) |
| U2 | LM2596S-3.3 | 9-12 V to 3.3 V step-down regulator |
| L1 / D3 | SRN6045TA330M 33 µH / SS34 | Inductor and Schottky diode of the power stage |
| D2 | 1N5819H | Series reverse-polarity protection |
| J1 | SWD connector | STM32 programming and debugging |
| J2 | UART connector | Serial output to a PC (PA2 / PA3) |
| J3 | Power input | 9-12 V |
| J4 | ESP32 programming | USB-serial adapter (USART1) |

### Main STM32 connections

| Signal | Pin |
|---|---|
| SPI_CS / SPI_SCK / SPI_MISO / SPI_MOSI (sensor) | PA4 / PA5 / PA6 / PA7 |
| SENS_INT1 (sensor data ready) | PA1 |
| UART_TX / UART_RX (J2) | PA2 / PA3 |
| USART1_TX / USART1_RX (ESP32 and J4) | PA9 / PA10 |
| SWDIO / SWCLK (J1) | PA13 / PA14 |
| TEST | PB0 |

### Design decisions

- **Power stage far from the sensor and the antenna:** L1 and D3 sit in the opposite corner.
- **ESP32 antenna** at the top edge, with a copper keepout on all layers.
- **Ground plane** on the bottom layer.
- Passives in **0805** size.
- Minimum clearance used: 5 mil. The solder mask between the sensor pads is very thin (about 0.05 mm); tell the manufacturer.

## Folder contents

```
proteus/   Proteus project (official design + simulation copy)
library/   Custom IIS3DWB device and footprint
gerber/    Fabrication files (Gerber + drill)
bom/       Bill of materials
```

## Tools

Proteus 9 (ISIS, ARES, VSM).
