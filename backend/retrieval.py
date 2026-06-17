import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

"Initialize ChromaDB client and collection"
client = chromadb.Client()
collection = client.get_or_create_collection(name="legalmind")

def store(chuncks :list[dict]) -> None:
    """Store the chunks in ChromaDB."""
    collection.add(
        embeddings=[chunk["embedding"] for chunk in chuncks],
        documents=[chunk["text"] for chunk in chuncks],
        metadatas=[{"page_number": chunk["page_number"], "chunk_number": chunk["chunk_number"]} for chunk in chuncks],
        ids=[f"{chunk['page_number']}_{chunk['chunk_number']}" for chunk in chuncks]
    )

def retrieve(quest: str, top_k: int = 4) -> list[dict]:
    """Retrieve relevant chunks based on the query."""
    query_embedding = model.encode(quest).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results

if __name__ == "__main__":
    from ingestion import extract_text_from_pdf, split_into_chunks
    from embeddings import embed_chunks

    # Step 1: ingest and embed
    pages = extract_text_from_pdf(r"C:\Users\mechi\Desktop\legalmind\sample_docs\test.pdf")
    chunks = split_into_chunks(pages)
    embedded_chunks = embed_chunks(chunks)

    # Step 2: store in ChromaDB
    store(embedded_chunks)
    print("Chunks stored successfully!")

    # Step 3: search
    results = retrieve("what are the confidentiality obligations?")
    print("\nTop results:")
    for i, doc in enumerate(results["documents"][0]):
        print(f"\nResult {i+1}: {doc[:200]}")
        