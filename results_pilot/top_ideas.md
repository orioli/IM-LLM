# Top 10 and bottom 10 ideas

1282 ideas scored individually and blind by `claude-sonnet-5-5` on relevance, novelty, feasibility, specificity (1–5). Score = mean of the four criteria. Cost per idea = the generating call's total tokens divided by its number of ideas.

## Who made them

| Arm | In top | In bottom |
| --- | --- | --- |
| A (full graph), high effort | 6 | 0 |
| A (full graph), low effort | 0 | 3 |
| B (need slice), high effort | 4 | 1 |
| B (need slice), low effort | 0 | 6 |

## Top 10

| Rank | Idea | Score | Rel | Nov | Feas | Spec | Condition | Effort | Need | Tokens / idea |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Solid-State RF Core (No High Voltage) | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M7 | 2,512 |
| 2 | Solid-State Heart: GaN Amplifier Replaces Magnetron and HV Chain | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M13 | 2,801 |
| 3 | 27 MHz RF Thaw Plates | 4.50 | 5 | 4 | 4 | 5 | B (need slice) | high | M4 | 2,115 |
| 4 | Curie-Point Butter Dish | 4.25 | 5 | 5 | 3 | 4 | A (full graph) | high | M17 | 4,126 |
| 5 | Curie-Point Butter Tray: power knob replaced by a self-limiting susceptor | 4.25 | 5 | 5 | 3 | 4 | A (full graph) | high | M17 | 4,580 |
| 6 | Weighing Roller Ring | 4.25 | 5 | 4 | 4 | 4 | A (full graph) | high | M8 | 3,634 |
| 7 | Solid-State RF Core: Magnetron and HV Stack Replaced by GaN Amplifiers | 4.25 | 5 | 4 | 3 | 5 | A (full graph) | high | M13 | 4,037 |
| 8 | Tap-to-Cook Packaging | 4.25 | 5 | 4 | 4 | 4 | A (full graph) | high | M6 | 4,710 |
| 9 | Tap-a-Tile Cooking | 4.25 | 5 | 4 | 4 | 4 | A (full graph) | high | M6 | 4,423 |
| 10 | Shape-Keyed Time Tokens | 4.25 | 5 | 4 | 4 | 4 | B (need slice) | high | M14 | 2,216 |

### #1 Solid-State RF Core (No High Voltage)

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M7_high_r01`
- **Target need:** M7 — Safe for family use (radiation, burns, electric shock)
- **Cost:** 2,512 tokens per idea (run: 4,480 in + 8,079 out, 5 ideas)
- **Applied to:** C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); T3 (Half-wave voltage doubler (capacitor + diode)); F20 (Discharges stored high voltage after switch-off); X7 (HV capacitor can hold a lethal charge after unplugging)
- **New elements:** Component: GaN solid-state RF power amplifier module — Replaces the magnetron, 2 kV transformer stack and HV capacitor with a 2.45 GHz GaN amplifier running from a 48 V DC bus.; Technology: Gallium-nitride switched-mode RF amplification — Class-E/F solid-state amplifier generates microwave power without vacuum tubes or kilovolt rails.; Function: Eliminates lethal stored high voltage — No component holds more than safe extra-low voltage, so no bleeder discharge is needed after unplugging.
- **New edges:** GaN solid-state RF power amplifier module -[enabled_by]-> Gallium-nitride switched-mode RF amplification; GaN solid-state RF power amplifier module -[performs_function]-> Eliminates lethal stored high voltage; Eliminates lethal stored high voltage -[addresses_need]-> M7; GaN solid-state RF power amplifier module -[resolves]-> X7; GaN solid-state RF power amplifier module -[resolves]-> C3
- **Rationale:** By removing the 2 kV supply entirely, the appliance can no longer deliver an electric shock from its power stage, which directly protects families from electrocution and reduces leakage sources.
- **Judge:** Solid-state RF is real and removes the lethal high-voltage stage, though the 48 V bus is not strictly 'extra-low' by every standard and cost is high.

### #2 Solid-State Heart: GaN Amplifier Replaces Magnetron and HV Chain

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M13_high_r03`
- **Target need:** M13 — Energy efficiency
- **Cost:** 2,801 tokens per idea (run: 4,520 in + 9,484 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode)
- **New elements:** Component: GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) — Low-voltage transistor power amplifier replaces the magnetron and its 4 kV transformer-doubler chain; no cathode to wear and no lethal HV.; Technology: Gallium nitride HEMT power amplifier — Wide-bandgap transistors reach high DC-to-RF efficiency at 2.45 GHz and allow precise, proportional power control.; Component: 50 V switch-mode PSU — Compact high-frequency SMPS replaces the bulky 50 Hz HV transformer and voltage doubler, so mains-frequency losses disappear.
- **New edges:** GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C1; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C2; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C3; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[resolves]-> C4; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[performs_function]-> F1; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[enabled_by]-> Gallium nitride HEMT power amplifier; 50 V switch-mode PSU -[performs_function]-> F2; 50 V switch-mode PSU -[feeds]-> GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail); GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[partially_mitigates]-> X8; GaN solid-state RF amplifier (2.45 GHz, 50 V DC rail) -[partially_mitigates]-> X7; F1 -[addresses_need]-> M13
- **Rationale:** Solid-state RF generation with a low-voltage supply removes the magnetron's heat-and-conversion losses and gives proportional power, so less electricity is wasted per cooked meal.
- **Judge:** Solid-state RF with GaN is real and directly targets conversion efficiency, though cost is high and efficiency gains over magnetrons are modest at present.

