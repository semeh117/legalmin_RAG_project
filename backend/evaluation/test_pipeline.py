import sys
import os

# Add backend/ to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env from project root
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

# Verify key loaded
print("OPENAI KEY FOUND:", os.getenv("OPENAI_API_KEY") is not None)
print("GROQ KEY FOUND:", os.getenv("GROQ_API_KEY") is not None)

from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    ContextualRecallMetric,
    ContextualPrecisionMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric
)

from ingestion import extract_text_from_pdf, split_into_chunks
from embeddings import embed_chunks
from retrieval import store, retrieve
from llm import get_answer
from evaluation.golden_data import GOLDEN_DATASET

# Step 1: ingest the contract
print("Ingesting contract...")
pages = extract_text_from_pdf(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "sample_docs",
        "Data_Engineer_Employment_Contract.pdf"
    )
)
chunks = split_into_chunks(pages)
embedded = embed_chunks(chunks)
store(embedded)
print(f"Ingested {len(chunks)} chunks successfully.")

# Step 2: build test cases
print("Building test cases...")
test_cases = []

for entry in GOLDEN_DATASET:
    retrieved_chunks = retrieve(entry["question"])
    answer = get_answer(entry["question"], retrieved_chunks)

    test_case = LLMTestCase(
        input=entry["question"],
        actual_output=answer,
        expected_output=entry["expected_answer"],
        retrieval_context=retrieved_chunks["documents"][0],
        expected_context=[entry["expected_context"]]
    )
    test_cases.append(test_case)

print(f"Built {len(test_cases)} test cases.")

# Step 3: define metrics
from deepeval.models import GPTModel
gpt = GPTModel(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
metrics = [
    ContextualRecallMetric(threshold=0.5, model=gpt),
    ContextualPrecisionMetric(threshold=0.5, model=gpt),
    FaithfulnessMetric(threshold=0.5, model=gpt),
    AnswerRelevancyMetric(threshold=0.5, model=gpt)
]

# Step 4: evaluate
print("Running evaluation...")
evaluate(test_cases, metrics)