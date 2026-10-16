# Top 10 and bottom 10 ideas

2625 ideas scored individually and blind by `claude-sonnet-5-5` on relevance, novelty, feasibility, specificity (1–5). Score = mean of the four criteria. Cost per idea = the generating call's total tokens divided by its number of ideas.

## Who made them

| Arm | In top | In bottom |
| --- | --- | --- |
| engineer, B (need slice), high effort | 2 | 2 |
| engineer, B (need slice), medium effort | 0 | 1 |
| engineer, C (no graph), high effort | 1 | 0 |
| lateral, B (need slice), high effort | 1 | 0 |
| lateral, B (need slice), medium effort | 0 | 3 |
| lateral, C (no graph), medium effort | 0 | 2 |
| patent, B (need slice), high effort | 2 | 0 |
| patent, B (need slice), medium effort | 1 | 1 |
| patent, C (no graph), high effort | 2 | 0 |
| patent, C (no graph), medium effort | 1 | 1 |

## Top 10

| Rank | Idea | Score | Rel | Nov | Feas | Spec | Condition | Effort | Need | Tokens / idea |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Solid-State Heart: GaN Amplifier Replaces Magnetron and HV Chain | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M13 | 2,801 |
| 2 | 27 MHz RF Thaw Plates | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M4 | 2,115 |
| 3 | RF Plate Defrost | 4.50 | 5 | 4 | 4 | 5 | C (no graph) | high | M4 | 2,844 |
| 4 | Solid-state RF tempering plates | 4.50 | 5 | 4 | 4 | 5 | C (no graph) | high | M4 | 2,325 |
| 5 | Solid-state frequency-agile RF defrost head | 4.50 | 5 | 4 | 4 | 5 | C (no graph) | medium | M4 | 1,211 |
| 6 | Thermal doneness map replaces the interior lamp | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | medium | M8 | 1,803 |
| 7 | Doneness Colour Halo | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M8 | 2,424 |
| 8 | Thermal-IR Window: Seeing Food Heat Instead of Light | 4.50 | 5 | 4 | 4 | 5 | C (no graph) | high | M8 | 1,653 |
| 9 | Solid-State Cooking: No Magnetron, No 4 kV | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M13 | 3,309 |
| 10 | 27 MHz capacitive RF thaw replacing the 2.45 GHz magnetron | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M4 | 4,965 |

