# Top 10 and bottom 10 ideas

2892 ideas scored individually and blind by `claude-sonnet-5-5` on relevance, novelty, feasibility, specificity (1–5). Score = mean of the four criteria. Cost per idea = the generating call's total tokens divided by its number of ideas.

## Who made them

| Arm | In top | In bottom |
| --- | --- | --- |
| A (full graph), high effort | 2 | 0 |
| A (full graph), low effort | 0 | 1 |
| A (full graph), medium effort | 2 | 0 |
| A (full graph), xhigh effort | 1 | 0 |
| B (need slice), high effort | 2 | 2 |
| B (need slice), low effort | 1 | 6 |
| B (need slice), medium effort | 0 | 1 |
| B (need slice), xhigh effort | 1 | 0 |
| R (random slice), high effort | 1 | 0 |

## Top 10

| Rank | Idea | Score | Rel | Nov | Feas | Spec | Condition | Effort | Need | Tokens / idea |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Solid-State RF Core: Magnetron and HV Stack Replaced by GaN Amplifiers | 4.50 | 5 | 4 | 4 | 5 | A (full graph) | high | M13 | 4,037 |
| 2 | Magnetron-free solid-state RF cooking head | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | low | M13 | 1,469 |
| 3 | Solid-State Heart: GaN Amplifier Replaces Magnetron and HV Chain | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M13 | 2,801 |
| 4 | 27 MHz Solid-State Electrode Thaw | 4.50 | 5 | 4 | 4 | 5 | A (full graph) | high | M4 | 4,266 |
| 5 | 27 MHz RF Thaw Plates | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M4 | 2,115 |
| 6 | Solid-State GaN Amplifier Replaces the Magnetron Stack | 4.50 | 5 | 4 | 4 | 5 | A (full graph) | medium | M13 | 3,336 |
| 7 | Solid-State 915 MHz Frequency-Agile Defroster | 4.50 | 5 | 4 | 4 | 5 | A (full graph) | medium | M4 | 3,449 |
| 8 | Solid-State 27 MHz Electrode Thaw | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | xhigh | M4 | 7,336 |
| 9 | Magnetron-free 27 MHz capacitive thaw | 4.50 | 5 | 4 | 4 | 5 | A (full graph) | xhigh | M4 | 9,153 |
| 10 | Solid-State Cooking Array (no magnetron, no high voltage) | 4.50 | 5 | 4 | 4 | 5 | R (random slice) | high | M7 | 2,398 |

### #1 Solid-State RF Core: Magnetron and HV Stack Replaced by GaN Amplifiers

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M13_high_r03`
- **Target need:** M13 — Energy efficiency
- **Cost:** 4,037 tokens per idea (run: 10,906 in + 9,277 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); T11 (Duty-cycle power modulation (on/off cycling)); X6 (Power only adjustable by on/off cycling, not continuously)
- **New elements:** Technology: GaN solid-state 2.45 GHz RF amplification — Paralleled gallium-nitride transistor stages generate 2.45 GHz RF from a low-voltage DC rail, with no cathode, filament or kV rail.; Component: GaN RF power amplifier module — Replaces the magnetron tube with a ~700 W transistor array that has no warm-up and no filament standby draw.; Technology: High-frequency switch-mode low-voltage PSU — Compact ~48 V SMPS replaces the iron-core HV transformer, voltage doubler capacitor and HV diode.; Component: Low-voltage SMPS board — Replaces transformer, HV capacitor and diode, removing core losses and the bleeder-resistor drain.; Function: Continuous analog RF power control — Sets any average power by gain control, so the on/off duty-cycle overshoot is eliminated.
- **New edges:** GaN solid-state 2.45 GHz RF amplification -[rooted_in]-> D1; GaN RF power amplifier module -[enabled_by]-> GaN solid-state 2.45 GHz RF amplification; GaN RF power amplifier module -[performs_function]-> F1; GaN RF power amplifier module -[resolves]-> C1; High-frequency switch-mode low-voltage PSU -[rooted_in]-> D3; Low-voltage SMPS board -[enabled_by]-> High-frequency switch-mode low-voltage PSU; Low-voltage SMPS board -[performs_function]-> F2; Low-voltage SMPS board -[resolves]-> C2; Continuous analog RF power control -[resolves]-> X6; Continuous analog RF power control -[addresses_need]-> M13
- **Rationale:** Removing the kV transformer, capacitor, diode and magnetron cathode cuts conversion and standby losses, and continuous power control ends the wasteful on/off cycling that drives M13 energy use.
- **Judge:** Solid-state RF is real and directly raises efficiency by removing HV stack losses and enabling continuous power control, though 700 W GaN cost remains a hurdle.

### #2 Magnetron-free solid-state RF cooking head

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M13_low_r01`
- **Target need:** M13 — Energy efficiency
- **Cost:** 1,469 tokens per idea (run: 4,520 in + 2,827 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); F1 (Generates microwave energy at 2.45 GHz); F2 (Converts mains voltage to ~4 kV DC for the magnetron)
- **New elements:** Technology: GaN solid-state RF amplifier at 2.45 GHz — Transistor-based power amplifier with phase-controlled outputs replaces the thermionic magnetron and its HV supply chain.; Component: Solid-state RF amplifier array — Low-voltage (48 V DC) amplifier modules driven by a switching supply, tuned to food load in real time.; Function: Delivers only the RF power the load absorbs — Closed-loop reflected-power sensing modulates output so energy is not wasted into a mismatched cavity.; Constraint: Solid-state RF cost per watt still above magnetron — Current GaN parts cost more per watt, offset by removing transformer, capacitor and diode.
- **New edges:** Solid-state RF amplifier array -[performs_function]-> Function; GaN solid-state RF amplifier at 2.45 GHz -[resolves]-> C1; Solid-state RF amplifier array -[resolves]-> C2; Solid-state RF amplifier array -[resolves]-> C3; Solid-state RF amplifier array -[resolves]-> C4; Delivers only the RF power the load absorbs -[addresses_need]-> M13; Solid-state RF cost per watt still above magnetron -[causes]-> Solid-state RF amplifier array; C1 -[partially_mitigates]-> X8
- **Rationale:** Removing the magnetron's ~4 kV conversion chain and matching RF output to load eliminates the largest standby and conversion losses, cutting energy per heated portion.
- **Judge:** Solid-state RF cooking is real and boosts efficiency through load matching, though cost is high and the substitution is not cheaper.