### #3 27 MHz RF Thaw Plates

- **Score:** 4.50 (relevance 5, novelty 4, feasibility 4, specificity 5)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r03`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 2,115 tokens per idea (run: 4,996 in + 5,581 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C5 (Waveguide duct); F1 (Generates microwave energy at 2.45 GHz); F3 (Guides microwave energy into the cavity)
- **New elements:** Technology: Solid-state RF amplifier at 27 MHz (LDMOS/GaN) — Low-cost transistor power stage replaces the vacuum magnetron, with no cathode to wear out.; Component: Parallel-plate RF electrode pair — Food sits between two insulated plates, so the field penetrates the full thickness of a frozen block.; Function: Volumetric thaw of ice through full thickness — Longer RF wavelength heats the interior of a frozen block evenly instead of only the surface.
- **New edges:** Solid-state RF amplifier at 27 MHz (LDMOS/GaN) -[resolves]-> C1; Parallel-plate RF electrode pair -[resolves]-> C5; Parallel-plate RF electrode pair -[performs_function]-> Volumetric thaw of ice through full thickness; Volumetric thaw of ice through full thickness -[addresses_need]-> M4; Solid-state RF amplifier at 27 MHz (LDMOS/GaN) -[partially_mitigates]-> X8
- **Rationale:** Lower-frequency RF penetrates frozen blocks deeply and uniformly, so the thaw is faster and more even than surface-first 2.45 GHz heating.
- **Judge:** RF thawing at 27 MHz is a real, proven industrial approach that heats frozen blocks uniformly and deeply, and solid-state RF replaces the magnetron, though cost and shielding are challenges in a home appliance.

### #4 Curie-Point Butter Dish

- **Score:** 4.25 (relevance 5, novelty 5, feasibility 3, specificity 4)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M17_high_r03`
- **Target need:** M17 — Bake a birthday cake (prep tasks like melting butter)
- **Cost:** 4,126 tokens per idea (run: 10,920 in + 9,709 out, 5 ideas)
- **Applied to:** C14 (Power-level knob (5-step duty-cycle cam switch)); F8 (Sets average heating power level); X6 (Power only adjustable by on/off cycling, not continuously); F17 (Melts / softens butter, chocolate, etc.)
- **New elements:** Technology: Curie-point ferrite susceptor — Ferrite-loaded ceramic whose microwave loss collapses above its Curie temperature (~40 °C), so the dish self-limits and stops heating once butter is liquid.; Component: Curie-point melting dish — Ceramic dish with a ferrite-loaded base that sets its own maximum temperature, replacing the 5-step power cam.; Function: Self-limiting melt at target temperature — Holds the contents at the melt point without any power setting from the user.
- **New edges:** Curie-point melting dish -[resolves]-> C14; Curie-point ferrite susceptor -[enabled_by]-> Curie-point melting dish; Curie-point melting dish -[performs_function]-> Self-limiting melt at target temperature; Self-limiting melt at target temperature -[addresses_need]-> M17; Curie-point melting dish -[partially_mitigates]-> X6
- **Rationale:** Butter melts itself to the right state with no power setting or watching, so a baker can prep the cake while the dish handles the heat.
- **Judge:** A Curie-point ferrite dish that self-limits at butter's melt point is clever and directly serves the melting prep task, though Curie temperatures near 40 °C and uniform melting are tricky.

### #5 Curie-Point Butter Tray: power knob replaced by a self-limiting susceptor

