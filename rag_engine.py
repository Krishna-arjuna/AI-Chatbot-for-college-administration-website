import os
import time
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Pre-defined answers for common questions (instant responses)
CACHE = {
    "whats your college name": "Rajarajeshwari college of Engineering",
    "what is your college name": "Rajarajeshwari college of Engineering", 
    "college name": "Rajarajeshwari college of Engineering",
    "where is the college": "Our college is located at 123 Education Street, City, State",
    "courses offered": "We offer Engineering, Business, Computer Science, and Arts programs",
    "contact information": "Phone: 123-456-7890, Email: info@rrcecollege.edu",
    "hello": "Hello! How can I help you with college information today?",
    "hi": "Hi there! What would you like to know about our college?",
    "hii": "Hi there! What would you like to know about our college?",
    "hey": "Hello! How can I assist you with college information?",
    "thank you": "You're welcome! Let me know if you need any other information.",
    "thanks": "You're welcome! Feel free to ask if you have more questions.",
    "bye": "Goodbye! Have a great day!",
    "goodbye": "Goodbye! Visit again if you need more information."
}

# Paths
VECTOR_STORE_DIR = os.path.join(os.path.dirname(__file__), "vector_store")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "college_info.txt")

def get_answer(query: str):
    try:
        print(f"🔍 Processing query: '{query}'")
        start_time = time.time()
        
        # Check cache first - FIXED LOGIC
        query_lower = query.lower().strip()
        
        # For greetings, only match exact short phrases
        greetings = ["hi", "hii", "hello", "hey", "hola"]
        if query_lower in greetings:
            response_time = time.time() - start_time
            print(f"✅ Greeting cache hit! Response in {response_time:.3f} seconds")
            return CACHE[query_lower]
        
        # For other cache entries, check if the query starts with or contains the exact phrase
        for key, answer in CACHE.items():
            # Skip greetings since we handled them above
            if key in greetings:
                continue
                
            # Check if query starts with the key or contains it as a whole word
            if (query_lower.startswith(key) or 
                f" {key} " in f" {query_lower} " or
                query_lower.endswith(f" {key}")):
                response_time = time.time() - start_time
                print(f"✅ Cache hit for '{key}'! Response in {response_time:.3f} seconds")
                return answer
        
        # If not in cache, use RAG approach
        print("🔄 Not in cache, using RAG...")
        
        # Check if vector store exists
        if not os.path.exists(VECTOR_STORE_DIR):
            return "I'm still setting up. Please try again in a moment."
        
        # Simple similarity search
        embeddings = OllamaEmbeddings(model="llama3")
        db = Chroma(
            persist_directory=VECTOR_STORE_DIR,
            embedding_function=embeddings
        )

        # Find relevant documents
        docs = db.similarity_search(query, k=1)
        
        if docs:
            context = docs[0].page_content[:500]
            prompt = f"Based on this context: {context}\n\nAnswer this question briefly: {query}"
        else:
            prompt = f"Answer this question about college information: {query}"

        # Use direct Ollama call for speed
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
            
            response = client.chat.completions.create(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            response_time = time.time() - start_time
            print(f"✅ LLM Response in {response_time:.2f} seconds")
            return answer
            
        except ImportError:
            from langchain_ollama import OllamaLLM
            llm = OllamaLLM(model="llama3.2:3b")
            answer = llm.invoke(prompt)
            response_time = time.time() - start_time
            print(f"✅ Fallback Response in {response_time:.2f} seconds")
            return answer
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return "I'll help you with that. For detailed information, please visit our college website or contact the administration office."

def create_knowledge_base():
    try:
        if not os.path.exists(DATA_FILE):
            print(f"❌ File not found: {DATA_FILE}")
            return

        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(DATA_FILE, encoding="utf-8")
        docs = loader.load()

        if not docs:
            print(f"❌ No documents found in {DATA_FILE}")
            return

        print(f"📘 Loaded {len(docs)} document(s) from {DATA_FILE}")

        embeddings = OllamaEmbeddings(model="llama3")
        db = Chroma.from_documents(
            docs,
            embeddings,
            persist_directory=VECTOR_STORE_DIR
        )

        print("✅ Knowledge base created and persisted successfully!")
        
    except Exception as e:
        print(f"❌ Error creating knowledge base: {e}")