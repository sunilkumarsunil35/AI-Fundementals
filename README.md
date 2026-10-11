# AI-Fundementals: AI Fundamentals for SDETs (Python + Claude)

An 8-week study plan for test engineers who want to understand AI systems well enough to test them,
and to use AI in their own testing work. <!-- counts:start -->There are 10 topics and 121 exercises: 50 core exercises plus 71 practice exercises.<!-- counts:end --> Every
exercise comes three ways:

- an **exercise** in `src/exercises/`, with the task in its docstring and an empty body for you to fill in
- a worked **solution** in `src/solutions/`, with comments on the idea and why it matters for testing
- **tests** in `test/` that check either one

Everything runs offline in plain Python. Exercises that talk to a model take a `client`; the tests pass
`FakeClaude` (same shape as `anthropic.Anthropic()`), so the suite is free, fast and deterministic. You
can pass the real Claude client to the same functions when you want to see live answers.

## Set up

You need Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the tests

```bash
sh run-tests.sh            # checks the worked solutions; everything should pass
sh run-tests.sh --mine     # checks YOUR code in src/exercises
```

On Windows without `sh`, run `python -m pytest` and `python -m pytest --mine`.

The run ends with one line per topic. With `--mine`, an exercise you haven't written yet shows as
**todo**, not as a failure:

```
------------------------------ progress by topic ------------------------------
ok   ml_basics              5/5 passing, 0 todo, 0 failed
todo ml_basics_practice     2/7 passing, 5 todo, 0 failed
todo metrics                0/4 passing, 4 todo, 0 failed
...
```

Handy options (they go straight to pytest):

```bash
sh run-tests.sh --mine -k embeddings        # one topic
sh run-tests.sh --mine -k cosine            # one exercise
sh run-tests.sh --mine -x                   # stop at the first failure
```

CI runs the solutions on every push (`.github/workflows/ci.yml`).

## Layout

```
AI-Fundementals/
├── run-tests.sh                 run everything (add --mine for your own code)
├── requirements.txt             pytest (requirements-claude.txt adds the anthropic SDK)
├── src/
│   ├── common/                  fake_claude.py (offline Claude), claude.py (real client), target.py
│   ├── exercises/<topic>/       problems.py (core) + practice.py: you fill these in
│   └── solutions/<topic>/       problems.py (core) + practice.py: worked answers
├── test/                        test_<topic>.py + test_<topic>_practice.py per topic, conftest.py
├── claude/PROMPTS.md            how to learn with Claude: hint, review and quiz prompts
├── scripts/try_with_claude.py   run some solutions against the real Claude API
├── tools/                       make_exercises.py, build_catalog.py (keep exercises and tracker in sync)
└── tracker/index.html           daily progress tracker
```

Topics: `ml_basics/ metrics/ nlp/ embeddings/ prompts/ llm_testing/ rag/ agents/ guardrails/ sdet/`

**Practice tip:** read the exercise's docstring, write your answer in `src/exercises`, and run
`sh run-tests.sh --mine -k <function_name>`. Stuck for 15 minutes? Use the tracker's **Hint** button: it
opens Claude with a prompt that teaches the idea and gives one hint at a time, without the code. Once
your test passes, press **Review** and paste your code, then compare with the solution here.

## 8-week roadmap

Spend about an hour a day: two exercises, then a line in the tracker's daily log. Each week, redo two
exercises from earlier weeks without looking, and finish the week's SDET deliverable.