- **Score:** 4.25 (relevance 5, novelty 5, feasibility 3, specificity 4)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M17_high_r04`
- **Target need:** M17 — Bake a birthday cake (prep tasks like melting butter)
- **Cost:** 4,580 tokens per idea (run: 10,920 in + 11,981 out, 5 ideas)
- **Applied to:** C14 (Power-level knob (5-step duty-cycle cam switch)); T11 (Duty-cycle power modulation (on/off cycling)); F8 (Sets average heating power level); F17 (Melts / softens butter, chocolate, etc.); X6 (Power only adjustable by on/off cycling, not continuously)
- **New elements:** Technology: Curie-point ferrite self-limiting susceptor — Ferrite whose microwave loss collapses above its tuned Curie temperature (~50 °C), so it self-regulates without any power setting.; Component: Curie-point melt tray (ceramic dish with embedded ferrite susceptor) — A butter dish that cannot overheat: it stops absorbing energy at ~50 °C, so the user just sets full power and walks away.; Function: Self-limits temperature for gentle melting — Material physics replaces the 5-step power cam and duty-cycle switching.
- **New edges:** Curie-point melt tray (ceramic dish with embedded ferrite susceptor) -[resolves]-> C14; Curie-point melt tray (ceramic dish with embedded ferrite susceptor) -[enabled_by]-> Curie-point ferrite self-limiting susceptor; Curie-point melt tray (ceramic dish with embedded ferrite susceptor) -[performs_function]-> F17; Curie-point melt tray (ceramic dish with embedded ferrite susceptor) -[performs_function]-> Self-limits temperature for gentle melting; Self-limits temperature for gentle melting -[addresses_need]-> M17; Curie-point melt tray (ceramic dish with embedded ferrite susceptor) -[partially_mitigates]-> X6
- **Rationale:** Melting butter for a cake becomes foolproof because the tray's material physics caps the temperature, so the user never needs to pick a power level or risk scorching.
- **Judge:** Self-limiting Curie-point ferrite susceptor is a clever, physically grounded way to make butter melting foolproof, though a ~50 °C ferrite with sharp loss collapse and food-safe packaging is a stretch.

### #6 Weighing Roller Ring

- **Score:** 4.25 (relevance 5, novelty 4, feasibility 4, specificity 4)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M8_high_r02`
- **Target need:** M8 — Human need for feedback (know when food is ready)
- **Cost:** 3,634 tokens per idea (run: 10,914 in + 7,255 out, 5 ideas)
- **Applied to:** C11 (Roller ring and coupler (turntable support)); F5 (Distributes heat evenly by rotating food through the field)
- **New elements:** Component: Strain-gauge load-cell roller ring — Replaces the passive plastic roller ring with a weighing ring that reads the mass of the dish as it rotates.; Technology: Strain-gauge bridge weighing — Wheatstone-bridge strain gauges convert small deflections under load into a precise mass reading.; Function: Estimates moisture lost as doneness proxy — Tracks evaporative mass loss, which correlates with how far food has cooked or dried.
- **New edges:** Strain-gauge load-cell roller ring -[resolves]-> C11; Strain-gauge load-cell roller ring -[enabled_by]-> Strain-gauge bridge weighing; Strain-gauge bridge weighing -[rooted_in]-> D3; Strain-gauge load-cell roller ring -[performs_function]-> Estimates moisture lost as doneness proxy; Estimates moisture lost as doneness proxy -[resolves]-> F7; Estimates moisture lost as doneness proxy -[addresses_need]-> M8; Strain-gauge load-cell roller ring -[partially_mitigates]-> X5
- **Rationale:** Measuring how much water the food has lost gives a direct, food-based signal of readiness, so the user no longer has to guess a time for M8.
- **Judge:** A thermochromic dot on the vessel gives direct, visible feedback from across the room, which is clever and feasible, though it requires special consumable vessels.

### #7 Solid-State RF Core: Magnetron and HV Stack Replaced by GaN Amplifiers

