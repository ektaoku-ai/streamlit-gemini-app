# Project members- Sam Smith, Morgan Smith,Rachel Bulkley,Ekta Arora
import streamlit as st
import google.generativeai as genai
from textExtractor import extract_document_text

#Step 1- Configure API
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if API_KEY:
    genai.configure(api_key=API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
else:
    gemini_model = None

#Step 2- Parameters to chunk the uploaded doc
CHUNK_SIZE = 80000
CHUNK_OVERLAP = 500
MAX_CHUNKS = 8

# Step 3- Read the uploaded file
def read_file_text(upload_file) -> str:
    if upload_file is None:
        return ""
    raw = upload_file.read()
    return raw.decode("utf-8", errors="ignore")

# Step 4- Split the large chunk of uploaded text into overlapping text
def split_into_chunks(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    n = len(text)
    start = 0

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        # move start forward, keeping a bit of overlap
        start = end - overlap

    # Step 5- : Putting a hard cap on number of chunks to avoid quota blowups
    if len(chunks) > MAX_CHUNKS:
        chunks = chunks[:MAX_CHUNKS]

    return chunks


st.title("Generate AI response (Closed-source Gemini, large documents)")

question = st.text_input("Enter your Question")
upload_file = st.file_uploader(
    "Upload attachment",
    type=['txt', 'pdf', 'doc', 'docx', 'html']
)

if st.button("Generate Response"):
    if not question:
        st.warning("Please enter your question.")
    else:
        if gemini_model is None:
            st.error("Gemini API key is not configured. Add GEMINI_API_KEY to Streamlit secrets.")
        else:
            # Step 6- Read full document text
            document_text = ""
            if upload_file is not None:
                document_text = extract_document_text(upload_file)

            if not document_text:
                prompt = f"""
You are a helpful assistant.

Question: {question}

Answer:
"""
                with st.spinner("Calling Gemini..."):
                    resp = gemini_model.generate_content(prompt)
                st.subheader("AI response")
                st.write(resp.text)
            else:
                # Step 7-  Split document into few, larger chunks
                chunks = split_into_chunks(document_text)

                partial_answers = []

                # Step 8- Command Gemini about each chunk
                with st.spinner(f"Reading document in {len(chunks)} chunk(s)..."):
                    for i, chunk in enumerate(chunks, start=1):
                        chunk_prompt = f"""
You are a helpful assistant. You will see one chunk of a larger document.

Chunk {i} of {len(chunks)}:
{chunk}

Question: {question}

Based ONLY on this chunk, either:
- provide any information that helps answer the question, or
- say "No relevant information in this chunk."

Answer for this chunk:
"""
                        resp = gemini_model.generate_content(chunk_prompt)
                        partial_answers.append(resp.text)

                # Step 9- Build chunk summary, please note that Python 3.9 safe
                chunk_summary_lines = []
                for idx, ans in enumerate(partial_answers, start=1):
                    chunk_summary_lines.append(f"- Chunk {idx}: {ans}")
                chunk_summary = "\n".join(chunk_summary_lines)

                # Step 10- Combine partial answers into a final answer
                combine_prompt = f"""
You are a helpful assistant. A long document was split into chunks and the
question was answered separately on each chunk.

Original question:
{question}

Here are the partial answers from each chunk:
{chunk_summary}

Please read all partial answers and produce ONE final, coherent answer for the user.
If some information is missing or uncertain, mention that clearly.

Final answer:
"""
                with st.spinner("Combining chunk answers..."):
                    final_resp = gemini_model.generate_content(combine_prompt)

                st.subheader("AI response")
                st.write(final_resp.text)