### #1 Solid-State Heart: GaN Amplifier Replaces Magnetron and HV Chain

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M13_high_r03`
- **Target need:** M13 — Energy efficiency
- **Cost:** 2,801 tokens per idea (run: 4,520 in + 9,484 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode)
- **New elements:** Component: GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) — Low-voltage transistor power amplifier replaces the magnetron and its 4 kV transformer-doubler chain; no cathode to wear and no lethal HV.; Technology: Gallium nitride HEMT power amplifier — Wide-bandgap transistors reach high DC-to-RF efficiency at 2.45 GHz and allow precise, proportional power control.; Component: 50 V switch-mode PSU — Compact high-frequency SMPS replaces the bulky 50 Hz HV transformer and voltage doubler, so mains-frequency losses disappear.
- **New edges:** GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C1; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C2; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C3; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C4; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[performs_function]-> F1; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[enabled_by]-> Gallium nitride HEMT power amplifier; 50 V switch-mode PSU -[performs_function]-> F2; 50 V switch-mode PSU -[feeds]-> GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail); GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[partially_mitigates]-> X8; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[partially_mitigates]-> X7; F1 -[addresses_need]-> M13
- **Rationale:** Solid-state RF generation with a low-voltage supply removes the magnetron's heat-and-conversion losses and gives proportional power, so less electricity is wasted per cooked meal.
- **Judge:** Solid-state RF replacing the magnetron is a real, directly efficiency-relevant substitution (GaN ovens exist), though cost is high and efficiency gains are moderate.

### #2 27 MHz RF Thaw Plates

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r03`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 2,115 tokens per idea (run: 4,996 in + 5,581 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C5 (Waveguide duct); F1 (Generates microwave energy at 2.45 GHz); F3 (Guides microwave energy into the cavity)
- **New elements:** Technology: Solid-state RF amplifier at 27 MHz (LDMOS/GaN) — Low-cost transistor power stage replaces the vacuum magnetron, with no cathode to wear out.; Component: Parallel-plate RF electrode pair — Food sits between two insulated plates, so the field penetrates the full thickness of a frozen block.; Function: Volumetric thaw of ice through full thickness — Longer RF wavelength heats the interior of a frozen block evenly instead of only the surface.
- **New edges:** Solid-state RF amplifier at 27 MHz (LDMOS/GaN) -[resolves]-> C1; Parallel-plate RF electrode pair -[resolves]-> C5; Parallel-plate RF electrode pair -[performs_function]-> Volumetric thaw of ice through full thickness; Volumetric thaw of ice through full thickness -[addresses_need]-> M4; Solid-state RF amplifier at 27 MHz (LDMOS/GaN) -[partially_mitigates]-> X8
- **Rationale:** Lower-frequency RF penetrates frozen blocks deeply and uniformly, so the thaw is faster and more even than surface-first 2.45 GHz heating.
- **Judge:** RF thawing at 27 MHz is real and effective for frozen blocks, and solid-state RF replacing the magnetron fits the SUBSTITUTE operator, though cost and shielding remain challenges.

### #3 RF Plate Defrost

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition C (no graph), high effort · run `C_M4_high_r02`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 2,844 tokens per idea (run: 1,050 in + 13,168 out, 5 ideas)
- **Applied to:** M4 (Defrost frozen food quickly)
- **New elements:** Component: 2.45 GHz magnetron — Current heat source; couples weakly to ice, so thawing starts slowly and then runs away on liquid pockets.; Component: 27 MHz RF solid-state oscillator — Low-cost GaN generator at 27.12 MHz that replaces the magnetron as the energy source.; Component: Parallel RF electrode plates — Metal plates on either side of the food, so the field penetrates ice evenly through its full thickness.; Technology: GaN solid-state RF amplification — Cool-running, precisely tunable RF power from inexpensive semiconductors.; Field: Industrial RF dielectric heating — Physics already used in factory RF thawing lines, shrunk to a countertop.; Function: Volumetric uniform thawing — Heats the core and rim together, avoiding a cooked outside with a frozen centre.; Constraint: Ice absorbs little 2.45 GHz energy — Microwave-frequency thawing is slow at first and uneven throughout.
- **New edges:** 27 MHz RF solid-state oscillator -[resolves]-> 2.45 GHz magnetron; 2.45 GHz magnetron -[causes]-> Ice absorbs little 2.45 GHz energy; Parallel RF electrode plates -[partially_mitigates]-> Ice absorbs little 2.45 GHz energy; 27 MHz RF solid-state oscillator -[feeds]-> Parallel RF electrode plates; 27 MHz RF solid-state oscillator -[enabled_by]-> GaN solid-state RF amplification; GaN solid-state RF amplification -[rooted_in]-> Industrial RF dielectric heating; Parallel RF electrode plates -[performs_function]-> Volumetric uniform thawing; Volumetric uniform thawing -[addresses_need]-> M4
- **Rationale:** Replacing the microwave source with RF electrodes lets the field penetrate ice evenly, so frozen food thaws faster and without cooked edges.
- **Judge:** RF defrosting at 27 MHz is real and proven (e.g., NXP, Whirlpool/Miele prototypes), directly addresses fast and even thawing, though it is less novel since it exists in industry and thermal runaway remains a challenge.

### #4 Solid-state RF tempering plates

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition C (no graph), high effort · run `patent_C_M4_high_r14`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 2,325 tokens per idea (run: 1,194 in + 10,429 out, 5 ideas)
- **Applied to:** base:magnetron (not in graph); base:glass_turntable (not in graph); base:waveguide (not in graph)
- **New elements:** Technology: RF dielectric tempering at 27.12 MHz — Volumetric heating of food placed between electrodes using the ISM-band RF field, which penetrates thick blocks without rotation.; Component: Solid-state RF amplifier — GaN power amplifier with an L-network match, replacing the magnetron and waveguide.; Component: Parallel-plate electrode pair — Two flat electrodes above and below the food, replacing the glass turntable as the heating field source.; Function: Volumetric uniform thawing — Heat is generated throughout the food's volume rather than only at its surface, so the core thaws with the edges.
- **New edges:** Solid-state RF amplifier -[feeds]-> Parallel-plate electrode pair; RF dielectric tempering at 27.12 MHz -[enabled_by]-> Solid-state RF amplifier; Solid-state RF amplifier -[performs_function]-> Volumetric uniform thawing; Volumetric uniform thawing -[addresses_need]-> M4; Solid-state RF amplifier -[resolves]-> base:magnetron; Parallel-plate electrode pair -[resolves]-> base:glass_turntable
- **Rationale:** Volumetric RF heating thaws thick frozen blocks evenly and removes the slow edge-first melting that currently stalls M4.
- **Judge:** RF tempering at 27.12 MHz is real, proven in industry, and directly improves thawing uniformity, though a consumer-cost GaN amplifier and electrode system is challenging.

### #5 Solid-state frequency-agile RF defrost head

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition C (no graph), medium effort · run `patent_C_M4_medium_r15`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,211 tokens per idea (run: 1,194 in + 4,863 out, 5 ideas)
- **Applied to:** M4 (Defrost frozen food quickly)
- **New elements:** Component: GaN solid-state RF amplifier array — Replaces the fixed 2.45 GHz magnetron with phase-controlled GaN amplifiers that sweep frequency and power across the ISM band to match the dielectric loss of ice versus water.; Technology: Gallium nitride power semiconductors — Wideband, high-efficiency RF power generation without a vacuum tube or high-voltage filament.; Function: Frequency-agile dielectric heating — Couples energy into ice and water fractions selectively, reducing hot spots and thawing time.; Field: RF and microwave engineering — Field in which the solid-state amplifier and sweep control are rooted.
- **New edges:** GaN solid-state RF amplifier array -[resolves]-> Magnetron; GaN solid-state RF amplifier array -[performs_function]-> Frequency-agile dielectric heating; Gallium nitride power semiconductors -[enabled_by]-> GaN solid-state RF amplifier array; Gallium nitride power semiconductors -[rooted_in]-> RF and microwave engineering; Frequency-agile dielectric heating -[addresses_need]-> M4
- **Rationale:** Selective, swept-frequency coupling into ice rather than water fractions shortens defrost time while avoiding the cooked-edge and hot-spot failure of single-frequency heating.
- **Judge:** Solid-state RF with frequency and phase control is real, being commercialized, and directly targets uneven defrost, though the claim of selectively coupling into ice is overstated and cost is high.

### #6 Thermal doneness map replaces the interior lamp

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), medium effort · run `patent_B_M8_medium_r06`
- **Target need:** M8 — Human need for feedback (know when food is ready)
- **Cost:** 1,803 tokens per idea (run: 2,857 in + 6,160 out, 5 ideas)
- **Applied to:** C17 (Interior lamp (20-25 W incandescent)); C8 (Hinged door with perforated metal mesh window); F11 (Illuminates cavity so the user can watch the food); X14 (Interior lamp burns out and is hard to replace)
- **New elements:** Component: 8x8 infrared thermopile array behind door mesh — Low-cost IR sensor array reads surface temperature of food through the mesh and drives a colour-coded doneness map on the door display.; Technology: Infrared thermopile sensing — Thermopile detects emitted infrared, which passes through the perforated mesh because the holes are much larger than IR wavelengths.; Field: Thermal sensing — Infrared detection and thermal imaging.; Function: Shows surface temperature map of food — Converts invisible heat distribution into a visible cold-spot and hot-spot display for the user.
- **New edges:** 8x8 infrared thermopile array behind door mesh -[resolves]-> C17; 8x8 infrared thermopile array behind door mesh -[enabled_by]-> Infrared thermopile sensing; Infrared thermopile sensing -[rooted_in]-> Thermal sensing; 8x8 infrared thermopile array behind door mesh -[performs_function]-> Shows surface temperature map of food; Shows surface temperature map of food -[addresses_need]-> M8; 8x8 infrared thermopile array behind door mesh -[partially_mitigates]-> X14
- **Rationale:** It replaces the light that only shows whether food is visible with a sensor that shows whether food is actually hot enough, which directly answers the user's need to know when food is ready.
- **Judge:** An IR thermopile array viewing food through the door mesh gives direct, visual doneness feedback and is plausible with existing low-cost sensors, though it reads only surface temperature.

