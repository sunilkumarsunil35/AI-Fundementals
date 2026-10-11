"""Regenerates the exercise list in tracker/index.html and the exercise tables in README.md from
src/solutions, so the tracker never drifts from the code.

    python tools/build_catalog.py           update both files
    python tools/build_catalog.py --check   fail if either is out of date (CI runs this)

Titles, difficulty and doc links live in META below. The task text is the first sentence(s) of each
function's docstring.
"""

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS = ROOT / "src" / "solutions"
TRACKER = ROOT / "tracker" / "index.html"
README = ROOT / "README.md"

CLAUDE_DOCS = "https://platform.claude.com/docs/en/"
WIKI = "https://en.wikipedia.org/wiki/"

# id, display name, default doc link for the topic
TOPICS = [
    ("ml_basics", "ML basics", "https://developers.google.com/machine-learning/crash-course"),
    ("metrics", "Evaluation metrics", "https://scikit-learn.org/stable/modules/model_evaluation.html"),
    ("nlp", "Text and tokens", "https://huggingface.co/learn/llm-course/chapter6/1"),
    ("embeddings", "Embeddings and similarity", CLAUDE_DOCS + "build-with-claude/embeddings"),
    ("prompts", "Prompt engineering with Claude", CLAUDE_DOCS + "build-with-claude/prompt-engineering/overview"),
    ("llm_testing", "Testing LLM apps", CLAUDE_DOCS + "test-and-evaluate/develop-tests"),
    ("rag", "Retrieval-augmented generation", "https://www.anthropic.com/engineering/contextual-retrieval"),
    ("agents", "Tool use and agents", CLAUDE_DOCS + "agents-and-tools/tool-use/overview"),
    ("guardrails", "Safety, guardrails and cost", CLAUDE_DOCS + "test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks"),
    ("sdet", "AI in the SDET process", "https://docs.pytest.org/en/stable/how-to/parametrize.html"),
]

