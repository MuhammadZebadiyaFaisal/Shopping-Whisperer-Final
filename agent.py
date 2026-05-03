import os
import streamlit as st
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq

# 1. API KEY & CLIENT SETUP
# Initialize the official Groq client
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# 2. LOAD DATA
# @st.cache_data prevents Streamlit from re-reading the files on every single interaction
@st.cache_data
def load_docs(folder="./shopping_data/"):
    texts = []
    if not os.path.exists(folder):
        return texts
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                texts.append(f.read())
    return texts

# 3. SPLIT TEXT
# A clean, dependency-free alternative to Langchain's RecursiveCharacterTextSplitter
def split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# 4. CREATE MEMORY & EMBEDDINGS
# @st.cache_resource is CRITICAL here. It stops the app from hanging by only building the AI's memory once.
@st.cache_resource
def setup_vector_db():
    docs = load_docs()
    
    # Initialize the local HuggingFace embedding model
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    
    all_chunks = []
    for doc in docs:
        all_chunks.extend(split_text(doc))
        
    if not all_chunks:
        return embedder, None, all_chunks
        
    # Create the FAISS Index natively
    embeddings = embedder.encode(all_chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    return embedder, index, all_chunks

embedder, index, all_chunks = setup_vector_db()

# 5. THE AI AGENT AND FRONTEND FUNCTION
def get_shopping_verdict(user_query):
    if not index:
        return "System Error: Shopping data could not be loaded. Check your data folder."
        
    # Find the top 3 most relevant chunks of text using FAISS
    query_embedding = embedder.encode([user_query])
    distances, indices = index.search(np.array(query_embedding), k=3)
    
    # Combine the found text chunks into a single context string
    context = "\n\n".join([all_chunks[i] for i in indices[0]])
    
    # Build the prompt explicitly
    prompt = f"""
You are an expert shopping assistant. Use the context below to answer the user's query.

Context:
{context}

User Query:
{user_query}
"""

    try:
        # Direct Groq API call
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and expert shopping assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # Replaced your decommissioned 'llama3-70b-8192' with the currently supported 70b model
            model="llama-3.3-70b-versatile", 
            temperature=0
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error connecting to Groq: {str(e)}"