### #7 Doneness Colour Halo

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `patent_B_M8_high_r06`
- **Target need:** M8 — Human need for feedback (know when food is ready)
- **Cost:** 2,424 tokens per idea (run: 2,857 in + 9,262 out, 5 ideas)
- **Applied to:** C17 (Interior lamp (20-25 W incandescent)); C22 (End-of-cycle bell (mechanical 'ding')); F11 (Illuminates cavity so the user can watch the food); F12 (Signals end of cooking (audible alert))
- **New elements:** Technology: Addressable RGB LED colour gradient — Long-life solid-state LEDs whose colour is set continuously by a driver chip, replacing an incandescent filament.; Component: Door-frame RGB LED light bar — A ring of LEDs around the door frame that shifts colour from cold blue to ready green.; Component: IR thermopile spot sensor aimed at the food — Low-cost non-contact sensor reads the surface temperature of the food and feeds the colour driver.; Function: Shows doneness as a colour gradient visible from across the room — Silent, ambient readiness feedback that works without a sound alert.
- **New edges:** Door-frame RGB LED light bar -[resolves]-> C17; Door-frame RGB LED light bar -[enabled_by]-> Addressable RGB LED colour gradient; Addressable RGB LED colour gradient -[rooted_in]-> D7; Door-frame RGB LED light bar -[performs_function]-> Shows doneness as a colour gradient visible from across the room; IR thermopile spot sensor aimed at the food -[feeds]-> Door-frame RGB LED light bar; Shows doneness as a colour gradient visible from across the room -[partially_mitigates]-> F12; Shows doneness as a colour gradient visible from across the room -[enables_function]-> F11; Door-frame RGB LED light bar -[partially_mitigates]-> X14; Shows doneness as a colour gradient visible from across the room -[addresses_need]-> M8
- **Rationale:** -
- **Judge:** An ambient colour gradient from a thermopile reading gives continuous, glanceable readiness feedback that directly serves the need, using cheap solid-state parts.