### #3 Solid-State Heart: GaN Amplifier Replaces Magnetron and HV Chain

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M13_high_r03`
- **Target need:** M13 — Energy efficiency
- **Cost:** 2,801 tokens per idea (run: 4,520 in + 9,484 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode)
- **New elements:** Component: GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) — Low-voltage transistor power amplifier replaces the magnetron and its 4 kV transformer-doubler chain; no cathode to wear and no lethal HV.; Technology: Gallium nitride HEMT power amplifier — Wide-bandgap transistors reach high DC-to-RF efficiency at 2.45 GHz and allow precise, proportional power control.; Component: 50 V switch-mode PSU — Compact high-frequency SMPS replaces the bulky 50 Hz HV transformer and voltage doubler, so mains-frequency losses disappear.
- **New edges:** GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C1; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C2; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C3; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C4; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[performs_function]-> F1; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[enabled_by]-> Gallium nitride HEMT power amplifier; 50 V switch-mode PSU -[performs_function]-> F2; 50 V switch-mode PSU -[feeds]-> GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail); GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[partially_mitigates]-> X8; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[partially_mitigates]-> X7; F1 -[addresses_need]-> M13
- **Rationale:** Solid-state RF generation with a low-voltage supply removes the magnetron's heat-and-conversion losses and gives proportional power, so less electricity is wasted per cooked meal.
- **Judge:** Solid-state RF replacing the magnetron is a real, directly efficiency-relevant substitution (GaN ovens exist), though cost is high and efficiency gains are moderate.

### #4 27 MHz Solid-State Electrode Thaw

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M4_high_r05`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 4,266 tokens per idea (run: 10,910 in + 10,419 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C5 (Waveguide duct); C6 (Mica waveguide cover); F1 (Generates microwave energy at 2.45 GHz); F3 (Guides microwave energy into the cavity)
- **New elements:** Technology: Solid-state 27 MHz RF oscillator (LDMOS/GaN) — Low-frequency RF with a wavelength of about 11 m penetrates frozen blocks deeply and produces fewer standing-wave hot spots than 2.45 GHz.; Component: Parallel-plate RF electrode shelves — Capacitive electrodes above and below the food replace the magnetron, waveguide and mica cover.; Function: Volumetric thaw from the inside out — Heats the whole frozen block at once so the surface does not cook while the centre stays frozen.
- **New edges:** Solid-state 27 MHz RF oscillator (LDMOS/GaN) -[rooted_in]-> D1; Parallel-plate RF electrode shelves -[enabled_by]-> Solid-state 27 MHz RF oscillator (LDMOS/GaN); Parallel-plate RF electrode shelves -[performs_function]-> Volumetric thaw from the inside out; Volumetric thaw from the inside out -[addresses_need]-> M4; Volumetric thaw from the inside out -[enables_function]-> F16; Parallel-plate RF electrode shelves -[partially_mitigates]-> X3; Solid-state 27 MHz RF oscillator (LDMOS/GaN) -[resolves]-> C1; Solid-state 27 MHz RF oscillator (LDMOS/GaN) -[resolves]-> X8; Parallel-plate RF electrode shelves -[resolves]-> C5; Parallel-plate RF electrode shelves -[resolves]-> C6
- **Rationale:** Lower-frequency RF heats frozen food deeply and evenly, which speeds up thawing and removes the magnetron's lifetime limit.
- **Judge:** Solid-state 27 MHz RF thawing with electrodes is real technology (RF defrosters exist) and fits the need well, though it is not cheaper or simpler and the electrode setup is tricky.

### #5 27 MHz RF Thaw Plates

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r03`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 2,115 tokens per idea (run: 4,996 in + 5,581 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C5 (Waveguide duct); F1 (Generates microwave energy at 2.45 GHz); F3 (Guides microwave energy into the cavity)
- **New elements:** Technology: Solid-state RF amplifier at 27 MHz (LDMOS/GaN) — Low-cost transistor power stage replaces the vacuum magnetron, with no cathode to wear out.; Component: Parallel-plate RF electrode pair — Food sits between two insulated plates, so the field penetrates the full thickness of a frozen block.; Function: Volumetric thaw of ice through full thickness — Longer RF wavelength heats the interior of a frozen block evenly instead of only the surface.
- **New edges:** Solid-state RF amplifier at 27 MHz (LDMOS/GaN) -[resolves]-> C1; Parallel-plate RF electrode pair -[resolves]-> C5; Parallel-plate RF electrode pair -[performs_function]-> Volumetric thaw of ice through full thickness; Volumetric thaw of ice through full thickness -[addresses_need]-> M4; Solid-state RF amplifier at 27 MHz (LDMOS/GaN) -[partially_mitigates]-> X8
- **Rationale:** Lower-frequency RF penetrates frozen blocks deeply and uniformly, so the thaw is faster and more even than surface-first 2.45 GHz heating.
- **Judge:** RF thawing at 27 MHz is real and effective for frozen blocks, and solid-state RF replacing the magnetron fits the SUBSTITUTE operator, though cost and shielding remain challenges.

### #6 Solid-State GaN Amplifier Replaces the Magnetron Stack

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition A (full graph), medium effort · run `A_M13_medium_r04`
- **Target need:** M13 — Energy efficiency
- **Cost:** 3,336 tokens per idea (run: 10,906 in + 5,773 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode)
- **New elements:** Technology: GaN solid-state RF amplifier at 2.45 GHz — Gallium-nitride transistor amplifier with drive-level power control replaces the cathode, filament, and high-voltage rail.; Component: Solid-state RF amplifier module (12-24 V DC) — Low-voltage transistor module with heatsink, powered from a small switch-mode supply, with no 4 kV doubler or HV capacitor.; Function: Delivers continuous, variable RF power without on/off cycling — Power is set by drive level, so there is no filament standby draw and no duty-cycle waste.
- **New edges:** Solid-state RF amplifier module (12-24 V DC) -[resolves]-> C1; Solid-state RF amplifier module (12-24 V DC) -[resolves]-> C2; Solid-state RF amplifier module (12-24 V DC) -[resolves]-> C3; Solid-state RF amplifier module (12-24 V DC) -[resolves]-> C4; GaN solid-state RF amplifier at 2.45 GHz -[partially_mitigates]-> F1; Delivers continuous, variable RF power without on/off cycling -[addresses_need]-> M13; Solid-state RF amplifier module (12-24 V DC) -[partially_mitigates]-> X7
- **Rationale:** Removing the filament standby draw, the 4 kV rail, and the duty-cycle losses cuts wasted electricity at every use and at idle.
- **Judge:** Solid-state RF cooking is real and efficiency-relevant (no filament, variable power), though cost and GaN efficiency at high power remain hurdles.

### #7 Solid-State 915 MHz Frequency-Agile Defroster

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition A (full graph), medium effort · run `A_M4_medium_r01`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 3,449 tokens per idea (run: 10,910 in + 6,334 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); F1 (Generates microwave energy at 2.45 GHz); X8 (Limited magnetron lifetime (cathode/filament wear)); X3 (Uneven heating — standing-wave hot and cold spots)
- **New elements:** Component: GaN solid-state RF amplifier array (915 MHz / 2.45 GHz, frequency-agile) — Replaces the magnetron with a solid-state amplifier that sweeps frequency to flatten standing-wave hot spots.; Technology: Gallium-nitride RF power amplification with frequency sweeping — Semiconductor amplifiers run at 915 MHz, which penetrates frozen food more deeply than 2.45 GHz, and sweep frequency to avoid fixed standing-wave nulls.; Function: Penetrates frozen blocks evenly from the core outward — Lower-frequency, swept RF thaws ice throughout the block instead of only at the surface.
- **New edges:** GaN solid-state RF amplifier array (915 MHz / 2.45 GHz, frequency-agile) -[resolves]-> C1; GaN solid-state RF amplifier array (915 MHz / 2.45 GHz, frequency-agile) -[performs_function]-> F1; GaN solid-state RF amplifier array (915 MHz / 2.45 GHz, frequency-agile) -[enabled_by]-> Gallium-nitride RF power amplification with frequency sweeping; Gallium-nitride RF power amplification with frequency sweeping -[partially_mitigates]-> X3; Penetrates frozen blocks evenly from the core outward -[addresses_need]-> M4; GaN solid-state RF amplifier array (915 MHz / 2.45 GHz, frequency-agile) -[enables_function]-> Penetrates frozen blocks evenly from the core outward
- **Rationale:** Lower-frequency, frequency-swept solid-state RF penetrates ice-cold centres and removes the hot-spot cold-spot problem that makes frozen meat thaw unevenly.
- **Judge:** Solid-state RF with frequency sweeping and 915 MHz penetration directly targets uneven thawing and is physically plausible, though costly and not really a cheaper substitution.

### #8 Solid-State 27 MHz Electrode Thaw

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), xhigh effort · run `B_M4_xhigh_r05`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 7,336 tokens per idea (run: 4,996 in + 31,684 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); C5 (Waveguide duct); C6 (Mica waveguide cover)
- **New elements:** Technology: Solid-state LDMOS/GaN RF amplification at 27.12 MHz — Low-voltage (about 50 V DC) transistor amplifier in the ISM band, with no cathode and no HV chain.; Technology: Quasi-static parallel-plate capacitive RF heating — Food forms the dielectric between two plates, and the field penetrates tens of cm into frozen blocks.; Component: 27 MHz RF amplifier module — Compact solid-state module replaces the magnetron, HV transformer, capacitor and diode.; Component: Dual RF electrode plates — Stamped steel shelf plates replace the waveguide duct and mica cover.; Function: Volumetric deep RF thaw of frozen blocks — Heats the whole block through its thickness, removing standing-wave hot and cold spots.
- **New edges:** 27 MHz RF amplifier module -[enabled_by]-> Solid-state LDMOS/GaN RF amplification at 27.12 MHz; Dual RF electrode plates -[enabled_by]-> Quasi-static parallel-plate capacitive RF heating; 27 MHz RF amplifier module -[performs_function]-> Volumetric deep RF thaw of frozen blocks; Dual RF electrode plates -[performs_function]-> Volumetric deep RF thaw of frozen blocks; Volumetric deep RF thaw of frozen blocks -[addresses_need]-> M4; Volumetric deep RF thaw of frozen blocks -[resolves]-> F16; 27 MHz RF amplifier module -[resolves]-> C1; 27 MHz RF amplifier module -[resolves]-> C2; 27 MHz RF amplifier module -[resolves]-> C3; 27 MHz RF amplifier module -[resolves]-> C4; Dual RF electrode plates -[resolves]-> C5; Dual RF electrode plates -[resolves]-> C6; Dual RF electrode plates -[partially_mitigates]-> X3; 27 MHz RF amplifier module -[partially_mitigates]-> X7; 27 MHz RF amplifier module -[partially_mitigates]-> X8
- **Rationale:** A low-frequency solid-state RF field penetrates thick frozen blocks volumetrically and evenly, aiming for a faster and safer thaw than surface-limited 2.45 GHz duty-cycling while removing the HV chain and waveguide.
- **Judge:** RF defrosting at 27 MHz is real and proven (RF thawing equipment exists), and solid-state RF is plausible, though runaway heating of thawed regions and scaling to a consumer appliance remain challenges.

### #9 Magnetron-free 27 MHz capacitive thaw

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition A (full graph), xhigh effort · run `A_M4_xhigh_r04`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 9,153 tokens per idea (run: 10,910 in + 34,857 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); C5 (Waveguide duct)
- **New elements:** Technology: 27.12 MHz capacitive RF thawing — Frozen load sits between electrode plates; the roughly 11 m wavelength gives no standing-wave hot spots and deep, uniform penetration.; Component: Solid-state 27 MHz RF generator — A low-voltage LDMOS or GaN oscillator with a matching network replaces the magnetron, HV transformer, capacitor and diode stack.; Component: Insulated RF electrode plate pair — Top and bottom plates inside the cavity, with the grounded cavity walls acting as the return path.; Function: Uniform through-thickness thawing of frozen blocks — Capacitive RF loss heats low-loss frozen food evenly from core to surface without rotation.
- **New edges:** 27.12 MHz capacitive RF thawing -[rooted_in]-> D1; 27.12 MHz capacitive RF thawing -[rooted_in]-> D3; Solid-state 27 MHz RF generator -[enabled_by]-> 27.12 MHz capacitive RF thawing; Insulated RF electrode plate pair -[enabled_by]-> 27.12 MHz capacitive RF thawing; Solid-state 27 MHz RF generator -[resolves]-> C1; Solid-state 27 MHz RF generator -[resolves]-> C2; Solid-state 27 MHz RF generator -[resolves]-> C3; Solid-state 27 MHz RF generator -[resolves]-> C4; Insulated RF electrode plate pair -[resolves]-> C5; Solid-state 27 MHz RF generator -[resolves]-> X7; Solid-state 27 MHz RF generator -[resolves]-> X8; Insulated RF electrode plate pair -[performs_function]-> Uniform through-thickness thawing of frozen blocks; Uniform through-thickness thawing of frozen blocks -[addresses_need]-> M4; Uniform through-thickness thawing of frozen blocks -[resolves]-> X3; Uniform through-thickness thawing of frozen blocks -[resolves]-> F4
- **Rationale:** Capacitive 27 MHz heating thaws frozen blocks through their full thickness with no standing-wave hot spots, so the core thaws as fast as the edges.
- **Judge:** RF thawing at 27 MHz is real and proven in industrial tempering, and it directly addresses uniform fast defrost; the main challenges are electrode design and cost for consumer scale.

### #10 Solid-State Cooking Array (no magnetron, no high voltage)

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition R (random slice), high effort · run `R_M7_high_r02`
- **Target need:** M7 — Safe for family use (radiation, burns, electric shock)
- **Cost:** 2,398 tokens per idea (run: 3,801 in + 8,191 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); T3 (Half-wave voltage doubler (capacitor + diode)); X7 (HV capacitor can hold a lethal charge after unplugging)
- **New elements:** Technology: GaN solid-state 2.45 GHz RF amplifier array — Low-voltage transistor power amplifiers whose outputs are phase-combined into the cavity, with no vacuum tube and no kV supply.; Component: Solid-state RF amplifier module array — Dozens of 20-50 W modules on a 48 V DC bus radiate through patch antennas in the cavity walls, replacing the magnetron and HV doubler.; Function: Generates 2.45 GHz heating field at touch-safe voltage — Removes the lethal HV rail, so there is no charged capacitor to hold energy after unplugging.
- **New edges:** Solid-state RF amplifier module array -[resolves]-> C1; Solid-state RF amplifier module array -[enabled_by]-> GaN solid-state 2.45 GHz RF amplifier array; GaN solid-state 2.45 GHz RF amplifier array -[rooted_in]-> D3; Solid-state RF amplifier module array -[performs_function]-> Generates 2.45 GHz heating field at touch-safe voltage; Generates 2.45 GHz heating field at touch-safe voltage -[addresses_need]-> M7; Solid-state RF amplifier module array -[partially_mitigates]-> X7
- **Rationale:** Eliminating the kV supply and stored high-voltage charge removes the electric-shock hazard at its source, so the appliance is safe to open or unplug.
- **Judge:** Solid-state RF cooking is real and removes the kV hazard and stored charge, though cost and efficiency remain hurdles.

## Bottom 10

| Rank | Idea | Score | Rel | Nov | Feas | Spec | Condition | Effort | Need | Tokens / idea |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2892 | Lens-Free Glass Dome Replacing Lamp and Door Window | 1.67 | 1 | 2 | 2 | None | B (need slice) | low | M4 | 1,541 |
| 2891 | Low-Voltage Switch-Mode Supply: Lethal HV Stage Removed | 2.00 | 1 | 2 | 2 | 3 | B (need slice) | high | M4 | 3,069 |
| 2890 | Transparent Glass Cavity Window Lamp-Free Vision | 2.00 | 1 | 2 | 3 | 2 | A (full graph) | low | M12 | 2,666 |
| 2889 | Direct-Coupled Magnetron Pod (No Waveguide Duct) | 2.25 | 2 | 1 | 3 | 3 | B (need slice) | high | M4 | 3,052 |
| 2888 | Capacitor-Free 48 V Bus Power Stage | 2.25 | 1 | 2 | 3 | 3 | B (need slice) | medium | M4 | 1,920 |
| 2887 | GaN Universal-Mains Power Stage Replaces HV Transformer Stack | 2.25 | 1 | 2 | 3 | 3 | B (need slice) | low | M12 | 1,709 |
| 2886 | Ghost Lamp Vision: Replace the Interior Lamp With Microwave-Transparent Transparent Walls | 2.25 | 1 | 2 | 3 | 3 | B (need slice) | low | M12 | 1,425 |
| 2885 | Transparent Conductive-Film Door Replacing Mesh Window | 2.25 | 2 | 2 | 2 | 3 | B (need slice) | low | M6 | 1,113 |
| 2884 | Ferrite-Free Clockwork Nutrient Timer | 2.25 | 1 | 3 | 2 | 3 | B (need slice) | low | M12 | 1,449 |
| 2883 | Stored-Energy Cordless Capacitor Pack | 2.25 | 1 | 3 | 2 | 3 | B (need slice) | low | M5 | 1,487 |

### #2892 Lens-Free Glass Dome Replacing Lamp and Door Window

- **Score:** 1.67 (relevance 1, novelty 2, feasibility 2, specificity None)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M4_low_r02`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,541 tokens per idea (run: 4,996 in + 2,709 out, 5 ideas)
- **Applied to:** C6 (Mica waveguide cover); F3 (Guides microwave energy into the cavity); F5 (Distributes heat evenly by rotating food through the field)
- **New elements:** Technology: Phase-change smart glass with RF shielding — Electrochromic glass that stays clear for viewing, but also blocks radiation leakage.; Component: Electrochromic door panel — A fully transparent door that replaces the mica cover and the viewing window so the user can see the food at any time.; Function: Lets the user monitor defrost progress without opening the door — Removes the need to open the door for checks, keeping RF energy contained and speeding defrost.
- **New edges:** Electrochromic door panel -[enabled_by]-> Phase-change smart glass with RF shielding; Electrochromic door panel -[performs_function]-> Lets the user monitor defrost progress without opening the door; Lets the user monitor defrost progress without opening the door -[enables_function]-> F16; Electrochromic door panel -[resolves]-> C6
- **Rationale:** Continuous visibility without opening the door keeps the cavity sealed and lets parents track thawing, directly supporting faster, safer defrosting for M4.
- **Judge:** Visibility through the door does not speed defrosting, and the claim that it speeds the process is false, so it barely serves M4.

### #2891 Low-Voltage Switch-Mode Supply: Lethal HV Stage Removed

- **Score:** 2.00 (relevance 1, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r05`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 3,069 tokens per idea (run: 4,996 in + 10,351 out, 5 ideas)
- **Applied to:** C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); X7 (HV capacitor can hold a lethal charge after unplugging); A5 (Parent with young children)
- **New elements:** Component: Switch-mode low-voltage power stage (48 V class) — A GaN or Si switching converter replaces the transformer, capacitor and diode with a small low-voltage stage.; Technology: High-frequency switch-mode power conversion — Converts mains to low-voltage DC at tens of kHz, so magnetics are tiny and no lethal stored charge remains.; Function: Enables unattended, child-safe defrost cycles — No lethal capacitor and no high-voltage transformer, so the appliance is safe to leave running and safe to open or unplug.
- **New edges:** P1 -[has_component]-> Switch-mode low-voltage power stage (48 V class); Switch-mode low-voltage power stage (48 V class) -[enabled_by]-> High-frequency switch-mode power conversion; High-frequency switch-mode power conversion -[rooted_in]-> D3; Switch-mode low-voltage power stage (48 V class) -[performs_function]-> F2; Enables unattended, child-safe defrost cycles -[enables_function]-> F16; Enables unattended, child-safe defrost cycles -[addresses_need]-> M4; Enables unattended, child-safe defrost cycles -[relevant_to]-> A5; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C2; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C3; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C4; Switch-mode low-voltage power stage (48 V class) -[partially_mitigates]-> X7
- **Rationale:** A parent with young children can start a defrost cycle and walk away, because the lethal high-voltage stage that makes the appliance hazardous to open or leave running is gone.
- **Judge:** Safety is the benefit, not defrost speed, and a 48 V supply cannot drive a magnetron or deliver the needed RF power.

### #2890 Transparent Glass Cavity Window Lamp-Free Vision

- **Score:** 2.00 (relevance 1, novelty 2, feasibility 3, specificity 2)
- **Made by:** claude-haiku-5-5, condition A (full graph), low effort · run `A_M12_low_r02`
- **Target need:** M12 — Healthy diet (nutrient retention, less fat)
- **Cost:** 2,666 tokens per idea (run: 10,917 in + 2,412 out, 5 ideas)
- **Applied to:** C17 (Interior lamp (20-25 W incandescent)); C8 (Hinged door with perforated metal mesh window); X14 (Interior lamp burns out and is hard to replace); F11 (Illuminates cavity so the user can watch the food)
- **New elements:** Technology: Electrochromic door glass with ITO conductive layer — Transparent conductive coating on the door window lets the user see inside without a bulb, and it blocks RF through the sub-wavelength pattern.; Function: Shows food state at a glance without a lamp — Replaces the incandescent lamp, so users can check cooking progress and avoid opening the door, which keeps heat and nutrients inside.
- **New edges:** Electrochromic door glass with ITO conductive layer -[enabled_by]-> C17; Electrochromic door glass with ITO conductive layer -[partially_mitigates]-> X14; Shows food state at a glance without a lamp -[addresses_need]-> M8; Shows food state at a glance without a lamp -[addresses_need]-> M12
- **Rationale:** Viewing without opening the door keeps cavity heat and steam in, so food cooks with less nutrient loss and less reliance on overcooking, serving M12.
- **Judge:** Door windows already have RF-blocking mesh, and the nutrient benefit is tenuous; the electrochromic and ITO description is muddled.

### #2889 Direct-Coupled Magnetron Pod (No Waveguide Duct)

- **Score:** 2.25 (relevance 2, novelty 1, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r02`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 3,052 tokens per idea (run: 4,996 in + 10,265 out, 5 ideas)
- **Applied to:** C5 (Waveguide duct); C6 (Mica waveguide cover)
- **New elements:** Component: Antenna-coupled magnetron pod — Magnetron antenna radiates straight into the cavity from a short mounted pod, with no duct.; Technology: Coaxial / slot-antenna direct radiation — Energy leaves the source through a short, low-loss aperture instead of a long metal duct.; Function: Delivers most of the magnetron output into the food — Shorter path means less reflection loss, so more of the 700 W reaches the load.
- **New edges:** Antenna-coupled magnetron pod -[enabled_by]-> Coaxial / slot-antenna direct radiation; Coaxial / slot-antenna direct radiation -[rooted_in]-> D1; Antenna-coupled magnetron pod -[performs_function]-> Delivers most of the magnetron output into the food; Antenna-coupled magnetron pod -[resolves]-> C5; Antenna-coupled magnetron pod -[feeds]-> C7; Delivers most of the magnetron output into the food -[resolves]-> F3; Delivers most of the magnetron output into the food -[addresses_need]-> M4
- **Rationale:** Removing the duct and its losses lets more of the magnetron's output go into the frozen food, which shortens the thaw time.
- **Judge:** Removing the waveguide is an incremental tweak, and the claimed efficiency gain is dubious since the duct loss is small and coupling affects field uniformity.

### #2888 Capacitor-Free 48 V Bus Power Stage

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), medium effort · run `B_M4_medium_r03`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,920 tokens per idea (run: 4,996 in + 4,606 out, 5 ideas)
- **Applied to:** C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); X7 (HV capacitor can hold a lethal charge after unplugging); X15 (Regional mains variants (230 V/50 Hz vs 120 V/60 Hz))
- **New elements:** Component: Low-voltage GaN switching supply with 48 V DC bus — A high-frequency switch-mode supply, fed from a 48 V rail, replaces the transformer, capacitor and diode chain.; Technology: High-frequency switch-mode power conversion — Small ferrite transformers and GaN switches step the voltage up to the RF stage efficiently at kilohertz to megahertz rates.; Function: Delivers magnetron-free energy at any mains voltage — A universal input stage converts 120 V or 230 V mains to the internal bus, which removes the regional variant problem.
- **New edges:** Low-voltage GaN switching supply with 48 V DC bus -[resolves]-> C2; Low-voltage GaN switching supply with 48 V DC bus -[resolves]-> C3; Low-voltage GaN switching supply with 48 V DC bus -[resolves]-> C4; High-frequency switch-mode power conversion -[enabled_by]-> Low-voltage GaN switching supply with 48 V DC bus; High-frequency switch-mode power conversion -[partially_mitigates]-> X7; Delivers magnetron-free energy at any mains voltage -[partially_mitigates]-> X15; Delivers magnetron-free energy at any mains voltage -[performs_function]-> F2
- **Rationale:** Removing the kilovolt capacitor and transformer makes the oven safe and globally portable, so it can be plugged in and used to thaw food anywhere.
- **Judge:** This is a power-supply swap with little bearing on defrost speed, and it only makes sense alongside a solid-state RF source.

