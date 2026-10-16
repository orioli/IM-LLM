# Persona as a factor: results

Top idea = quality score ≥ 4 (4 criteria, same prompt as the main study). Patentable idea = patentability ≥ 4. Yield = hits per 100k tokens, 95% CI from resampling calls within need.

## Per cell

| Persona | Effort | Representation | Calls | Top-idea rate | Yield [95% CI] | Mean novelty | Patentable rate | Patentable yield [95% CI] | Mean patentability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Innovation engineer | medium | B · need slice | 45 | 11.6% | 6.4 [4.5–8.3] | 3.30 | 0.4% | 0.2 [0.0–0.7] | 2.13 |
| Innovation engineer | medium | C · no graph | 45 | 10.2% | 10.0 [6.6–13.8] | 3.35 | 0.9% | 0.9 [0.0–2.2] | 2.20 |
| Innovation engineer | high | B · need slice | 43 | 15.4% | 5.6 [4.2–7.1] | 3.29 | 0.5% | 0.2 [0.0–0.5] | 2.17 |
| Innovation engineer | high | C · no graph | 45 | 8.4% | 5.2 [3.1–7.4] | 3.32 | 0.9% | 0.5 [0.0–1.4] | 2.24 |
| Innovation engineer | pooled | B · need slice | 88 | 13.4% | 5.9 [4.8–7.2] | 3.30 | 0.5% | 0.2 [0.0–0.5] | 2.15 |
| Innovation engineer | pooled | C · no graph | 90 | 9.3% | 7.0 [5.1–9.1] | 3.34 | 0.9% | 0.7 [0.2–1.4] | 2.22 |
| Lateral thinker | medium | B · need slice | 45 | 10.2% | 5.4 [3.6–7.3] | 3.24 | 1.3% | 0.7 [0.0–1.8] | 2.16 |
| Lateral thinker | medium | C · no graph | 43 | 4.2% | 3.9 [1.7–6.6] | 3.22 | 1.0% | 0.9 [0.0–2.2] | 2.13 |
| Lateral thinker | high | B · need slice | 42 | 11.9% | 4.0 [2.9–5.1] | 3.23 | 0.0% | 0.0 [0.0–0.0] | 2.18 |
| Lateral thinker | high | C · no graph | 44 | 7.4% | 4.0 [2.6–5.4] | 3.24 | 0.5% | 0.2 [0.0–0.8] | 2.20 |
| Lateral thinker | pooled | B · need slice | 87 | 11.0% | 4.6 [3.6–5.6] | 3.23 | 0.7% | 0.3 [0.0–0.8] | 2.17 |
| Lateral thinker | pooled | C · no graph | 87 | 5.8% | 3.9 [2.7–5.2] | 3.23 | 0.7% | 0.5 [0.0–1.1] | 2.16 |
| Patent-focused | medium | B · need slice | 44 | 11.8% | 5.9 [4.3–7.5] | 3.32 | 0.9% | 0.5 [0.0–1.1] | 2.16 |
| Patent-focused | medium | C · no graph | 43 | 8.2% | 7.2 [4.4–9.9] | 3.32 | 1.3% | 1.2 [0.0–2.4] | 2.31 |
| Patent-focused | high | B · need slice | 41 | 18.0% | 5.7 [4.4–7.1] | 3.35 | 0.5% | 0.2 [0.0–0.5] | 2.20 |
| Patent-focused | high | C · no graph | 45 | 7.1% | 3.7 [2.2–5.3] | 3.35 | 1.3% | 0.7 [0.0–1.4] | 2.24 |
| Patent-focused | pooled | B · need slice | 85 | 14.8% | 5.8 [4.8–6.8] | 3.33 | 0.7% | 0.3 [0.0–0.6] | 2.18 |
| Patent-focused | pooled | C · no graph | 88 | 7.7% | 4.9 [3.6–6.4] | 3.33 | 1.3% | 0.9 [0.3–1.6] | 2.28 |

## Echo of the persona exemplars

Share of ideas that repeat each persona's exemplar (Eurostar Wi-Fi; Dyson cyclone). The engineer, who sees neither, is the baseline for chance mentions.