### #8 Thermal-IR Window: Seeing Food Heat Instead of Light

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition C (no graph), high effort · run `patent_C_M8_high_r10`
- **Target need:** M8 — Human need for feedback (know when food is ready)
- **Cost:** 1,653 tokens per idea (run: 1,202 in + 7,062 out, 5 ideas)
- **Applied to:** 20-25 W interior incandescent lamp (not in graph); M8 (Human need for feedback (know when food is ready))
- **New elements:** Technology: Passive thermal infrared sensing — Detects emitted infrared radiation from surfaces, so it needs no visible light and no illumination.; Component: 8x8 thermopile IR sensor array in cavity roof — Low-power array (about 0.1 W) that maps food surface temperature, replacing the 20-25 W lamp as the means of seeing inside.; Function: Surface temperature mapping of food — Produces a live heat map of the food so the user sees which zones are hot or cold.; Function: Cold-spot detection — Flags unevenly heated zones that show the food is not yet ready in the centre.
- **New edges:** 8x8 thermopile IR sensor array in cavity roof -[resolves]-> 20-25 W interior incandescent lamp; 8x8 thermopile IR sensor array in cavity roof -[enabled_by]-> Passive thermal infrared sensing; 8x8 thermopile IR sensor array in cavity roof -[performs_function]-> Surface temperature mapping of food; Surface temperature mapping of food -[enables_function]-> Cold-spot detection; Cold-spot detection -[addresses_need]-> M8; Surface temperature mapping of food -[addresses_need]-> M8
- **Rationale:** The user gets a direct, continuous readout of which parts of the food are actually ready, rather than inferring readiness from a glowing interior they must squint at.
- **Judge:** An IR array gives direct, spatial readiness feedback; it is plausible, though a thermopile array may need a microwave-safe window and its reading is limited to surface temperature.

### #9 Solid-State Cooking: No Magnetron, No 4 kV

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `lateral_B_M13_high_r15`
- **Target need:** M13 — Energy efficiency
- **Cost:** 3,309 tokens per idea (run: 4,673 in + 11,871 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); F1 (Generates microwave energy at 2.45 GHz); F2 (Converts mains voltage to ~4 kV DC for the magnetron)
- **New elements:** Component: Solid-state GaN RF amplifier array (2.45 GHz) — Low-voltage transistor power-amplifier modules replace the magnetron, HV transformer, capacitor and diode.; Technology: Gallium-nitride HEMT power amplification — Transistor RF gain runs from 12 to 48 V DC, so there is no thermionic cathode and no 4 kV rail.; Function: Generates 2.45 GHz RF from low-voltage DC — Delivers the same RF output as F1 without thermionic losses or high-voltage conversion.
- **New edges:** Solid-state GaN RF amplifier array (2.45 GHz) -[resolves]-> C1; Solid-state GaN RF amplifier array (2.45 GHz) -[resolves]-> C2; Solid-state GaN RF amplifier array (2.45 GHz) -[resolves]-> C3; Solid-state GaN RF amplifier array (2.45 GHz) -[resolves]-> C4; Solid-state GaN RF amplifier array (2.45 GHz) -[enabled_by]-> Gallium-nitride HEMT power amplification; Gallium-nitride HEMT power amplification -[rooted_in]-> D1; Solid-state GaN RF amplifier array (2.45 GHz) -[performs_function]-> Generates 2.45 GHz RF from low-voltage DC; Generates 2.45 GHz RF from low-voltage DC -[resolves]-> F1; Generates 2.45 GHz RF from low-voltage DC -[enables_function]-> F3; Generates 2.45 GHz RF from low-voltage DC -[addresses_need]-> M13; Solid-state GaN RF amplifier array (2.45 GHz) -[partially_mitigates]-> X8; Solid-state GaN RF amplifier array (2.45 GHz) -[partially_mitigates]-> X7
- **Rationale:** Removing the high-voltage conversion chain and the thermionic magnetron cuts conversion losses and standby waste while serving the same heating function at lower voltage.
- **Judge:** Solid-state RF replaces the magnetron and its high-voltage chain, which directly improves efficiency; the technology is real, though cost and efficiency parity are still being worked out.