| Week | Topics                          | Goal                                                                    | SDET deliverable                                          |
| ---- | ------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------- |
| 1    | ML basics, evaluation metrics   | Explain train/test split, overfitting and precision vs recall           | Score a fake classifier: confusion matrix, P/R/F1         |
| 2    | Text, tokens, embeddings        | Know what a token is and why cosine similarity finds meaning            | Find duplicate bug reports with embeddings                |
| 3    | Prompt engineering with Claude  | Build Messages API requests; read answers safely (tags, JSON, stops)    | A QA-assistant system prompt plus a schema check          |
| 4    | Testing LLM apps                | Test non-deterministic output: golden sets, judges, retries, cost       | A golden-set regression suite that runs offline           |
| 5    | Retrieval-augmented generation  | Chunk, retrieve, cite; measure with recall@k and MRR                    | A RAG test that fails on made-up citations                |
| 6    | Tool use and agents             | Run the tool-use loop; keep it bounded, validated and approved          | An agent test that asserts the tool trajectory            |
| 7    | Safety, guardrails and cost     | Guard inputs and outputs; budget tokens and requests                    | A red-team suite with a canary secret                     |
| 8    | AI in the SDET process          | Use Claude across the test life cycle, with code that checks its work   | Generate, review and triage tests for one real feature    |

## Exercises by topic

<!-- problems:start -->
| Topic | Exercises | Source |
| ----- | --------- | ------ |
| ML basics | Mean and standard deviation, Min-max scaling, Train/test split with a seed, Predict with a linear model, Fit a line (least squares) | [exercise](src/exercises/ml_basics/problems.py) · [solution](src/solutions/ml_basics/problems.py) |
| Evaluation metrics | Accuracy, Confusion counts (TP/FP/FN/TN), Precision, recall and F1, MAE and RMSE | [exercise](src/exercises/metrics/problems.py) · [solution](src/solutions/metrics/problems.py) |
| Text and tokens | Normalise text, Word tokenizer, N-grams, Bag of words, TF-IDF | [exercise](src/exercises/nlp/problems.py) · [solution](src/solutions/nlp/problems.py) |
| Embeddings and similarity | Dot product, Vector length, Cosine similarity, Normalise a vector, Top-k similar | [exercise](src/exercises/embeddings/problems.py) · [solution](src/solutions/embeddings/problems.py) |
| Prompt engineering with Claude | Fill a prompt template, Build a Messages API request, Few-shot prompt, Read the response text, Ask Claude, Extract JSON from a reply | [exercise](src/exercises/prompts/problems.py) · [solution](src/solutions/prompts/problems.py) |
| Testing LLM apps | Missing keywords check, Run a golden data set, Consistency rate, Retry 429/529 with backoff, Parse a judge score | [exercise](src/exercises/llm_testing/problems.py) · [solution](src/solutions/llm_testing/problems.py) |
| Retrieval-augmented generation | Split documents into chunks, Keyword similarity score, Retrieve top-k chunks, Build a grounded prompt, Answer with RAG | [exercise](src/exercises/rag/problems.py) · [solution](src/solutions/rag/problems.py) |
| Tool use and agents | Define a tool, Read tool calls, Build a tool result, Execute tool calls safely, Agent loop | [exercise](src/exercises/agents/problems.py) · [solution](src/solutions/agents/problems.py) |
| Safety, guardrails and cost | Redact PII, Detect prompt injection, Estimate cost, Token bucket rate limiter | [exercise](src/exercises/guardrails/problems.py) · [solution](src/solutions/guardrails/problems.py) |
| AI in the SDET process | Boundary value analysis, Test case generation prompt, Parse generated test cases, Find flaky tests, Failure signature, Group failures | [exercise](src/exercises/sdet/problems.py) · [solution](src/solutions/sdet/problems.py) |
<!-- problems:end -->

## Practice exercises

One `practice.py` per topic, each with the same task docstring and its own tests.