- **Score:** 4.25 (relevance 5, novelty 4, feasibility 3, specificity 5)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M13_high_r03`
- **Target need:** M13 — Energy efficiency
- **Cost:** 4,037 tokens per idea (run: 10,906 in + 9,277 out, 5 ideas)
- **Applied to:** C1 (Magnetron tube (2.45 GHz, ~700 W output)); C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); T11 (Duty-cycle power modulation (on/off cycling)); X6 (Power only adjustable by on/off cycling, not continuously)
- **New elements:** Technology: GaN solid-state 2.45 GHz RF amplification — Paralleled gallium-nitride transistor stages generate 2.45 GHz RF from a low-voltage DC rail, with no cathode, filament or kV rail.; Component: GaN RF power amplifier module — Replaces the magnetron tube with a ~700 W transistor array that has no warm-up and no filament standby draw.; Technology: High-frequency switch-mode low-voltage PSU — Compact ~48 V SMPS replaces the iron-core HV transformer, voltage doubler capacitor and HV diode.; Component: Low-voltage SMPS board — Replaces transformer, HV capacitor and diode, removing core losses and the bleeder-resistor drain.; Function: Continuous analog RF power control — Sets any average power by gain control, so the on/off duty-cycle overshoot is eliminated.
- **New edges:** GaN solid-state 2.45 GHz RF amplification -[rooted_in]-> D1; GaN RF power amplifier module -[enabled_by]-> GaN solid-state 2.45 GHz RF amplification; GaN RF power amplifier module -[performs_function]-> F1; GaN RF power amplifier module -[resolves]-> C1; High-frequency switch-mode low-voltage PSU -[rooted_in]-> D3; Low-voltage SMPS board -[enabled_by]-> High-frequency switch-mode low-voltage PSU; Low-voltage SMPS board -[performs_function]-> F2; Low-voltage SMPS board -[resolves]-> C2; Continuous analog RF power control -[resolves]-> X6; Continuous analog RF power control -[addresses_need]-> M13
- **Rationale:** Removing the kV transformer, capacitor, diode and magnetron cathode cuts conversion and standby losses, and continuous power control ends the wasteful on/off cycling that drives M13 energy use.
- **Judge:** Solid-state RF is real and offers higher efficiency and control, though 700 W GaN cost is high and the efficiency gain over a magnetron is modest, but it directly targets energy use.

### #8 Tap-to-Cook Packaging

- **Score:** 4.25 (relevance 5, novelty 4, feasibility 4, specificity 4)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M6_high_r05`
- **Target need:** M6 — Simple operation with no learning curve
- **Cost:** 4,710 tokens per idea (run: 10,910 in + 12,642 out, 5 ideas)
- **Applied to:** C13 (Mechanical timer knob & cam switch (0-30 min)); C14 (Power-level knob (5-step duty-cycle cam switch)); C24 (Control panel fascia); F7 (Sets and counts down cooking duration); F8 (Sets average heating power level)
- **New elements:** Component: NFC reader in the door's outer panel — Hold a food pack's tag against the front glass and the oven loads its time and power program.; Technology: Passive NFC tags printed on food packaging — A 13.56 MHz near-field tag stores the cook program and needs no battery.; Function: Loads cook program from the food packaging — The packaging does the thinking, and the user only taps.; Constraint: Metal cavity blocks in-cavity tag reading — Tags must be read through the front panel, not from inside the cavity.
- **New edges:** NFC reader in the door's outer panel -[resolves]-> C13; NFC reader in the door's outer panel -[resolves]-> C14; NFC reader in the door's outer panel -[relevant_to]-> C24; NFC reader in the door's outer panel -[enabled_by]-> Passive NFC tags printed on food packaging; Passive NFC tags printed on food packaging -[rooted_in]-> D1; NFC reader in the door's outer panel -[performs_function]-> Loads cook program from the food packaging; Loads cook program from the food packaging -[addresses_need]-> M6; Loads cook program from the food packaging -[addresses_need]-> M4; C7 -[causes]-> Metal cavity blocks in-cavity tag reading; NFC reader in the door's outer panel -[partially_mitigates]-> Metal cavity blocks in-cavity tag reading
- **Rationale:** Users never set a time or power level because the food package carries the instructions and a single tap loads them.
- **Judge:** Tap-to-cook removes settings entirely, and NFC is cheap, but it depends on packaging adoption and does not cover non-packaged food.

### #9 Tap-a-Tile Cooking

- **Score:** 4.25 (relevance 5, novelty 4, feasibility 4, specificity 4)
- **Made by:** claude-haiku-5-5, condition A (full graph), high effort · run `A_M6_high_r01`
- **Target need:** M6 — Simple operation with no learning curve
- **Cost:** 4,423 tokens per idea (run: 10,910 in + 11,203 out, 5 ideas)
- **Applied to:** C13 (Mechanical timer knob & cam switch (0-30 min)); C14 (Power-level knob (5-step duty-cycle cam switch)); F7 (Sets and counts down cooking duration); F8 (Sets average heating power level)
- **New elements:** Technology: Passive near-field RFID (13.56 MHz) — Battery-free tags powered by the reader's inductive field, the same principle as transit cards.; Component: Food tile (passive RFID card printed with a food picture) — Each packaged meal or recipe ships with a tile that stores its own cook time and power level.; Component: Tile reader coil under the glass tray — Reads the tile through the tray and the cavity floor when the user places it on the tray.; Function: Sets time and power from a tapped tile — Replaces dialling a timer and a power level by hand with one placement of a tile.
- **New edges:** Food tile (passive RFID card printed with a food picture) -[enabled_by]-> Passive near-field RFID (13.56 MHz); Tile reader coil under the glass tray -[enabled_by]-> Passive near-field RFID (13.56 MHz); Tile reader coil under the glass tray -[performs_function]-> Sets time and power from a tapped tile; Sets time and power from a tapped tile -[addresses_need]-> M6; Tile reader coil under the glass tray -[resolves]-> C14; Food tile (passive RFID card printed with a food picture) -[resolves]-> C13
- **Rationale:** The user puts down a picture tile and the oven sets itself, so there is nothing to read, dial or remember.
- **Judge:** Placing a tile that sets time and power removes all dialling, and RFID is cheap and proven, though it depends on a tile ecosystem and does not cover ad-hoc reheating.

### #10 Shape-Keyed Time Tokens