### #10 27 MHz capacitive RF thaw replacing the 2.45 GHz magnetron

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `patent_B_M4_high_r09`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 4,965 tokens per idea (run: 5,140 in + 19,684 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C5 (Waveguide duct); C6 (Mica waveguide cover); F1 (Generates microwave energy at 2.45 GHz); F3 (Guides microwave energy into the cavity); T1 (Electron cyclotron motion in crossed E×B fields (cavity magnetron)); T4 (Rectangular waveguide TE10 mode propagation)
- **New elements:** Technology: 27.12 MHz capacitive RF dielectric heating — Electrodes on either side of the load drive displacement current through the food; the ~11 m wavelength gives a nearly uniform field across a frozen block, unlike the 12 cm wave at 2.45 GHz.; Component: Solid-state 27.12 MHz RF oscillator — LDMOS or GaN transistor oscillator running from a low-voltage DC rail; replaces the magnetron, filament and cathode, so there is no thermionic wear.; Component: Parallel-plate thaw electrode pair — Upper plate in the cavity ceiling and lower plate as a raised shelf, separated by ceramic spacers; replaces the waveguide and mica cover.; Function: Volumetric thawing by displacement-current heating — Heats the full thickness of a frozen block at once instead of from the surface inward.
- **New edges:** 27.12 MHz capacitive RF dielectric heating -[rooted_in]-> D1; Solid-state 27.12 MHz RF oscillator -[enabled_by]-> 27.12 MHz capacitive RF dielectric heating; Parallel-plate thaw electrode pair -[enabled_by]-> 27.12 MHz capacitive RF dielectric heating; Solid-state 27.12 MHz RF oscillator -[feeds]-> Parallel-plate thaw electrode pair; Parallel-plate thaw electrode pair -[performs_function]-> Volumetric thawing by displacement-current heating; Volumetric thawing by displacement-current heating -[addresses_need]-> M4; Solid-state 27.12 MHz RF oscillator -[resolves]-> C1; Parallel-plate thaw electrode pair -[resolves]-> C5; Parallel-plate thaw electrode pair -[resolves]-> C6; Parallel-plate thaw electrode pair -[partially_mitigates]-> X3; Solid-state 27.12 MHz RF oscillator -[partially_mitigates]-> X8
- **Rationale:** Volumetric RF heating at 27 MHz thaws the whole block at once with fewer hot and cold spots, so frozen food defrosts faster and more evenly than surface-first 2.45 GHz heating.
- **Judge:** RF thawing at 27 MHz is a real, proven technology for tempering frozen blocks with better uniformity, and solid-state RF is plausible, though it is costly and risks arcing and runaway heating.

## Bottom 10

| Rank | Idea | Score | Rel | Nov | Feas | Spec | Condition | Effort | Need | Tokens / idea |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2625 | Low-Voltage Switch-Mode Supply: Lethal HV Stage Removed | 2.00 | 1 | 2 | 2 | 3 | B (need slice) | high | M4 | 3,069 |
| 2624 | Polished Cavity Daylight | 2.00 | 2 | 2 | 2 | None | B (need slice) | medium | M8 | 1,582 |
| 2623 | Direct-Coupled Magnetron Pod (No Waveguide Duct) | 2.25 | 2 | 1 | 3 | 3 | B (need slice) | high | M4 | 3,052 |
| 2622 | Ready Chime Replaced by Thaw Hum | 2.25 | 1 | 2 | 3 | 3 | C (no graph) | medium | M4 | 1,203 |
| 2621 | Progress Glow | 2.25 | 1 | 2 | 3 | 3 | C (no graph) | medium | M4 | 1,037 |
| 2620 | Capacitor-Free 48 V Bus Power Stage | 2.25 | 1 | 2 | 3 | 3 | B (need slice) | medium | M4 | 1,920 |
| 2619 | Supercapacitor-buffered pulse power replaces continuous transformer supply | 2.25 | 2 | 2 | 2 | 3 | C (no graph) | medium | M4 | 1,677 |
| 2618 | Cavity-shrink insert replaces empty air volume | 2.25 | 2 | 2 | 2 | 3 | B (need slice) | medium | M13 | 1,691 |
| 2617 | Ceramic dielectric probe feed replaces the waveguide and mica cover | 2.25 | 2 | 2 | 2 | 3 | B (need slice) | medium | M13 | 2,212 |
| 2616 | Thaw Progress Door Ring | 2.25 | 1 | 3 | 2 | 3 | B (need slice) | medium | M4 | 2,161 |

### #2625 Low-Voltage Switch-Mode Supply: Lethal HV Stage Removed

- **Score:** 2.00 (relevance 1, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r05`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 3,069 tokens per idea (run: 4,996 in + 10,351 out, 5 ideas)
- **Applied to:** C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); X7 (HV capacitor can hold a lethal charge after unplugging); A5 (Parent with young children)
- **New elements:** Component: Switch-mode low-voltage power stage (48 V class) — A GaN or Si switching converter replaces the transformer, capacitor and diode with a small low-voltage stage.; Technology: High-frequency switch-mode power conversion — Converts mains to low-voltage DC at tens of kHz, so magnetics are tiny and no lethal stored charge remains.; Function: Enables unattended, child-safe defrost cycles — No lethal capacitor and no high-voltage transformer, so the appliance is safe to leave running and safe to open or unplug.
- **New edges:** P1 -[has_component]-> Switch-mode low-voltage power stage (48 V class); Switch-mode low-voltage power stage (48 V class) -[enabled_by]-> High-frequency switch-mode power conversion; High-frequency switch-mode power conversion -[rooted_in]-> D3; Switch-mode low-voltage power stage (48 V class) -[performs_function]-> F2; Enables unattended, child-safe defrost cycles -[enables_function]-> F16; Enables unattended, child-safe defrost cycles -[addresses_need]-> M4; Enables unattended, child-safe defrost cycles -[relevant_to]-> A5; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C2; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C3; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C4; Switch-mode low-voltage power stage (48 V class) -[partially_mitigates]-> X7
- **Rationale:** A parent with young children can start a defrost cycle and walk away, because the lethal high-voltage stage that makes the appliance hazardous to open or leave running is gone.
- **Judge:** Safety is the benefit, not defrost speed, and a 48 V supply cannot drive a magnetron or deliver the needed RF power.

### #2624 Polished Cavity Daylight

- **Score:** 2.00 (relevance 2, novelty 2, feasibility 2, specificity None)
- **Made by:** claude-haiku-5-5, condition B (need slice), medium effort · run `lateral_B_M8_medium_r02`
- **Target need:** M8 — Human need for feedback (know when food is ready)
- **Cost:** 1,582 tokens per idea (run: 2,866 in + 5,043 out, 5 ideas)
- **Applied to:** C17 (Interior lamp (20-25 W incandescent)); C8 (Hinged door with perforated metal mesh window); X14 (Interior lamp burns out and is hard to replace); M8 (Human need for feedback (know when food is ready))
- **New elements:** Technology: Polished reflective metal cavity liner — A mirror-finish stainless liner bounces ambient kitchen light into the cavity and onto the food.; Component: Mirror-finish cavity liner — Replaces the bulb and its wiring with a cheap stamped steel panel that brightens the cavity.; Function: Lets the user watch food using room light — Keeps the food visible through the mesh window while removing a failure-prone bulb.
- **New edges:** Mirror-finish cavity liner -[resolves]-> C17; Polished reflective metal cavity liner -[enabled_by]-> Mirror-finish cavity liner; Mirror-finish cavity liner -[performs_function]-> Lets the user watch food using room light; Lets the user watch food using room light -[addresses_need]-> M8; Mirror-finish cavity liner -[partially_mitigates]-> X14
- **Rationale:** Visibility of the food is what satisfies the need to know it is ready, and room light reflected by a cheap mirror finish provides that without a burnable bulb.
- **Judge:** Reflecting room light into a mesh-windowed cavity barely brightens it and does not tell the user when food is ready, and it ignores the bulb's role.

### #2623 Direct-Coupled Magnetron Pod (No Waveguide Duct)

- **Score:** 2.25 (relevance 2, novelty 1, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r02`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 3,052 tokens per idea (run: 4,996 in + 10,265 out, 5 ideas)
- **Applied to:** C5 (Waveguide duct); C6 (Mica waveguide cover)
- **New elements:** Component: Antenna-coupled magnetron pod — Magnetron antenna radiates straight into the cavity from a short mounted pod, with no duct.; Technology: Coaxial / slot-antenna direct radiation — Energy leaves the source through a short, low-loss aperture instead of a long metal duct.; Function: Delivers most of the magnetron output into the food — Shorter path means less reflection loss, so more of the 700 W reaches the load.
- **New edges:** Antenna-coupled magnetron pod -[enabled_by]-> Coaxial / slot-antenna direct radiation; Coaxial / slot-antenna direct radiation -[rooted_in]-> D1; Antenna-coupled magnetron pod -[performs_function]-> Delivers most of the magnetron output into the food; Antenna-coupled magnetron pod -[resolves]-> C5; Antenna-coupled magnetron pod -[feeds]-> C7; Delivers most of the magnetron output into the food -[resolves]-> F3; Delivers most of the magnetron output into the food -[addresses_need]-> M4
- **Rationale:** Removing the duct and its losses lets more of the magnetron's output go into the frozen food, which shortens the thaw time.
- **Judge:** Removing the waveguide is an incremental tweak, and the claimed efficiency gain is dubious since the duct loss is small and coupling affects field uniformity.

### #2622 Ready Chime Replaced by Thaw Hum

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition C (no graph), medium effort · run `lateral_C_M4_medium_r06`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,203 tokens per idea (run: 1,203 in + 4,813 out, 5 ideas)
- **Applied to:** microwave_base_v1 (not in graph); M4 (Defrost frozen food quickly)
- **New elements:** Component: Thaw-tone speaker — A small speaker that replaces the end-of-timer bell with a quiet tone that changes pitch as the food thaws.; Function: Signal thaw state by sound — Lets users hear progress without opening the door, so they stop checking and interrupting the cycle.; Technology: Audio signalling — Low-power piezo sound that encodes status as pitch and rhythm.; Field: Human-computer interaction — Study of how people perceive and respond to device feedback.
- **New edges:** Thaw-tone speaker -[performs_function]-> Signal thaw state by sound; Signal thaw state by sound -[addresses_need]-> M4; Thaw-tone speaker -[enabled_by]-> Audio signalling; Audio signalling -[rooted_in]-> Human-computer interaction; Thaw-tone speaker -[resolves]-> microwave_base_v1
- **Rationale:** Pitch-based progress feedback keeps users from opening the door mid-thaw, avoiding heat loss and restarts that slow down defrosting.
- **Judge:** Audio feedback needs a thaw-state sensor it does not provide and does not speed up defrosting, so it serves M4 only weakly.

### #2621 Progress Glow

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition C (no graph), medium effort · run `lateral_C_M4_medium_r02`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,037 tokens per idea (run: 1,203 in + 3,981 out, 5 ideas)
- **Applied to:** base:interior_incandescent_lamp (not in graph); M4 (Defrost frozen food quickly)
- **New elements:** Component: Colour-shifting LED ring — A cool-white LED strip that shifts from blue (frozen) to amber (thawed) as the food warms, replacing the 20-25 W lamp.; Function: Show thaw progress at a glance — Lets the user see how close the food is to ready without opening the door.; Technology: Low-power LED — Draws a few watts, unlike the 20-25 W incandescent bulb.
- **New edges:** Colour-shifting LED ring -[performs_function]-> Show thaw progress at a glance; Show thaw progress at a glance -[addresses_need]-> M4; Low-power LED -[enabled_by]-> Colour-shifting LED ring; Colour-shifting LED ring -[resolves]-> base:interior_incandescent_lamp
- **Rationale:** A colour-shifting glow replaces the lamp and makes the wait feel shorter, because the user can see progress without interrupting the defrost.
- **Judge:** It only displays progress and does not speed thawing, and judging food temperature by color without a sensor is unrealistic.

### #2620 Capacitor-Free 48 V Bus Power Stage

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), medium effort · run `B_M4_medium_r03`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,920 tokens per idea (run: 4,996 in + 4,606 out, 5 ideas)
- **Applied to:** C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); X7 (HV capacitor can hold a lethal charge after unplugging); X15 (Regional mains variants (230 V/50 Hz vs 120 V/60 Hz))
- **New elements:** Component: Low-voltage GaN switching supply with 48 V DC bus — A high-frequency switch-mode supply, fed from a 48 V rail, replaces the transformer, capacitor and diode chain.; Technology: High-frequency switch-mode power conversion — Small ferrite transformers and GaN switches step the voltage up to the RF stage efficiently at kilohertz to megahertz rates.; Function: Delivers magnetron-free energy at any mains voltage — A universal input stage converts 120 V or 230 V mains to the internal bus, which removes the regional variant problem.
- **New edges:** Low-voltage GaN switching supply with 48 V DC bus -[resolves]-> C2; Low-voltage GaN switching supply with 48 V DC bus -[resolves]-> C3; Low-voltage GaN switching supply with 48 V DC bus -[resolves]-> C4; High-frequency switch-mode power conversion -[enabled_by]-> Low-voltage GaN switching supply with 48 V DC bus; High-frequency switch-mode power conversion -[partially_mitigates]-> X7; Delivers magnetron-free energy at any mains voltage -[partially_mitigates]-> X15; Delivers magnetron-free energy at any mains voltage -[performs_function]-> F2
- **Rationale:** Removing the kilovolt capacitor and transformer makes the oven safe and globally portable, so it can be plugged in and used to thaw food anywhere.
- **Judge:** This is a power-supply swap with little bearing on defrost speed, and it only makes sense alongside a solid-state RF source.