| Persona | Effort | Representation | Echo of Eurostar / Wi-Fi | Echo of Dyson / cyclone |
| --- | --- | --- | --- | --- |
| Innovation engineer | medium | B · need slice | 0.0% | 0.0% |
| Innovation engineer | medium | C · no graph | 0.9% | 0.0% |
| Innovation engineer | high | B · need slice | 0.0% | 0.0% |
| Innovation engineer | high | C · no graph | 0.4% | 0.0% |
| Innovation engineer | pooled | B · need slice | 0.0% | 0.0% |
| Innovation engineer | pooled | C · no graph | 0.7% | 0.0% |
| Lateral thinker | medium | B · need slice | 1.3% | 0.0% |
| Lateral thinker | medium | C · no graph | 0.9% | 0.0% |
| Lateral thinker | high | B · need slice | 1.0% | 0.0% |
| Lateral thinker | high | C · no graph | 1.8% | 0.0% |
| Lateral thinker | pooled | B · need slice | 1.1% | 0.0% |
| Lateral thinker | pooled | C · no graph | 1.4% | 0.0% |
| Patent-focused | medium | B · need slice | 0.0% | 0.0% |
| Patent-focused | medium | C · no graph | 0.0% | 0.0% |
| Patent-focused | high | B · need slice | 0.0% | 0.0% |
| Patent-focused | high | C · no graph | 0.9% | 0.0% |
| Patent-focused | pooled | B · need slice | 0.0% | 0.0% |
| Patent-focused | pooled | C · no graph | 0.5% | 0.0% |

## Interaction: does the slice help some personas more than others?

Ratio > 1: the need slice is more efficient than no graph for that persona.

| Measure | Persona | Effort | Yield B | Yield C | B ÷ C [95% CI] |
| --- | --- | --- | --- | --- | --- |
| top ideas | Innovation engineer | medium | 6.4 | 10.0 | 0.64 [0.39–1.07] |
| patentable ideas | Innovation engineer | medium | 0.2 | 0.9 | 0.28 [0.00–1.66] |
| top ideas | Innovation engineer | high | 5.6 | 5.2 | 1.09 [0.69–1.88] |
| patentable ideas | Innovation engineer | high | 0.2 | 0.5 | 0.31 [0.00–1.30] |
| top ideas | Innovation engineer | pooled | 5.9 | 7.0 | 0.84 [0.60–1.22] |
| patentable ideas | Innovation engineer | pooled | 0.2 | 0.7 | 0.30 [0.00–1.73] |
| top ideas | Lateral thinker | medium | 5.4 | 3.9 | 1.39 [0.76–3.35] |
| patentable ideas | Lateral thinker | medium | 0.7 | 0.9 | 0.81 [0.00–3.29] |
| top ideas | Lateral thinker | high | 4.0 | 4.0 | 1.01 [0.66–1.69] |
| patentable ideas | Lateral thinker | high | 0.0 | 0.2 | 0.00 [0.00–0.00] |
| top ideas | Lateral thinker | pooled | 4.6 | 3.9 | 1.16 [0.80–1.76] |
| patentable ideas | Lateral thinker | pooled | 0.3 | 0.5 | 0.60 [0.00–3.04] |
| top ideas | Patent-focused | medium | 5.9 | 7.2 | 0.82 [0.51–1.40] |
| patentable ideas | Patent-focused | medium | 0.5 | 1.2 | 0.38 [0.00–2.22] |
| top ideas | Patent-focused | high | 5.7 | 3.7 | 1.55 [1.03–2.61] |
| patentable ideas | Patent-focused | high | 0.2 | 0.7 | 0.22 [0.00–1.33] |
| top ideas | Patent-focused | pooled | 5.8 | 4.9 | 1.17 [0.86–1.66] |
| patentable ideas | Patent-focused | pooled | 0.3 | 0.9 | 0.31 [0.00–1.21] |

Personas differ in the slice's benefit if their B ÷ C intervals do not overlap; overlapping intervals are not evidence of no difference.