<!-- practice:start -->
| Topic | Exercises | Source |
| ----- | --------- | ------ |
| ML basics | Z-score standardisation, One-hot encoding, Mean squared error loss, k-nearest neighbours, One gradient descent step, Logistic regression predict, k-fold cross-validation | [exercise](src/exercises/ml_basics/practice.py) · [solution](src/solutions/ml_basics/practice.py) |
| Evaluation metrics | Multi-class confusion matrix, Macro F1, Normalise an answer, Exact match for LLM answers, Token F1 (SQuAD), ROUGE-L, Pick the best threshold, pass@k | [exercise](src/exercises/metrics/practice.py) · [solution](src/solutions/metrics/practice.py) |
| Text and tokens | Estimate tokens, Split sentences, Remove stop words, Jaccard similarity, Edit distance, Chunk text with overlap, Byte-pair encoding merges | [exercise](src/exercises/nlp/practice.py) · [solution](src/solutions/nlp/practice.py) |
| Embeddings and similarity | Euclidean distance, Mean pooling, In-memory vector store, Maximal marginal relevance, Group similar vectors, Find duplicate bug reports | [exercise](src/exercises/embeddings/practice.py) · [solution](src/solutions/embeddings/practice.py) |
| Prompt engineering with Claude | Extract XML tags, Validate output against a schema, Structured outputs request, Classify with Claude, Prompt chaining, Handle stop reasons, System prompt for a QA assistant | [exercise](src/exercises/prompts/practice.py) · [solution](src/solutions/prompts/practice.py) |
| Testing LLM apps | LLM-as-judge prompt, LLM-as-judge, Semantic regression check, Latency p50/p95, Cost of a test run, Caching client, A/B compare two prompts, Assert answer length | [exercise](src/exercises/llm_testing/practice.py) · [solution](src/solutions/llm_testing/practice.py) |
| Retrieval-augmented generation | Extract citations, Catch made-up citations, Recall@k, Mean reciprocal rank, Groundedness score, BM25 ranking, Hybrid ranking, Fit chunks in a context budget | [exercise](src/exercises/rag/practice.py) · [solution](src/solutions/rag/practice.py) |
| Tool use and agents | Validate tool input, Safe calculator tool, Tool trajectory, Tool approval policy, Parse a plan, Tool schema from a function, Agent token budget | [exercise](src/exercises/agents/practice.py) · [solution](src/solutions/agents/practice.py) |
| Safety, guardrails and cost | Luhn check, Mask secrets in logs, Moderate output, Red-team with a canary, Trim chat history, Guarded Claude call | [exercise](src/exercises/guardrails/practice.py) · [solution](src/solutions/guardrails/practice.py) |
| AI in the SDET process | Pairwise test design, Self-healing locator, Risk-based test selection, Parse Gherkin, Seeded test data, Triage a failure with Claude, Review AI-written tests | [exercise](src/exercises/sdet/practice.py) · [solution](src/solutions/sdet/practice.py) |
<!-- practice:end -->

## Where AI fits in the SDET process

| Test life cycle step | Claude helps by…                                     | Your code must…                                          | Exercises                                     |
| -------------------- | ---------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------- |
| Requirements review  | Spotting gaps and ambiguities                        | Keep the requirement in tags; ask for a fixed format     | `test_case_prompt`, `system_prompt_for_tester` |
| Test design          | Drafting cases, Gherkin, boundary and pairwise ideas | Parse, de-duplicate and review before anything is saved  | `parse_test_cases`, `pairwise`, `review_generated_tests` |
| Test data            | Inventing realistic records                          | Seed it, validate it against a schema, redact real PII   | `generate_test_data`, `validate_schema`, `redact_pii` |
| Automation           | Writing and fixing test code                         | Run it; never trust code you haven't executed            | `heal_locator`, `safe_calculate`               |
| Execution            | Choosing what to run                                 | Rank by risk; throttle API calls; stay in budget         | `prioritize`, `TokenBucket`, `run_cost`        |
| Triage               | Classifying failures and summarising logs            | Group by signature first; fixed labels; humans for "unsure" | `group_failures`, `flaky_tests`, `triage`  |
| Testing AI features  | (it *is* the system under test)                      | Golden sets, judges, groundedness, red-teaming           | weeks 4–7                                      |

## Testing LLM apps cheat sheet

