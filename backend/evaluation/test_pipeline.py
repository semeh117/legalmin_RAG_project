import sys
import os
import time
import requests
import asyncio
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
assert os.getenv("GLM_API_KEY"), "GLM_API_KEY not found in .env"
print("✅ GROQ_API_KEY loaded")
print("✅ GLM_API_KEY loaded")

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
# GLM evaluator (replaces Groq/Ollama for scoring only)
# ────────────────────────────────────────────────────────────────



class GLMEvaluator(DeepEvalBaseLLM):

    def __init__(self):
        self.model_id = "glm-4-flash"
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.api_key = os.getenv("GLM_API_KEY")

    def get_model_name(self):
        return self.model_id

    def load_model(self):
        return None

    def generate(self, prompt: str) -> str:
        start = time.perf_counter()

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model_id,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0
            }
        )

        data = response.json()

        elapsed = time.perf_counter() - start
        print(f"⚡ GLM response in {elapsed:.2f}s")

        return data["choices"][0]["message"]["content"]

    async def a_generate(self, prompt: str) -> str:
        return await asyncio.to_thread(self.generate, prompt)

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
# DEBUG MODE — limit to first N cases while confirming Gemini works
# Remove this block once stable to run the full 10.
# ===============================================================
DEBUG_LIMIT = 5
test_cases = test_cases[:DEBUG_LIMIT]
print(f"⚠️  Debug mode: running {len(test_cases)} of {len(GOLDEN_DATASET)} cases")


# ===============================================================
# Step 3 — Define metrics (uses GLM for scoring)
# ===============================================================
evaluator = GLMEvaluator()

metrics = [
    ContextualRecallMetric(threshold=0.5, model=evaluator),
    ContextualPrecisionMetric(threshold=0.5, model=evaluator),
    FaithfulnessMetric(threshold=0.5, model=evaluator),
    AnswerRelevancyMetric(threshold=0.5, model=evaluator),
]


# ===============================================================
# Step 4 — Run evaluation (one metric at a time, for clear progress)
# ===============================================================
print("\n🚀 Starting evaluation\n")

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

    time.sleep(1)  # small buffer between cases for Gemini rate limits

print("\n🎉 Evaluation complete.")