- **Score:** 4.25 (relevance 5, novelty 4, feasibility 4, specificity 4)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M14_high_r01`
- **Target need:** M14 — Accessible for elderly / visually impaired users
- **Cost:** 2,216 tokens per idea (run: 1,956 in + 9,122 out, 5 ideas)
- **Applied to:** C13 (Mechanical timer knob & cam switch (0-30 min)); X5 (Mechanical timer imprecise for short (<1 min) durations); F7 (Sets and counts down cooking duration); M14 (Accessible for elderly / visually impaired users)
- **New elements:** Component: Shape-keyed time tokens and matching slot cage — Chunky tactile tokens (round = 1 min, square = 5 min, star = 10 min) drop into a slot that sets the cam stop, so no numerals need reading.; Technology: Mechanical keyed-cam stop — Shape-matching mechanism that stops the cam at a fixed angle per token, removing the need for a dial or fine rotation.; Function: Sets cook duration by touch alone — Lets users set time by feel with no reading, no fine motor control, and no small print.
- **New edges:** Shape-keyed time tokens and matching slot cage -[resolves]-> C13; Shape-keyed time tokens and matching slot cage -[enabled_by]-> Mechanical keyed-cam stop; Shape-keyed time tokens and matching slot cage -[performs_function]-> Sets cook duration by touch alone; Sets cook duration by touch alone -[addresses_need]-> M14; Shape-keyed time tokens and matching slot cage -[partially_mitigates]-> X5; Mechanical keyed-cam stop -[rooted_in]-> D4
- **Rationale:** Replacing the numbered knob with shape-keyed tokens lets elderly and visually impaired users set time by touch, with fewer parts than a precision dial.
- **Judge:** Tactile shape tokens that mechanically set a cam stop are an intuitive, low-tech way to set time without reading, though the fixed token increments limit flexibility.

## Bottom 10

| Rank | Idea | Score | Rel | Nov | Feas | Spec | Condition | Effort | Need | Tokens / idea |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1282 | Low-Voltage Switch-Mode Supply: Lethal HV Stage Removed | 1.75 | 1 | 2 | 1 | 3 | B (need slice) | high | M4 | 3,069 |
| 1281 | Lens-Free Glass Dome Replacing Lamp and Door Window | 2.00 | 1 | 2 | 2 | 3 | B (need slice) | low | M4 | 1,541 |
| 1280 | Ambient Solar-Preheat Shell: Cavity Wall Doubles as a Photothermal Collector | 2.00 | 1 | 3 | 1 | 3 | B (need slice) | low | M13 | 1,490 |
| 1279 | Transparent Glass Cavity Window Lamp-Free Vision | 2.25 | 1 | 2 | 3 | 3 | A (full graph) | low | M12 | 2,666 |
| 1278 | Fully Transparent Thaw Chamber Without Lamp | 2.25 | 1 | 2 | 3 | 3 | A (full graph) | low | M4 | 2,708 |
| 1277 | Ghost Lamp Vision: Replace the Interior Lamp With Microwave-Transparent Transparent Walls | 2.25 | 1 | 2 | 3 | 3 | B (need slice) | low | M12 | 1,425 |
| 1276 | Transparent Plasma-Free Cavity Using Conductive Glass Mesh | 2.25 | 2 | 2 | 2 | 3 | B (need slice) | low | M7 | 1,402 |
| 1275 | Transparent Glass Cavity Replacing Lamp and Door Window | 2.25 | 2 | 2 | 2 | 3 | B (need slice) | low | M17 | 1,536 |
| 1274 | Transparent Conductive-Film Door Replacing Mesh Window | 2.25 | 2 | 2 | 2 | 3 | B (need slice) | low | M6 | 1,113 |
| 1273 | Thermochromic Thaw Window (Substitute the Interior Lamp) | 2.25 | 2 | 2 | 2 | 3 | A (full graph) | low | M4 | 3,091 |

### #1282 Low-Voltage Switch-Mode Supply: Lethal HV Stage Removed

- **Score:** 1.75 (relevance 1, novelty 2, feasibility 1, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), high effort · run `B_M4_high_r05`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 3,069 tokens per idea (run: 4,996 in + 10,351 out, 5 ideas)
- **Applied to:** C2 (High-voltage transformer); C3 (High-voltage capacitor (~1 µF, 2.1 kV) with internal bleeder resistor); C4 (High-voltage rectifier diode); X7 (HV capacitor can hold a lethal charge after unplugging); A5 (Parent with young children)
- **New elements:** Component: Switch-mode low-voltage power stage (48 V class) — A GaN or Si switching converter replaces the transformer, capacitor and diode with a small low-voltage stage.; Technology: High-frequency switch-mode power conversion — Converts mains to low-voltage DC at tens of kHz, so magnetics are tiny and no lethal stored charge remains.; Function: Enables unattended, child-safe defrost cycles — No lethal capacitor and no high-voltage transformer, so the appliance is safe to leave running and safe to open or unplug.
- **New edges:** P1 -[has_component]-> Switch-mode low-voltage power stage (48 V class); Switch-mode low-voltage power stage (48 V class) -[enabled_by]-> High-frequency switch-mode power conversion; High-frequency switch-mode power conversion -[rooted_in]-> D3; Switch-mode low-voltage power stage (48 V class) -[performs_function]-> F2; Enables unattended, child-safe defrost cycles -[enables_function]-> F16; Enables unattended, child-safe defrost cycles -[addresses_need]-> M4; Enables unattended, child-safe defrost cycles -[relevant_to]-> A5; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C2; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C3; Switch-mode low-voltage power stage (48 V class) -[resolves]-> C4; Switch-mode low-voltage power stage (48 V class) -[partially_mitigates]-> X7
- **Rationale:** A parent with young children can start a defrost cycle and walk away, because the lethal high-voltage stage that makes the appliance hazardous to open or leave running is gone.
- **Judge:** A 48 V supply cannot drive a magnetron, which needs kV, and the idea is about safety rather than defrost speed.

### #1281 Lens-Free Glass Dome Replacing Lamp and Door Window

- **Score:** 2.00 (relevance 1, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M4_low_r02`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 1,541 tokens per idea (run: 4,996 in + 2,709 out, 5 ideas)
- **Applied to:** C6 (Mica waveguide cover); F3 (Guides microwave energy into the cavity); F5 (Distributes heat evenly by rotating food through the field)
- **New elements:** Technology: Phase-change smart glass with RF shielding — Electrochromic glass that stays clear for viewing, but also blocks radiation leakage.; Component: Electrochromic door panel — A fully transparent door that replaces the mica cover and the viewing window so the user can see the food at any time.; Function: Lets the user monitor defrost progress without opening the door — Removes the need to open the door for checks, keeping RF energy contained and speeding defrost.
- **New edges:** Electrochromic door panel -[enabled_by]-> Phase-change smart glass with RF shielding; Electrochromic door panel -[performs_function]-> Lets the user monitor defrost progress without opening the door; Lets the user monitor defrost progress without opening the door -[enables_function]-> F16; Electrochromic door panel -[resolves]-> C6
- **Rationale:** Continuous visibility without opening the door keeps the cavity sealed and lets parents track thawing, directly supporting faster, safer defrosting for M4.
- **Judge:** A see-through door barely affects defrost speed, and the claim that it speeds defrosting is unfounded.