### #2619 Supercapacitor-buffered pulse power replaces continuous transformer supply

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition C (no graph), medium effort · run `patent_C_M4_medium_r10`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,677 tokens per idea (run: 1,194 in + 7,193 out, 5 ideas)
- **Applied to:** M4 (Defrost frozen food quickly)
- **New elements:** Technology: Pulsed power conversion with energy buffering — A slow mains charger stores energy that a fast converter releases in bursts.; Component: Supercapacitor bank, 48 V series stack — Stores energy charged slowly from a 230 V socket and delivers high-current bursts.; Component: Pulsed high-voltage converter feeding the magnetron — Switch-mode converter releases stored energy as 1.5 kW pulses into the magnetron.; Function: Deliver high-power bursts from a 700 W mains draw — Peak output exceeds the socket rating for short intervals, which accelerates heating.; Constraint: Mains current limit caps continuous microwave power — A standard socket and breaker limit sustained output, which lengthens defrost time.
- **New edges:** Supercapacitor bank, 48 V series stack -[enabled_by]-> Pulsed power conversion with energy buffering; Pulsed high-voltage converter feeding the magnetron -[enabled_by]-> Pulsed power conversion with energy buffering; Supercapacitor bank, 48 V series stack -[feeds]-> Pulsed high-voltage converter feeding the magnetron; Pulsed high-voltage converter feeding the magnetron -[performs_function]-> Deliver high-power bursts from a 700 W mains draw; Deliver high-power bursts from a 700 W mains draw -[addresses_need]-> M4; Supercapacitor bank, 48 V series stack -[partially_mitigates]-> Mains current limit caps continuous microwave power
- **Rationale:** Storing energy between bursts lets the oven deliver more power into the load than the socket could supply continuously, which shortens the time to thaw.
- **Judge:** Pulsing from a supercap cannot raise average energy beyond mains input, so the thaw time claim is flawed and the magnetron has its own power limits.

