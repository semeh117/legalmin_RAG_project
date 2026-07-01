import sys
import os
import time
import requests

# ────────────────────────────────────────────────────────────────
# Path setup
# ────────────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ────────────────────────────────────────────────────────────────
# Environment
# ────────────────────────────────────────────────────────────────
from dotenv import load_dotenv

ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".env"
)
load_dotenv(ENV_PATH)

assert os.getenv("GROQ_API_KEY"), "GROQ_API_KEY not found in .env"
print("✅ GROQ_API_KEY loaded (used for pipeline answers only)")

# ────────────────────────────────────────────────────────────────
# DeepEval
# ────────────────────────────────────────────────────────────────
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import (
    ContextualRecallMetric,
    ContextualPrecisionMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric,
)

# ────────────────────────────────────────────────────────────────
# Your pipeline
# ────────────────────────────────────────────────────────────────
from ingestion import extract_text_from_pdf, split_into_chunks
from embeddings import embed_chunks
from retrieval import store, retrieve
from llm import get_answer
from evaluation.golden_data import GOLDEN_DATASET


# ────────────────────────────────────────────────────────────────
# Ollama evaluator — local, free, unlimited. Separate from Groq
# (the pipeline LLM) so no quota ever competes.
# ────────────────────────────────────────────────────────────────
class OllamaEvaluator(DeepEvalBaseLLM):
    """Local evaluator using Ollama. Uses llama3.1:8b with forced
    JSON mode + low temperature for reliable structured output,
    which DeepEval's metrics require to parse verdicts correctly."""

    def __init__(self):
        self.model_id = "llama3.1:8b"
        self.url = "http://localhost:11434/api/generate"

    def get_model_name(self) -> str:
        return self.model_id

    def load_model(self):
        return None

    def generate(self, prompt: str) -> str:
        start = time.perf_counter()
        response = requests.post(
            self.url,
            json={
                "model": self.model_id,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1}
            },
            timeout=300  # local 8B models can be slow per call
        )
        elapsed = time.perf_counter() - start
        print(f"    ⚡ Ollama response in {elapsed:.2f}s")
        return response.json()["response"]

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)


# ===============================================================
# Step 0 — Verify Ollama is reachable before doing anything else
# ===============================================================
try:
    requests.get("http://localhost:11434", timeout=3)
    print("✅ Ollama is running")
except requests.exceptions.ConnectionError:
    raise SystemExit(
        "❌ Ollama is not running. Start it first with: ollama serve\n"
        "   (in a separate terminal, then rerun this script)"
    )


# ===============================================================
# Step 1 — Ingest document
# ===============================================================
PDF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "sample_docs",
    "Data_Engineer_Employment_Contract.pdf",
)

print(f"\n📄 Ingesting contract from: {PDF_PATH}")
pages = extract_text_from_pdf(PDF_PATH)
chunks = split_into_chunks(pages)
embedded = embed_chunks(chunks)
store(embedded)
print(f"✅ Stored {len(chunks)} chunks")


# ===============================================================
# Step 2 — Build test cases (uses Groq via get_answer)
# ===============================================================
print("\n🔨 Building test cases...")
test_cases = []

for i, entry in enumerate(GOLDEN_DATASET):
    print(f"  [{i+1}/{len(GOLDEN_DATASET)}] {entry['question'][:60]}...")

    retrieved_chunks = retrieve(entry["question"])
    answer = get_answer(entry["question"], retrieved_chunks)

    test_case = LLMTestCase(
        input=entry["question"],
        actual_output=answer,
        expected_output=entry["expected_answer"],
        retrieval_context=retrieved_chunks["documents"][0],
        expected_context=[entry["expected_context"]],
    )
    test_cases.append(test_case)

print(f"✅ Built {len(test_cases)} test cases")


# ===============================================================
# DEBUG MODE — run only 2 cases first. Change to full list once stable.
# ===============================================================
DEBUG_LIMIT = 5
test_cases = test_cases[:DEBUG_LIMIT]
print(f"⚠️  Debug mode: running {len(test_cases)} of {len(GOLDEN_DATASET)} cases")


# ===============================================================
# Step 3 — Define metrics (Ollama scores them, locally)
# ===============================================================
evaluator = OllamaEvaluator()

metrics = [
    ContextualRecallMetric(threshold=0.5, model=evaluator),
    ContextualPrecisionMetric(threshold=0.5, model=evaluator),
    FaithfulnessMetric(threshold=0.5, model=evaluator),
    AnswerRelevancyMetric(threshold=0.5, model=evaluator),
]


# ===============================================================
# Step 4 — Run evaluation
# One metric at a time, sequentially — avoids overloading the GPU
# with concurrent requests, which caused timeouts previously.
# ===============================================================
print("\n🚀 Starting evaluation (this will be slower than a cloud API — that's expected)\n")

for i, test_case in enumerate(test_cases):
    print("=" * 70)
    print(f"TEST CASE {i+1}/{len(test_cases)}: {test_case.input[:60]}")
    print("=" * 70)

    for metric in metrics:
        print(f"\nRunning {metric.__class__.__name__}...")
        start = time.perf_counter()
        try:
            evaluate([test_case], [metric])
            elapsed = time.perf_counter() - start
            print(f"✅ Finished in {elapsed:.2f}s")
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"❌ Failed after {elapsed:.2f}s — {type(e).__name__}: {e}")
            raise
import json

results_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "eval_results.json"
)

output = []
for tc in test_cases:
    output.append({
        "question": tc.input,
        "actual_output": tc.actual_output,
        "scores": {
            metric.__class__.__name__: getattr(metric, "score", None)
            for metric in metrics
        }
    })

with open(results_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n💾 Results saved to {results_path}")
print("\n🎉 Evaluation complete.")