## Appendix A: The microwave innovation matrix

Figure A1 (`0_innovation_matrix.png`) shows the whole graph. All 123 nodes are listed below by layer; the 246 edges and their types are in `microwave_base_graph.yaml`.

**Market needs (17)**

| ID | Label |
| --- | --- |
| M1 | Fast reheating for busy households |
| M2 | Crispy, browned texture like conventional oven |
| M3 | Hot milk / drink ready for breakfast |
| M4 | Defrost frozen food quickly |
| M5 | Save time in the kitchen |
| M6 | Simple operation with no learning curve |
| M7 | Safe for family use (radiation, burns, electric shock) |
| M8 | Human need for feedback (know when food is ready) |
| M9 | Low purchase price |
| M10 | Small kitchen footprint |
| M11 | Easy to clean |
| M12 | Healthy diet (nutrient retention, less fat) |
| M13 | Energy efficiency |
| M14 | Accessible for elderly / visually impaired users |
| M15 | Appliances that make you feel better (latent need) |
| M16 | Need for mobility (not having to stand by the appliance) |
| M17 | Bake a birthday cake (prep tasks like melting butter) |

**Functions (20)**

| ID | Label |
| --- | --- |
| F1 | Generates microwave energy at 2.45 GHz |
| F2 | Converts mains voltage to ~4 kV DC for the magnetron |
| F3 | Guides microwave energy into the cavity |
| F4 | Heats food via dielectric water-molecule vibration (FastHeating) |
| F5 | Distributes heat evenly by rotating food through the field |
| F6 | Contains microwave radiation inside the appliance |
| F7 | Sets and counts down cooking duration |
| F8 | Sets average heating power level |
| F9 | Opens and closes the door to access the cavity |
| F10 | Cuts RF power instantly when the door opens |
| F11 | Illuminates cavity so the user can watch the food |
| F12 | Signals end of cooking (audible alert) |
| F13 | Cools magnetron and electronics |
| F14 | Protects against overheating |
| F15 | Protects against overcurrent and electrical faults |
| F16 | Defrosts frozen food (low-power cycling) |
| F17 | Melts / softens butter, chocolate, etc. |
| F18 | Contains spills and allows cleaning |
| F19 | Suppresses electrical noise conducted back to mains |
| F20 | Discharges stored high voltage after switch-off |

**Components (28)**

| ID | Label |
| --- | --- |
| C1 | Magnetron tube (2.45 GHz, ~700 W output) |
| C2 | High-voltage transformer |
| C3 | High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor |
| C4 | High-voltage rectifier diode |
| C5 | Waveguide duct |
| C6 | Mica waveguide cover |
| C7 | Enamelled steel cooking cavity (~20 L) |
| C8 | Hinged door with perforated metal mesh window |
| C9 | Door choke seal (quarter-wave rim) |
| C10 | Rotating glass turntable tray |
| C11 | Roller ring and coupler (turntable support) |
| C12 | Turntable motor (~5 rpm) |
| C13 | Mechanical timer knob & cam switch (0-30 min) |
| C14 | Power-level knob (5-step duty-cycle cam switch) |
| C15 | Door-release push button & latch lever |
| C16 | Door interlock microswitches (primary, secondary, monitor) |
| C17 | Interior lamp (20-25 W incandescent) |
| C18 | Cooling fan and fan motor |
| C19 | Magnetron thermal cutout |
| C20 | Cavity thermal cutout |
| C21 | Main ceramic fuse |
| C22 | End-of-cycle bell (mechanical 'ding') |
| C23 | Outer steel cabinet (wrapper) |
| C24 | Control panel fascia |
| C25 | Mains power cord and plug |
| C26 | Door hinges |
| C27 | Ventilation louvres |
| C28 | Mains EMI noise filter |

**Technologies (24)**

| ID | Label |
| --- | --- |
| T1 | Electron cyclotron motion in crossed E×B fields (cavity magnetron) |
| T2 | Magnetic-shunt leakage HV transformer |
| T3 | Half-wave voltage doubler (capacitor + diode) |
| T4 | Rectangular waveguide TE10 mode propagation |
| T5 | Sub-wavelength aperture shielding (Faraday cage effect) |
| T6 | Quarter-wave choke seal |
| T7 | Shaded-pole / synchronous AC micro-motor (electromagnetic induction) |
| T8 | Motor-driven cam timer with spring-return mechanism |
| T9 | Bimetallic snap-disc thermostat |
| T10 | Redundant interlock microswitch logic (primary / secondary / monitor) |
| T11 | Duty-cycle power modulation (on/off cycling) |
| T12 | Incandescent tungsten-filament lamp |
| T13 | Forced-air convection cooling |
| T14 | Dielectric heating (dipolar rotation of water molecules) |
| T15 | Tempered / borosilicate glass forming |
| T16 | Mica sheet dielectric (muscovite laminate) |
| T17 | Enamel / epoxy powder coating of steel |
| T18 | Spring-loaded lever latch mechanics |
| T19 | Mechanical bell striker |
| T20 | Ceramic cartridge fuse (fusible-link overcurrent protection) |
| T21 | Sintered ferrite permanent magnets |
| T22 | Injection-molded engineering thermoplastics (PP, PBT, PPS) |
| T23 | Sheet-steel stamping & spot welding |
| T24 | Passive LC EMI line filtering |

**Fields (10)**

| ID | Label |
| --- | --- |
| D1 | Radio-frequency & microwave engineering |
| D2 | Vacuum electronics |
| D3 | Power electronics & electrical engineering |
| D4 | Electromechanics & mechanisms |
| D5 | Thermal engineering & heat transfer |
| D6 | Materials science (metals, ceramics, glass, polymers) |
| D7 | Lighting & optics |
| D8 | Sound engineering |
| D9 | Manufacturing engineering (stamping, molding, assembly) |
| D10 | Food science (dielectric properties of food) |

**Constraints (15)**

| ID | Label |
| --- | --- |
| X1 | Microwaves can't brown or crisp food surfaces |
| X2 | FCC/FDA radiation-leakage safety limits (21 CFR 1030.10, 5 mW/cm² at 5 cm) |
| X3 | Uneven heating — standing-wave hot and cold spots |
| X4 | Metal objects in cavity cause arcing |
| X5 | Mechanical timer imprecise for short (<1 min) durations |
| X6 | Power only adjustable by on/off cycling, not continuously |
| X7 | HV capacitor can hold a lethal charge after unplugging |
| X8 | Limited magnetron lifetime (cathode/filament wear) |
| X9 | Superheating of liquids — risk of eruptive boiling |
| X10 | Electrical safety standards (IEC 60335-2-25 / UL 923) |
| X11 | Cavity volume limited by countertop size |
| X12 | Low BOM target for entry-level price segment |
| X13 | No food-state sensing — open-loop cooking |
| X14 | Interior lamp burns out and is hard to replace |
| X15 | Regional mains variants (230 V/50 Hz vs 120 V/60 Hz) |

**Actors (8)**

| ID | Label |
| --- | --- |
| A1 | Time-pressed home cook |
| A2 | Appliance safety regulator/inspector |
| A3 | Student / single-person household |
| A4 | Elderly user |
| A5 | Parent with young children |
| A6 | Office worker using a shared kitchen |
| A7 | Repair technician |
| A8 | OEM manufacturer / cost engineer |

**Product (1)**

| ID | Label |
| --- | --- |
| P1 | Basic countertop microwave oven (timer knob, power knob, door button, lamp) |