### #2618 Cavity-shrink insert replaces empty air volume

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), medium effort · run `lateral_B_M13_medium_r08`
- **Target need:** M13 — Energy efficiency
- **Cost:** 1,691 tokens per idea (run: 4,673 in + 3,783 out, 5 ideas)
- **Applied to:** C7 (Enamelled steel cooking cavity (~20 L)); X11 (Cavity volume limited by countertop size); F4 (Heats food via dielectric water-molecule vibration (FastHeating))
- **New elements:** Component: Microwave-transparent food-sized insert — A mica or glass insert that fills most of the unused cavity air, so the field heats only the food zone.; Function: Confines RF energy to the food zone — Limits the heated volume to the food, reducing RF energy absorbed by empty air and walls.
- **New edges:** Microwave-transparent food-sized insert -[enabled_by]-> T16; Microwave-transparent food-sized insert -[performs_function]-> Confines RF energy to the food zone; Confines RF energy to the food zone -[partially_mitigates]-> X11; Confines RF energy to the food zone -[enables_function]-> F4; Confines RF energy to the food zone -[addresses_need]-> M13
- **Rationale:** Shrinking the effective heated volume to the food means less of the magnetron's output is spent on air and walls.
- **Judge:** An insert is simple, but the load absorbs most of the energy anyway, and empty air does not absorb RF, so efficiency gains are doubtful.

