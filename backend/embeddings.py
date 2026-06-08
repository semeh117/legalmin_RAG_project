from sentence_transformers import SentenceTransformer

# Load the pre-trained model
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks : list[dict])-> list[dict]:
    """Generate embeddings for each text chunk."""
    for chunk in chunks:
        chunk["embedding"] = model.encode(chunk["text"]).tolist()  # Convert to list for JSON serialization
    return chunks

"""test the function"""
if __name__ == "__main__":
    from ingestion import extract_text_from_pdf, split_into_chunks
    pages = extract_text_from_pdf(r"C:\Users\mechi\Desktop\legalmind\sample_docs\test.pdf")
    chunks = split_into_chunks(pages)
    embedded_chunks = embed_chunks(chunks)
    print(f"Total embedded chunks: {len(embedded_chunks)}")
    print(f"Sample embedding for first chunk: {embedded_chunks[0]['embedding']}")  # Print first 5 values of the embedding for the first chunk