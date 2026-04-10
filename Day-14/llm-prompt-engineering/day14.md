# Day 14 – LLM Fundamentals & Prompt Engineering

## Setup

```bash
pip install openai tiktoken python-dotenv
```

Create `.env` in this directory:
```
OPENAI_API_KEY=sk-...
```

Run either notebook with `jupyter notebook`.

## Deliverables

| File | Description |
|---|---|
| `llm-basics.ipynb` | API setup, tokens, temperature, system prompts, cost calculator |
| `prompt-engineering.ipynb` | 25 examples across 6 techniques with comparison matrix |
| `prompt-library/summarization.txt` | 5 reusable summarization templates |
| `prompt-library/extraction.txt` | 6 reusable extraction templates |
| `prompt-library/generation.txt` | 6 reusable generation templates |
| `prompt-library/reasoning.txt` | 6 CoT/reasoning templates |
| `prompt-library/few_shot.txt` | 5 few-shot framework templates |

## Key Concepts Covered

### Tokens & Context
- ~0.75 words per token in English; use `tiktoken` to count before sending
- Context window = input + output tokens combined; exceeding it truncates the prompt

### Temperature
- `0` = deterministic (use for extraction, classification, code)
- `0.7–1.0` = balanced (use for summarization, Q&A)
- `>1.0` = highly creative / unpredictable (rarely useful)

### Prompting Techniques

| Technique | When to use | Token cost |
|---|---|---|
| Zero-shot | Well-understood tasks | Low |
| Zero-shot + format constraint | Structured output needed | Low |
| Few-shot | Pattern/format tasks | Medium |
| Chain-of-thought | Math, logic, multi-step reasoning | High |
| Few-shot CoT | Complex reasoning + consistent format | High |

### Prompt Engineering Rules of Thumb
1. Specify output format explicitly (JSON, bullet list, single word)
2. Include audience and length constraints in summaries
3. Add "Think step by step" for reasoning tasks
4. For classifiers, enumerate valid labels in the prompt
5. 2–3 few-shot examples usually beats more; diversity matters more than quantity
6. `temperature=0` for reproducibility during testing; raise it only for creative tasks
7. Always test with 5+ varied inputs before shipping a prompt to production

### Cost Model
Cost = (input_tokens × input_price + output_tokens × output_price) / 1,000,000

| Model | Input (per 1M) | Output (per 1M) |
|---|---|---|
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4o | $2.50 | $10.00 |
| o1-mini | $1.10 | $4.40 |

Use `gpt-4o-mini` by default — cheapest and fast enough for most tasks.