### #2617 Ceramic dielectric probe feed replaces the waveguide and mica cover

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), medium effort · run `patent_B_M13_medium_r14`
- **Target need:** M13 — Energy efficiency
- **Cost:** 2,212 tokens per idea (run: 4,664 in + 6,395 out, 5 ideas)
- **Applied to:** C5 (Waveguide duct); C6 (Mica waveguide cover); F3 (Guides microwave energy into the cavity); M13 (Energy efficiency)
- **New elements:** Component: Alumina-ceramic dielectric probe antenna — Low-loss ceramic-loaded coaxial probe couples RF from the magnetron directly into the cavity.; Technology: Coaxial probe coupling with low-loss dielectric loading — Direct coupling avoids the TE10 duct and its sealing cover, lowering insertion loss.
- **New edges:** Alumina-ceramic dielectric probe antenna -[resolves]-> C5; Alumina-ceramic dielectric probe antenna -[resolves]-> C6; Alumina-ceramic dielectric probe antenna -[performs_function]-> F3; Coaxial probe coupling with low-loss dielectric loading -[enabled_by]-> Alumina-ceramic dielectric probe antenna; Alumina-ceramic dielectric probe antenna -[addresses_need]-> M13
- **Rationale:** Replacing the waveguide and mica cover with a low-loss direct probe reduces RF transmission losses between the magnetron and the food, so more of the magnetron's output reaches the load.
- **Judge:** Waveguide losses are already small, and a ceramic probe handling kW-level RF near the load risks arcing and heating, so the gain is marginal.

### #2616 Thaw Progress Door Ring

- **Score:** 2.25 (relevance 1, novelty 3, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), medium effort · run `lateral_B_M4_medium_r02`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 2,161 tokens per idea (run: 5,149 in + 5,655 out, 5 ideas)
- **Applied to:** P1 (Basic countertop microwave oven (timer knob, power knob, door button, lamp)); X9 (Superheating of liquids — risk of eruptive boiling); M4 (Defrost frozen food quickly)
- **New elements:** Component: Thermochromic thaw-progress ring on door glass — Printed colour ring on the door window that shifts from frost-blue to clear as the food thaws, replacing the interior lamp and bell.; Technology: Thermochromic ink and light-guided glass — Heat-sensitive pigment that changes colour at set temperatures, lit by ambient light and needing no bulb.; Function: Makes thaw progress visible and reduces perceived waiting — Shows the user the thaw advancing at a glance, so the wait feels shorter and the user trusts the result.
- **New edges:** Thermochromic thaw-progress ring on door glass -[enabled_by]-> Thermochromic ink and light-guided glass; Thermochromic thaw-progress ring on door glass -[performs_function]-> Makes thaw progress visible and reduces perceived waiting; Makes thaw progress visible and reduces perceived waiting -[addresses_need]-> M4; Thermochromic thaw-progress ring on door glass -[relevant_to]-> P1; Thermochromic thaw-progress ring on door glass -[relevant_to]-> X9
- **Rationale:** Making the thaw visibly progress changes the experience of waiting, so frozen food feels ready sooner even though its physical thawing time is unchanged.
- **Judge:** It does not speed thawing, only perceived waiting, and a thermochromic ring on the door is unlikely to track food temperature.
