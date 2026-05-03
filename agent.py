import os
os.system('pip install langchain-groq langchain-community faiss-cpu sentence-transformers pypdf')
from langchain_groq import ChatGroq
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# 1. THE KEY 
import streamlit as st
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# 2. LOAD DATA (Looks inside your 'shopping_data' folder)
loader = DirectoryLoader('./shopping_data/', glob="./*.txt", loader_cls=TextLoader)
docs = loader.load()

# 3. SPLIT TEXT (RAG Step)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

# 4. CREATE MEMORY
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = FAISS.from_documents(chunks, embeddings)

# 5. THE AI AGENT
llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)
shopping_whisperer = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_db.as_retriever())

# 6. THE FUNCTION FOR FRONTEND
def get_shopping_verdict(user_query):
    response = shopping_whisperer.invoke(user_query)
    return response["result"]