### #2887 GaN Universal-Mains Power Stage Replaces HV Transformer Stack

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M12_low_r05`
- **Target need:** M12 — Healthy diet (nutrient retention, less fat)
- **Cost:** 1,709 tokens per idea (run: 4,639 in + 3,908 out, 5 ideas)
- **Applied to:** C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); X7 (HV capacitor can hold a lethal charge after unplugging); X15 (Regional mains variants (230 V/50 Hz vs 120 V/60 Hz))
- **New elements:** Component: GaN switch-mode power supply with low-voltage DC link — High-frequency switching converter that replaces the transformer, capacitor and diode stack and runs on any mains voltage.; Function: Universal 100-240 V operation with no lethal stored charge — Low-energy DC link discharges in milliseconds, removing the lethal-charge hazard.; Technology: High-frequency GaN switching power conversion — Wide-bandgap transistors switching at hundreds of kHz to produce the magnetron supply voltage.
- **New edges:** GaN switch-mode power supply with low-voltage DC link -[resolves]-> C2; GaN switch-mode power supply with low-voltage DC link -[resolves]-> C3; Universal 100-240 V operation with no lethal stored charge -[resolves]-> X7; Universal 100-240 V operation with no lethal stored charge -[partially_mitigates]-> X15; High-frequency GaN switching power conversion -[enabled_by]-> GaN switch-mode power supply with low-voltage DC link
- **Rationale:** Simplifying the power stage makes the appliance cheaper and easier to sell in every market, which lets healthy-cooking features reach more families.
- **Judge:** Inverter power stages already exist in microwaves, and this idea mainly lowers cost and offers only a tenuous link to healthy eating.

### #2886 Ghost Lamp Vision: Replace the Interior Lamp With Microwave-Transparent Transparent Walls

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M12_low_r03`
- **Target need:** M12 — Healthy diet (nutrient retention, less fat)
- **Cost:** 1,425 tokens per idea (run: 4,639 in + 2,486 out, 5 ideas)
- **Applied to:** C7 (Enamelled steel cooking cavity (~20 L)); F4 (Heats food via dielectric water-molecule vibration (FastHeating))
- **New elements:** Technology: Indium-tin-oxide transparent conductive window — Thin, transparent conductive coating on the door that blocks microwaves while letting light through, so food can be watched without an internal lamp.; Component: Door-window ITO mesh — Fine conductive mesh laminated into the door glass, shielding the cavity and passing visible light.
- **New edges:** Door-window ITO mesh -[enabled_by]-> Indium-tin-oxide transparent conductive window; Door-window ITO mesh -[resolves]-> Indium-tin-oxide transparent conductive window; Door-window ITO mesh -[relevant_to]-> A5; Door-window ITO mesh -[relevant_to]-> M12
- **Rationale:** Lets parents watch food brown and steam without opening the door, reducing heat loss and encouraging them to check that vegetables are cooked gently rather than overcooked.
- **Judge:** Microwave doors already have mesh viewing windows, and this has only a tenuous link to healthy diet.

