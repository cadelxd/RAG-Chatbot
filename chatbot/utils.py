# core/utils.py
import chromadb
import google.generativeai as genai
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from django.conf import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize a persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

def process_document(file_path):
    try:
        # Clear previous collection to avoid conflicts
        try:
            client.delete_collection(name="document_chatbot")
        except:
            pass # Collection might not exist yet

        # Load and split the document
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(pages)

        # Create a new collection and add chunks
        collection = client.get_or_create_collection(name="document_chatbot")

        # Batching for performance with large files
        chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]
        chunk_texts = [chunk.page_content for chunk in chunks]
        chunk_metadatas = [{"source": file_path, "page": chunk.metadata.get("page", 0)} for chunk in chunks]

        collection.add(
            documents=chunk_texts,
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )
        return True
    except Exception as e:
        print(f"Error processing document: {e}")
        return False

def get_answer(query):
    try:
        # Access the collection
        collection = client.get_collection(name="document_chatbot")

        # Retrieve relevant chunks via a similarity search
        results = collection.query(
            query_texts=[query],
            n_results=3,
        )

        context_text = "\n\n".join(results['documents'][0])

        # Craft the prompt for the LLM
        prompt = f"Using only the following document context, answer the user's question. If the answer is not in the document, state that you cannot provide an answer from the provided context.\n\nDocument Context:\n{context_text}\n\nUser Question:\n{query}"

        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        return response.text
    except Exception as e:
        print(f"Error getting answer: {e}")
        return "An error occurred while fetching the answer. Please try again or re-upload the document."