# function or class name -> (title, difficulty E/M/H, optional doc link overriding the topic's)
META = {
    # ml_basics
    "mean_and_std": ("Mean and standard deviation", "E", None),
    "min_max_scale": ("Min-max scaling", "E", None),
    "train_test_split": ("Train/test split with a seed", "E", None),
    "predict_linear": ("Predict with a linear model", "E", None),
    "fit_line": ("Fit a line (least squares)", "M", WIKI + "Simple_linear_regression"),
    "z_score": ("Z-score standardisation", "E", None),
    "one_hot": ("One-hot encoding", "E", None),
    "mse_loss": ("Mean squared error loss", "E", None),
    "knn_predict": ("k-nearest neighbours", "M", WIKI + "K-nearest_neighbors_algorithm"),
    "gradient_descent_step": ("One gradient descent step", "M", WIKI + "Gradient_descent"),
    "logistic_predict": ("Logistic regression predict", "M", WIKI + "Logistic_regression"),
    "k_fold_indices": ("k-fold cross-validation", "M", WIKI + "Cross-validation_(statistics)"),
    # metrics
    "accuracy": ("Accuracy", "E", None),
    "confusion_counts": ("Confusion counts (TP/FP/FN/TN)", "E", None),
    "precision_recall_f1": ("Precision, recall and F1", "E", None),
    "mae_rmse": ("MAE and RMSE", "E", None),
    "confusion_matrix": ("Multi-class confusion matrix", "M", None),
    "macro_f1": ("Macro F1", "M", None),
    "normalize_answer": ("Normalise an answer", "E", None),
    "exact_match": ("Exact match for LLM answers", "E", None),
    "token_f1": ("Token F1 (SQuAD)", "M", None),
    "rouge_l": ("ROUGE-L", "H", WIKI + "ROUGE_(metric)"),
    "best_threshold": ("Pick the best threshold", "M", None),
    "pass_at_k": ("pass@k", "M", "https://arxiv.org/abs/2107.03374"),
    # nlp
    "normalize_text": ("Normalise text", "E", None),
    "tokenize": ("Word tokenizer", "E", None),
    "ngrams": ("N-grams", "E", None),
    "bag_of_words": ("Bag of words", "M", WIKI + "Bag-of-words_model"),
    "tf_idf": ("TF-IDF", "M", WIKI + "Tf%E2%80%93idf"),
    "estimate_tokens": ("Estimate tokens", "E", CLAUDE_DOCS + "build-with-claude/token-counting"),
    "sentence_split": ("Split sentences", "E", None),
    "remove_stopwords": ("Remove stop words", "E", None),
    "jaccard": ("Jaccard similarity", "E", WIKI + "Jaccard_index"),
    "edit_distance": ("Edit distance", "M", WIKI + "Levenshtein_distance"),
    "chunk_words": ("Chunk text with overlap", "M", None),
    "bpe_merges": ("Byte-pair encoding merges", "H", "https://huggingface.co/learn/llm-course/chapter6/5"),
    # embeddings
    "dot": ("Dot product", "E", None),
    "norm": ("Vector length", "E", None),
    "cosine_similarity": ("Cosine similarity", "E", WIKI + "Cosine_similarity"),
    "normalize": ("Normalise a vector", "E", None),
    "top_k_similar": ("Top-k similar", "M", None),
    "euclidean_distance": ("Euclidean distance", "E", None),
    "mean_pool": ("Mean pooling", "E", None),
    "VectorStore": ("In-memory vector store", "M", None),
    "mmr": ("Maximal marginal relevance", "H", None),
    "group_similar": ("Group similar vectors", "M", None),
    "find_duplicates": ("Find duplicate bug reports", "M", None),
    # prompts
    "fill_template": ("Fill a prompt template", "E", None),
    "build_request": ("Build a Messages API request", "E", CLAUDE_DOCS + "build-with-claude/working-with-messages"),
    "few_shot_prompt": ("Few-shot prompt", "E", CLAUDE_DOCS + "build-with-claude/prompt-engineering/claude-prompting-best-practices"),
    "response_text": ("Read the response text", "E", None),
    "ask_claude": ("Ask Claude", "E", None),
    "extract_json": ("Extract JSON from a reply", "M", None),
    "extract_tag": ("Extract XML tags", "E", CLAUDE_DOCS + "build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags"),
    "validate_schema": ("Validate output against a schema", "H", "https://json-schema.org/understanding-json-schema/reference"),
    "structured_request": ("Structured outputs request", "M", CLAUDE_DOCS + "build-with-claude/structured-outputs"),
    "classify": ("Classify with Claude", "M", None),
    "summarize_then_extract": ("Prompt chaining", "M", CLAUDE_DOCS + "build-with-claude/prompt-engineering/claude-prompting-best-practices#chain-complex-prompts"),
    "check_stop_reason": ("Handle stop reasons", "M", CLAUDE_DOCS + "build-with-claude/handling-stop-reasons"),
    "system_prompt_for_tester": ("System prompt for a QA assistant", "E", CLAUDE_DOCS + "build-with-claude/prompt-engineering/claude-prompting-best-practices#give-claude-a-role"),
    # llm_testing
    "missing_keywords": ("Missing keywords check", "E", None),
    "run_golden_set": ("Run a golden data set", "M", None),
    "consistency_rate": ("Consistency rate", "M", None),
    "call_with_retry": ("Retry 429/529 with backoff", "M", CLAUDE_DOCS + "api/errors"),
    "parse_judge_score": ("Parse a judge score", "E", None),
    "judge_prompt": ("LLM-as-judge prompt", "E", None),
    "llm_judge": ("LLM-as-judge", "M", None),
    "regressions": ("Semantic regression check", "M", None),
    "latency_stats": ("Latency p50/p95", "E", None),
    "run_cost": ("Cost of a test run", "E", CLAUDE_DOCS + "about-claude/pricing"),
    "CachingClient": ("Caching client", "M", None),
    "ab_compare": ("A/B compare two prompts", "M", None),
    "assert_length": ("Assert answer length", "E", None),
    # rag
    "split_documents": ("Split documents into chunks", "M", None),
    "keyword_score": ("Keyword similarity score", "E", None),
    "retrieve": ("Retrieve top-k chunks", "M", None),
    "build_rag_prompt": ("Build a grounded prompt", "E", None),
    "answer_with_rag": ("Answer with RAG", "M", None),
    "extract_citations": ("Extract citations", "E", None),
    "invalid_citations": ("Catch made-up citations", "E", None),
    "recall_at_k": ("Recall@k", "E", None),
    "mean_reciprocal_rank": ("Mean reciprocal rank", "M", WIKI + "Mean_reciprocal_rank"),
    "groundedness": ("Groundedness score", "M", None),
    "bm25_scores": ("BM25 ranking", "H", WIKI + "Okapi_BM25"),
    "hybrid_rank": ("Hybrid ranking", "M", None),
    "context_budget": ("Fit chunks in a context budget", "E", None),
    # agents
    "make_tool": ("Define a tool", "E", None),
    "tool_calls": ("Read tool calls", "E", None),
    "tool_result": ("Build a tool result", "E", None),
    "execute_tool_calls": ("Execute tool calls safely", "M", None),
    "agent_loop": ("Agent loop", "H", CLAUDE_DOCS + "agents-and-tools/tool-use/define-tools"),
    "validate_tool_input": ("Validate tool input", "M", None),
    "safe_calculate": ("Safe calculator tool", "M", None),
    "tools_used": ("Tool trajectory", "E", None),
    "apply_policy": ("Tool approval policy", "M", None),
    "parse_plan": ("Parse a plan", "E", None),
    "tool_from_function": ("Tool schema from a function", "H", None),
    "budgeted_steps": ("Agent token budget", "E", None),
    # guardrails
    "redact_pii": ("Redact PII", "M", None),
    "looks_like_injection": ("Detect prompt injection", "E", None),
    "estimate_cost": ("Estimate cost", "E", CLAUDE_DOCS + "about-claude/pricing"),
    "TokenBucket": ("Token bucket rate limiter", "M", CLAUDE_DOCS + "api/rate-limits"),
    "luhn_valid": ("Luhn check", "E", WIKI + "Luhn_algorithm"),
    "mask_secrets": ("Mask secrets in logs", "M", None),
    "moderate": ("Moderate output", "E", None),
    "red_team": ("Red-team with a canary", "M", None),
    "trim_history": ("Trim chat history", "M", None),
    "guarded_ask": ("Guarded Claude call", "H", None),
    # sdet
    "boundary_values": ("Boundary value analysis", "E", WIKI + "Boundary-value_analysis"),
    "test_case_prompt": ("Test case generation prompt", "E", None),
    "parse_test_cases": ("Parse generated test cases", "M", None),
    "flaky_tests": ("Find flaky tests", "M", None),
    "failure_signature": ("Failure signature", "M", None),
    "group_failures": ("Group failures", "M", None),
    "pairwise": ("Pairwise test design", "H", WIKI + "All-pairs_testing"),
    "heal_locator": ("Self-healing locator", "M", None),
    "prioritize": ("Risk-based test selection", "M", None),
    "parse_gherkin": ("Parse Gherkin", "M", "https://cucumber.io/docs/gherkin/reference/"),
    "generate_test_data": ("Seeded test data", "M", None),
    "triage": ("Triage a failure with Claude", "M", None),
    "review_generated_tests": ("Review AI-written tests", "M", None),
}