### #2885 Transparent Conductive-Film Door Replacing Mesh Window

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M6_low_r02`
- **Target need:** M6 — Simple operation with no learning curve
- **Cost:** 1,113 tokens per idea (run: 2,915 in + 2,652 out, 5 ideas)
- **Applied to:** C8 (Hinged door with perforated metal mesh window); T5 (Sub-wavelength aperture shielding (Faraday cage effect))
- **New elements:** Technology: Indium-tin-oxide coated glass viewing panel — A transparent conductive coating on glass reflects microwaves while passing visible light, with no mesh holes.; Component: Full-glass door panel — Wide clear door panel that shows the whole cavity and food without a perforated frame.; Function: Shows cavity contents across the whole door — Makes the food visible from any angle, so the user doesn't need to crouch or search for a view.
- **New edges:** Indium-tin-oxide coated glass viewing panel -[resolves]-> T5; Full-glass door panel -[resolves]-> C8; Full-glass door panel -[performs_function]-> Shows cavity contents across the whole door; Shows cavity contents across the whole door -[addresses_need]-> M6; Full-glass door panel -[partially_mitigates]-> X2
- **Rationale:** A clear, edge-to-edge window lets users see the food at a glance, which removes the need to learn where to look or how to check progress.
- **Judge:** Better visibility helps only marginally with simple operation, and ITO coatings face problems with microwave shielding, durability and cost, so the mesh is not truly replaced.

### #2884 Ferrite-Free Clockwork Nutrient Timer

- **Score:** 2.25 (relevance 1, novelty 3, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M12_low_r04`
- **Target need:** M12 — Healthy diet (nutrient retention, less fat)
- **Cost:** 1,449 tokens per idea (run: 4,639 in + 2,606 out, 5 ideas)
- **Applied to:** C12 (Turntable motor (~5 rpm)); C10 (Rotating glass turntable tray); F5 (Distributes heat evenly by rotating food through the field); C11 (Roller ring and coupler (turntable support))
- **New elements:** Technology: Piezo-resonant rotation sensing — Replaces the rotating tray motor and roller ring with a vibration-driven spinner that uses less energy and fewer moving parts.; Function: Even heating with less energy waste — Rotates food evenly so it cooks through without long re-heats that degrade nutrients.; Component: Vibrating base plate spinner — Vibrates the tray base to rotate it, removing the motor, coupler and roller ring.
- **New edges:** Vibrating base plate spinner -[performs_function]-> Even heating with less energy waste; Even heating with less energy waste -[addresses_need]-> M12; Piezo-resonant rotation sensing -[enabled_by]-> Vibrating base plate spinner; Vibrating base plate spinner -[relevant_to]-> C12
- **Rationale:** Even, shorter cooking cycles preserve heat-sensitive nutrients, and a simpler spinner reduces cost so healthier cooking reaches more households.
- **Judge:** A piezo-vibration spinner replacing the turntable motor is an interesting substitution, but it barely serves the healthy-diet need and may not move heavy loads.