| To check that…                               | Use                                                                 |
| -------------------------------------------- | ------------------------------------------------------------------- |
| The answer mentions the right facts          | `missing_keywords()` or `token_f1()` against a reference            |
| The output has the right shape               | Structured outputs, then `validate_schema()` anyway                 |
| Free-text quality is good enough             | `llm_judge()` with a rubric; spot-check the judge by hand           |
| A prompt change didn't break old answers     | `run_golden_set()` and `regressions()` on every change              |
| The feature is stable                        | `consistency_rate()` over 5–10 runs                                 |
| RAG answers come from the documents          | `invalid_citations()`, `groundedness()`, `recall_at_k()`            |
| The agent did the right steps                | `tools_used()` on the conversation, not just the final text        |
| It can't be talked into leaking or harm      | `red_team()` with a canary, `looks_like_injection()`, `moderate()`  |
| Rate limits don't fail the run               | `call_with_retry()` on 429/529 only; never retry a 400              |
| The bill stays sane                          | `run_cost()` per run, `CachingClient` in CI, cheaper model for judges |

## Metrics cheat sheet

| Metric         | Question it answers                              | Watch out for                               |
| -------------- | ------------------------------------------------ | ------------------------------------------- |
| Accuracy       | How often is it right overall?                   | Misleading when classes are imbalanced      |
| Precision      | When it says "yes", how often is it right?       | Can be high while missing most cases        |
| Recall         | Of all real "yes" cases, how many did it find?   | Can be high by saying "yes" to everything   |
| F1 / macro F1  | Balance of the two (per class, then averaged)    | Hides which one is low: report both         |
| MAE / RMSE     | How far off are numeric predictions?             | RMSE >> MAE means a few huge misses         |
| Exact match    | Is the short answer the same after normalising?  | Too strict for long answers                 |
| Token F1, ROUGE-L | How much do the words overlap?                | Rewards copying, not correctness            |
| recall@k, MRR  | Did retrieval find the right chunk, and early?   | Needs labelled relevant chunks              |
| pass@k         | Does one of k attempts pass the tests?           | k > 1 hides how often a single try fails    |

## Learning with Claude

You use Claude as a tutor, not as an answer key. `claude/PROMPTS.md` has the full set; the short version:

1. **Learn**: tracker → **Hint ↗**. Claude explains the idea with a tiny example, why it matters for
   testing, then gives one hint at a time and holds back the code.
2. **Try**: write it in `src/exercises`, run `sh run-tests.sh --mine -k <name>`.
3. **Review**: tracker → **Review ↗**, paste your code. Then open the solution and compare.
4. **Explain back**: tell Claude the idea in three sentences and ask it to find the gap.
5. **Log it**: one line in the tracker's daily log: what you learned, what Claude had to correct.

To see the Claude exercises run for real (it costs a few cents):

```bash
pip install -r requirements-claude.txt
export ANTHROPIC_API_KEY=...            # or: ant auth login
python scripts/try_with_claude.py
```

## Python tips for this repo

- Inject what you can't control: the `client`, `sleep`, `clock`, the `embed` function. That one habit
  is what makes AI code testable.
- Read `response.content` by block type. Claude can return thinking and tool_use blocks before the
  text, so `content[0].text` is a bug waiting to happen.
- Check `stop_reason` before you trust the text: `max_tokens` means it was cut off.
- Seed every random choice (`random.Random(seed)`) so a failure can be replayed.
- `pytest.approx` for floats; never compare floats with `==`.

## Progress tracker

`tracker/index.html` is a daily tracker for every exercise above, with links to each exercise, its
solution, a doc page, and **Hint** / **Review** buttons that open Claude with a tutoring prompt for that
exercise. You can open it on a phone or a computer. Mark each exercise To do, Attempted, Done or Revise
and keep notes on it. Log minutes and a line about each study day, and see your roadmap week with its
goal and SDET deliverable, your streak, topic progress and a 12-week activity heatmap.

After adding or renaming an exercise in `src/solutions`, run:

```bash
python tools/make_exercises.py --new     # create the blank exercise file for a new topic
python tools/build_catalog.py            # refresh the tracker and the tables above
```
