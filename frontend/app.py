import streamlit as st
import requests

API_URL = "http://backend:8000"

st.title("LegalMind: Your Legal Document Assistant")
st.subheader("AI Legal Consultant for PDF Documents")

# Upload PDF
st.header("Upload a PDF Document")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing your document..."):
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        )
    
    if response.status_code == 200:
        st.success(f"✅ {response.json()['message']}")
    else:
        st.error("❌ Failed to process document")

# Section 2: Ask Question
st.header("❓ Ask a Question")
question = st.text_input("Type your legal question here...")

if st.button("Ask LegalMind"):
    if question:
        with st.spinner("Analyzing document..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question}
            )
        
        if response.status_code == 200:
            st.header("📋 Answer")
            st.write(response.json()["answer"])
        else:
            st.error("❌ Failed to get answer")
    else:
        st.warning("⚠️ Please type a question first!")