def _task(doc: str) -> str:
    text = " ".join(doc.split())
    return text


def catalog():
    out = []
    names = dict((t, n) for t, n, _ in TOPICS)
    for topic, name, topic_doc in TOPICS:
        items = []
        for kind in ("problems", "practice"):
            tree = ast.parse((SOLUTIONS / topic / f"{kind}.py").read_text())
            for node in tree.body:
                if not isinstance(node, (ast.FunctionDef, ast.ClassDef)) or node.name.startswith("_"):
                    continue
                if node.name not in META:
                    raise SystemExit(f"tools/build_catalog.py: add {node.name} ({topic}/{kind}.py) to META")
                title, diff, doc = META[node.name]
                items.append({"fn": node.name, "title": title, "diff": diff, "kind": kind,
                              "doc": doc or topic_doc, "task": _task(ast.get_docstring(node) or "")})
        out.append({"id": topic, "name": names[topic], "items": items})
    return out


def tracker_html(cat):
    lines = TRACKER.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("  const CATALOG = "):
            lines[i] = "  const CATALOG = " + json.dumps(cat, ensure_ascii=False) + ";"
            return "\n".join(lines) + "\n"
    raise SystemExit("tracker/index.html has no 'const CATALOG = ' line")


def _table(cat, kind):
    rows = ["| Topic | Exercises | Source |", "| ----- | --------- | ------ |"]
    for t in cat:
        titles = [it["title"] for it in t["items"] if it["kind"] == kind]
        src = f"[exercise](src/exercises/{t['id']}/{kind}.py) · [solution](src/solutions/{t['id']}/{kind}.py)"
        rows.append(f"| {t['name']} | {', '.join(titles)} | {src} |")
    return rows


def readme_md(cat):
    text = README.read_text()
    for kind in ("problems", "practice"):
        start, end = f"<!-- {kind}:start -->", f"<!-- {kind}:end -->"
        if start not in text or end not in text:
            raise SystemExit(f"README.md is missing the {start} / {end} markers")
        head, rest = text.split(start, 1)
        _, tail = rest.split(end, 1)
        text = head + start + "\n" + "\n".join(_table(cat, kind)) + "\n" + end + tail
    total = sum(len(t["items"]) for t in cat)
    core = sum(1 for t in cat for it in t["items"] if it["kind"] == "problems")
    head, rest = text.split("<!-- counts:start -->", 1)
    _, tail = rest.split("<!-- counts:end -->", 1)
    counts = f"There are {len(cat)} topics and {total} exercises: {core} core exercises plus {total - core} practice exercises."
    return head + "<!-- counts:start -->" + counts + "<!-- counts:end -->" + tail


def main(argv):
    cat = catalog()
    wanted = {TRACKER: tracker_html(cat), README: readme_md(cat)}
    if "--check" in argv:
        stale = [p.name for p, s in wanted.items() if p.read_text() != s]
        if stale:
            print("Out of date:", ", ".join(stale), "- run: python tools/build_catalog.py")
            return 1
        print("tracker and README are up to date")
        return 0
    for p, s in wanted.items():
        p.write_text(s)
    print(f"updated tracker/index.html and README.md ({sum(len(t['items']) for t in cat)} exercises)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
