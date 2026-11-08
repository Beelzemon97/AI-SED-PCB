# Proteus files

- `AI-SED-PCB.pdsprj`: official design (schematic + PCB layout). Source of the Gerber files.
- `sim-demo-terminal.png`: Proteus VSM simulation of the firmware on the STM32F411CE of the board. The Virtual Terminal (USART1, PA9, 115200 baud) shows the diagnosis of 16 test windows: 16/16 correct.

## How the simulation was run
- The firmware is `firmware/app/ai_sed_proteus.elf`, loaded as the *Program File* of the STM32F411CE, with *Forced HCLK* set to `16000000`.
- The Virtual Terminal is connected to USART1_TX (PA9), 115200 baud, 8N1. The simulation runs in debug mode.
- Parts without a Proteus model (LM2596S-3.3, IIS3DWB, ESP32-C3-MINI-1, inductor, diodes and connectors) were excluded from the simulation, and the IIS3DWB was replaced by a corrected symbol in a separate simulation copy of the board.
- Limits: Proteus does not model the Cortex-M4 floating-point unit nor the DWT counter, so the Proteus ELF is a software-float build (`-DNO_DWT`). The IIS3DWB cannot be simulated; the windows come from CWRU data stored in flash.

The simulation copy of the project is being revalidated with the working sensor and will be added in the `sensor-validation` branch.