### #1280 Ambient Solar-Preheat Shell: Cavity Wall Doubles as a Photothermal Collector

- **Score:** 2.00 (relevance 1, novelty 3, feasibility 1, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M13_low_r04`
- **Target need:** M13 — Energy efficiency
- **Cost:** 1,490 tokens per idea (run: 4,520 in + 2,929 out, 5 ideas)
- **Applied to:** C7 (Enamelled steel cooking cavity (~20 L)); C6 (Mica waveguide cover); X11 (Cavity volume limited by countertop size); P1 (Basic countertop microwave oven (timer knob, power knob, door button, lamp))
- **New elements:** Technology: Selective-absorber solar coating on enamel — Black spectrally selective coating that absorbs ambient light and heat to warm the cavity and contents before RF starts.; Component: Photothermal cavity skin — Outer wrapper and cavity face acting as a passive collector that preheats food.; Function: Passive preheating of food — Reduces the RF energy needed to bring food up to cooking temperature.
- **New edges:** Photothermal cavity skin -[enabled_by]-> Selective-absorber solar coating on enamel; Photothermal cavity skin -[performs_function]-> Passive preheating of food; Passive preheating of food -[enables_function]-> F4; Passive preheating of food -[addresses_need]-> M13; Photothermal cavity skin -[resolves]-> C7
- **Rationale:** Using free ambient and kitchen light to supply part of the heating energy directly lowers the electrical energy each cooking cycle requires.
- **Judge:** Ambient light on a cavity wall yields negligible heat, so the energy saving is practically nil, though the concept is concrete.

### #1279 Transparent Glass Cavity Window Lamp-Free Vision

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition A (full graph), low effort · run `A_M12_low_r02`
- **Target need:** M12 — Healthy diet (nutrient retention, less fat)
- **Cost:** 2,666 tokens per idea (run: 10,917 in + 2,412 out, 5 ideas)
- **Applied to:** C17 (Interior lamp (20-25 W incandescent)); C8 (Hinged door with perforated metal mesh window); X14 (Interior lamp burns out and is hard to replace); F11 (Illuminates cavity so the user can watch the food)
- **New elements:** Technology: Electrochromic door glass with ITO conductive layer — Transparent conductive coating on the door window lets the user see inside without a bulb, and it blocks RF through the sub-wavelength pattern.; Function: Shows food state at a glance without a lamp — Replaces the incandescent lamp, so users can check cooking progress and avoid opening the door, which keeps heat and nutrients inside.
- **New edges:** Electrochromic door glass with ITO conductive layer -[enabled_by]-> C17; Electrochromic door glass with ITO conductive layer -[partially_mitigates]-> X14; Shows food state at a glance without a lamp -[addresses_need]-> M8; Shows food state at a glance without a lamp -[addresses_need]-> M12
- **Rationale:** Viewing without opening the door keeps cavity heat and steam in, so food cooks with less nutrient loss and less reliance on overcooking, serving M12.
- **Judge:** The link to nutrition is weak, since microwaves already have see-through mesh doors and little heat is lost by opening the door.

### #1278 Fully Transparent Thaw Chamber Without Lamp

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition A (full graph), low effort · run `A_M4_low_r03`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 2,708 tokens per idea (run: 10,910 in + 2,630 out, 5 ideas)
- **Applied to:** C17 (Interior lamp (20-25 W incandescent)); F11 (Illuminates cavity so the user can watch the food); C8 (Hinged door with perforated metal mesh window); X14 (Interior lamp burns out and is hard to replace)
- **New elements:** Technology: Electroluminescent cavity panel — A thin EL film on the cavity wall lights the interior cold and reliably, with no filament to burn out.; Component: EL light sheet — Replaces the 20-25 W incandescent lamp with a low-power, long-life sheet.; Function: Shows defrost progress to user — The light sheet can pulse or change color to show the thaw stage.
- **New edges:** EL light sheet -[enabled_by]-> Electroluminescent cavity panel; EL light sheet -[performs_function]-> Shows defrost progress to user; Shows defrost progress to user -[addresses_need]-> M8; EL light sheet -[partially_mitigates]-> X14
- **Rationale:** A cool, long-life EL light sheet that signals thaw progress lets users see when frozen food is ready, supporting M4 and removing the burnout problem.
- **Judge:** Replacing the lamp is a simple substitution but barely serves fast defrosting, and EL brightness inside a microwave cavity is doubtful.

### #1277 Ghost Lamp Vision: Replace the Interior Lamp With Microwave-Transparent Transparent Walls

- **Score:** 2.25 (relevance 1, novelty 2, feasibility 3, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M12_low_r03`
- **Target need:** M12 — Healthy diet (nutrient retention, less fat)
- **Cost:** 1,425 tokens per idea (run: 4,639 in + 2,486 out, 5 ideas)
- **Applied to:** C7 (Enamelled steel cooking cavity (~20 L)); F4 (Heats food via dielectric water-molecule vibration (FastHeating))
- **New elements:** Technology: Indium-tin-oxide transparent conductive window — Thin, transparent conductive coating on the door that blocks microwaves while letting light through, so food can be watched without an internal lamp.; Component: Door-window ITO mesh — Fine conductive mesh laminated into the door glass, shielding the cavity and passing visible light.
- **New edges:** Door-window ITO mesh -[enabled_by]-> Indium-tin-oxide transparent conductive window; Door-window ITO mesh -[resolves]-> Indium-tin-oxide transparent conductive window; Door-window ITO mesh -[relevant_to]-> A5; Door-window ITO mesh -[relevant_to]-> M12
- **Rationale:** Lets parents watch food brown and steam without opening the door, reducing heat loss and encouraging them to check that vegetables are cooked gently rather than overcooked.
- **Judge:** Transparent conductive door shielding is a real concept, but it barely serves the healthy-diet need and microwave doors already use metal mesh.

### #1276 Transparent Plasma-Free Cavity Using Conductive Glass Mesh

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M7_low_r05`
- **Target need:** M7 — Safe for family use (radiation, burns, electric shock)
- **Cost:** 1,402 tokens per idea (run: 4,480 in + 2,530 out, 5 ideas)
- **Applied to:** C8 (Hinged door with perforated metal mesh window); T5 (Sub-wavelength aperture shielding (Faraday cage effect)); C7 (Enamelled steel cooking cavity (~20 L)); T17 (Enamel / epoxy powder coating of steel)
- **New elements:** Technology: Indium-tin-oxide coated borosilicate window — Transparent conductive film reflects microwaves while passing visible light, removing the perforated mesh.; Component: Transparent conductive door window — Full-face window that seals RF without holes or sharp metal edges.; Function: Removes sharp mesh edges and cuts snag hazards — Smooth glass face has no exposed metal to scratch or arc.
- **New edges:** Indium-tin-oxide coated borosilicate window -[resolves]-> T5; Transparent conductive door window -[resolves]-> C8; Removes sharp mesh edges and cuts snag hazards -[addresses_need]-> M7; Transparent conductive door window -[partially_mitigates]-> X4
- **Rationale:** A continuous conductive glass face removes the mesh that children can poke fingers through and that snags clothing, and it reduces the metal-arcing risk that comes with exposed edges.
- **Judge:** ITO windows are physically plausible, but ITO's conductivity is poor at microwave shielding with good transparency, and the claimed safety gain over mesh is marginal; the 'plasma-free' title is also unexplained.

### #1275 Transparent Glass Cavity Replacing Lamp and Door Window

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M17_low_r03`
- **Target need:** M17 — Bake a birthday cake (prep tasks like melting butter)
- **Cost:** 1,536 tokens per idea (run: 4,975 in + 2,703 out, 5 ideas)
- **Applied to:** C6 (Mica waveguide cover); C7 (Enamelled steel cooking cavity (~20 L)); C14 (Power-level knob (5-step duty-cycle cam switch))
- **New elements:** Technology: Transparent conductive oxide (ITO) microwave-transparent film — Thin, see-through conductive coating that reflects visible light but passes microwaves within the mesh slot limit.; Component: Fully glazed cavity with embedded ITO window — Replaces the lamp and mesh window so the parent can watch butter melt without opening the door.
- **New edges:** Fully glazed cavity with embedded ITO window -[performs_function]-> Function: Melts butter gently without hot spots or superheating; Transparent conductive oxide (ITO) microwave-transparent film -[enabled_by]-> Fully glazed cavity with embedded ITO window; Fully glazed cavity with embedded ITO window -[resolves]-> C7; Fully glazed cavity with embedded ITO window -[partially_mitigates]-> X2
- **Rationale:** A fully visible cavity lets a parent monitor butter and chocolate melting in real time, catching scorching early during cake prep.
- **Judge:** A see-through cavity is of modest help for butter prep, and ITO shielding at microwave frequencies is questionable, since existing mesh windows already work.

### #1274 Transparent Conductive-Film Door Replacing Mesh Window

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition B (need slice), low effort · run `B_M6_low_r02`
- **Target need:** M6 — Simple operation with no learning curve
- **Cost:** 1,113 tokens per idea (run: 2,915 in + 2,652 out, 5 ideas)
- **Applied to:** C8 (Hinged door with perforated metal mesh window); T5 (Sub-wavelength aperture shielding (Faraday cage effect))
- **New elements:** Technology: Indium-tin-oxide coated glass viewing panel — A transparent conductive coating on glass reflects microwaves while passing visible light, with no mesh holes.; Component: Full-glass door panel — Wide clear door panel that shows the whole cavity and food without a perforated frame.; Function: Shows cavity contents across the whole door — Makes the food visible from any angle, so the user doesn't need to crouch or search for a view.
- **New edges:** Indium-tin-oxide coated glass viewing panel -[resolves]-> T5; Full-glass door panel -[resolves]-> C8; Full-glass door panel -[performs_function]-> Shows cavity contents across the whole door; Shows cavity contents across the whole door -[addresses_need]-> M6; Full-glass door panel -[partially_mitigates]-> X2
- **Rationale:** A clear, edge-to-edge window lets users see the food at a glance, which removes the need to learn where to look or how to check progress.
- **Judge:** ITO-coated glass as a microwave shield is a real idea, but it is costly, may not shield adequately, and does little for ease of operation.

### #1273 Thermochromic Thaw Window (Substitute the Interior Lamp)

- **Score:** 2.25 (relevance 2, novelty 2, feasibility 2, specificity 3)
- **Made by:** claude-haiku-5-5, condition A (full graph), low effort · run `A_M4_low_r05`
- **Target need:** M4 — Defrost frozen food quickly
- **Cost:** 3,091 tokens per idea (run: 10,910 in + 4,546 out, 5 ideas)
- **Applied to:** C17 (Interior lamp (20-25 W incandescent)); F11 (Illuminates cavity so the user can watch the food); X14 (Interior lamp burns out and is hard to replace); M8 (Human need for feedback (know when food is ready))
- **New elements:** Technology: Thermochromic and liquid-crystal indicator film — Film on the door window changes colour across temperature bands, showing frozen, thawing and ready zones.; Component: Thermochromic door window film — Printed film replaces the 20-25 W lamp as a no-power, never-burns-out viewing aid.; Function: Visual thaw-progress display — Shows the user at a glance which parts of the food are still frozen.
- **New edges:** Thermochromic and liquid-crystal indicator film -[rooted_in]-> D7; Thermochromic door window film -[enabled_by]-> Thermochromic and liquid-crystal indicator film; Thermochromic door window film -[performs_function]-> Visual thaw-progress display; Visual thaw-progress display -[addresses_need]-> M4; Visual thaw-progress display -[addresses_need]-> M8; Thermochromic door window film -[resolves]-> C17; Thermochromic door window film -[partially_mitigates]-> X14
- **Rationale:** A passive colour display tells the user when frozen food is ready for cooking, so they can judge thaw progress without opening the door or guessing the time.
- **Judge:** A thermochromic window would not show the temperature of food inside and does not speed up defrosting, so it is a weak fit.
