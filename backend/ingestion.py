import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """step one: Extract text from the PDF document."""
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc):
        pages.append(
            {"page_number": page_num + 1, "text": page.get_text()}
        )
    return pages

"""step two: Split the extracted text into smaller chunks."""

def split_into_chunks(pages : list[dict]):
    splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],       
    chunk_size=1000,
    chunk_overlap=100,
    )
    chunks = []
    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for i, chunk in enumerate(page_chunks):
            chunks.append(
                {"page_number": page["page_number"], "chunk_number": i + 1, "text": chunk}
            )
    return chunks


"""test the functions"""
if __name__ == "__main__":
    pdf_path = r"C:\Users\mechi\Desktop\legalmind\sample_docs\test.pdf"
    pages = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(pages)
    print(f"Total chunks extracted: {len(chunks)}")
    for chunk in chunks:
        print(f"Page {chunk['page_number']} | Chunk {chunk['chunk_number']} | {chunk['text'][:100]}")