# Proteus files

- `AI-SED-PCB.pdsprj`: official design (schematic + PCB layout). Source of the Gerber files. Not modified for the simulation.
- `AI-SED-PCB-sim.pdsprj`: simulation copy of the same board used to run the firmware in Proteus VSM. It uses a corrected IIS3DWB symbol (`IIS3DWB_FIX`) and excludes from simulation the parts that have no Proteus model (U2, U3, U4, L1, D2, D3, J1-J4).
- `USERDVC.LIB` / `USERDVC.IDX`: user library that contains `IIS3DWB_FIX`. Copy both into `C:\ProgramData\Labcenter Electronics\Proteus 9 Professional\DATA\LIBRARY\`.
- `sim-demo-terminal.png`: Virtual Terminal output of the simulation (16/16 windows correct).

## How to run the simulation
1. Open `AI-SED-PCB-sim.pdsprj`.
2. Double-click the STM32F411CE: set *Program File* to `firmware/app/ai_sed_proteus.elf` and *Forced HCLK* to `16000000`.
3. The Virtual Terminal is on USART1_TX (PA9), 115200 baud, 8N1.
4. Start the simulation in debug mode (F12). Expected output: 16 lines `W<n> ... OK` and `Result: 16/16 correct`.

Limits: Proteus does not model the Cortex-M4 floating-point unit nor the DWT counter, so the Proteus ELF is a software-float build (`-DNO_DWT`). The IIS3DWB cannot be simulated; the windows come from CWRU data stored in flash.
