# Hardware

- `proteus/`: Proteus project (schematic + PCB layout). See its README.
- `library/`: custom IIS3DWB device and LGA-14 footprint (`Libreria_IIS3DWB.pdsprj`).
- `gerber/`: fabrication files generated from the routed board: copper, solder resist, silkscreen, paste, board profile, drill files, assembly layer and IPC-D-356A netlist.
- `bom/`: bill of materials. See its README.

Board: 2 layers, 5 × 5 cm. Checks passed in Proteus: 0 unrouted connections, 0 connectivity errors, 0 DRC errors, Pre-Production Check passed. Minimum clearance 5 mil; the solder mask between the sensor pads is very thin (about 0.05 mm), so tell the manufacturer.

Main parts: STM32F411CE (U1), LM2596S-3.3 (U2), IIS3DWB (U3), ESP32-C3-MINI-1 (U4). Pin assignments and design decisions are in the root README.
