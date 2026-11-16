| Model | Ideas per top idea | $0 | $0.0012 (AI judge) | $0.50 (human) |
| --- | --- | --- | --- | --- |
| Haiku 5.5 | 16.5 [14.1–19.6] | 0.003 [0.002–0.003] | **0.023** [0.019–0.027] | 8.26 [7.05–9.80] |
| Opus 5.5 | 7.4 [6.7–8.2] | 0.049 [0.045–0.055] | 0.058 [0.053–0.065] | **3.73** [3.38–4.14] |
| Fable 5.1 | 6.8 [6.3–7.4] | 0.105 [0.096–0.115] | 0.113 [0.104–0.124] | **3.50** [3.24–3.81] |
| DeepSeek V4.1 Flash | 18.7 [16.4–21.4] | **0.002** [0.002–0.003] | **0.025** [0.022–0.028] | 9.36 [8.22–10.73] |
| DeepSeek V4 Pro | 15.7 [13.6–18.4] | 0.010 [0.008–0.012] | 0.029 [0.025–0.034] | 7.87 [6.83–9.20] |
| Qwen3.8 Flash | 24.4 [19.6–31.2] | 0.006 [0.005–0.008] | 0.035 [0.028–0.046] | 12.20 [9.81–15.63] |

Net cost per top idea (USD) = (generation cost + screening cost x ideas) / top ideas, pooled over the four representations (M6, 50 ideas per call). 95% intervals: 2,000 bootstrap resamples of calls within representation. Generation at list price; $0.0012 is the measured cost of the automated judge per idea; $0.50 is about 30 seconds of human reading at $60 an hour. Bold: cheapest, or indistinguishable from the cheapest.

Opus 5.5 becomes cheaper than Haiku 5.5 once screening costs more than $0.0051 per idea (95% CI $0.0036–$0.0075).

Fable 5.1 becomes cheaper than Haiku 5.5 once screening costs more than $0.0105 per idea (95% CI $0.0077–$0.0145).

DeepSeek V4.1 Flash against Haiku 5.5: cheaper only while screening costs less than $0.0003 per idea.

DeepSeek V4 Pro becomes cheaper than Haiku 5.5 once screening costs more than $0.0090 per idea (95% CI $0.0012–$0.0760).

Qwen3.8 Flash against Haiku 5.5: dearer at every screening cost.