### #2883 Stored-Energy Cordless Capacitor Pack

- **Score:** 2.25 (relevance 1, novelty 3, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M5_low_r04`
- **Target need:** M5 — Save time in the kitchen
- **Cost:** 1,487 tokens per idea (run: 4,996 in + 2,438 out, 5 ideas)
- **Applied to:** C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C2 (High-voltage transformer); X7 (HV capacitor can hold a lethal charge after unplugging); F2 (Converts mains voltage to ~4 kV DC for the magnetron)
- **New elements:** Technology: Super-capacitor / Li-ion pulse bank — Stores energy at low voltage and boosts it through a DC-DC converter to RF supply levels.; Component: Low-voltage DC-DC RF supply — Replaces the 2 kV mains transformer and voltage doubler.
- **New edges:** Low-voltage DC-DC RF supply -[resolves]-> C2; Low-voltage DC-DC RF supply -[resolves]-> C3; Low-voltage DC-DC RF supply -[performs_function]-> F2; Super-capacitor / Li-ion pulse bank -[partially_mitigates]-> X7; Super-capacitor / Li-ion pulse bank -[addresses_need]-> M5
- **Rationale:** A battery-backed, low-voltage supply can be plugged in and used at once, and it removes the lethal HV capacitor, so the appliance is quicker to start and safer to handle.
- **Judge:** A battery-backed low-voltage supply barely addresses saving time, and delivering kilowatt-level pulses from capacitors is impractical and costly.
