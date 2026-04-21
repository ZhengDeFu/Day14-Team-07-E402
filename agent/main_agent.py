import asyncio
import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    client = OpenAI()
except ImportError:
    client = None

# Simple in-memory vector store
class SimpleVectorStore:
    def __init__(self):
        self.documents = []
        self.ids = []
    
    def add(self, doc_id: str, content: str, metadata: dict = None):
        self.ids.append(doc_id)
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {}
        })
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Simple keyword-based search (can be replaced with embeddings)."""
        query_lower = query.lower()
        scores = []
        
        for i, doc in enumerate(self.documents):
            # Simple scoring based on keyword matching
            score = 0
            query_words = query_lower.split()
            content_lower = doc["content"].lower()
            
            for word in query_words:
                if len(word) > 2:  # Skip short words
                    if word in content_lower:
                        score += 1
            
            scores.append((i, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        results = []
        for idx, score in scores[:top_k]:
            if score > 0:
                results.append({
                    "id": self.documents[idx]["id"],
                    "content": self.documents[idx]["content"],
                    "score": score,
                    "metadata": self.documents[idx]["metadata"]
                })
        
        return results

# Global vector store
vector_store = SimpleVectorStore()

def load_documents():
    """Load all articles into the vector store."""
    articles_dir = "articles"
    
    for filename in os.listdir(articles_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(articles_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Truncate very long content
                if len(content) > 5000:
                    content = content[:5000] + "..."
                vector_store.add(filename, content, {"source": filename})

# Load documents on module import
load_documents()

class MainAgent:
    """
    RAG-based Agent for VinFast VF8 Q&A.
    """
    def __init__(self):
        self.name = "VF8SupportAgent-v1"
        self.system_prompt = """Bạn là trợ lý hỗ trợ khách hàng VinFast. 
Hãy trả lời câu hỏi dựa trên thông tin từ sách hướng dẫn sử dụng VF8.
Trả lời ngắn gọn, chính xác và hữu ích."""

    async def query(self, question: str) -> Dict:
        """
        Main RAG pipeline:
        1. Retrieval: Find relevant context
        2. Generation: Generate answer using LLM
        """
        # Step 1: Retrieval
        retrieved_docs = vector_store.search(question, top_k=3)
        
        # Build context from retrieved documents
        context = "\n\n".join([
            f"[{doc['id']}]: {doc['content'][:500]}" 
            for doc in retrieved_docs
        ])
        
        # Step 2: Generation
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Dựa trên thông tin sau:\n\n{context}\n\nCâu hỏi: {question}\n\nTrả lời:"}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                answer = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage else 0
            except Exception as e:
                answer = f"Xin lỗi, có lỗi xảy ra: {str(e)}"
                tokens_used = 0
        else:
            # Fallback without API
            answer = f"Dựa trên tài liệu hướng dẫn, tôi xin trả lời câu hỏi '{question}': Đây là câu trả lời mẫu dựa trên thông tin về VF8."
            tokens_used = 50
        
        return {
            "answer": answer,
            "contexts": [doc["content"] for doc in retrieved_docs],
            "retrieved_ids": [doc["id"] for doc in retrieved_docs],
            "metadata": {
                "model": "gpt-4o-mini" if client else "mock",
                "tokens_used": tokens_used,
                "sources": [doc["id"] for doc in retrieved_docs]
            }
        }

if __name__ == "__main__":
    agent = MainAgent()
    
    async def test():
        resp = await agent.query("VF8 là dòng xe gì?")
        print("Question: VF8 là dòng xe gì?")
        print(f"Answer: {resp['answer']}")
        print(f"Retrieved IDs: {resp['retrieved_ids']}")
    
    asyncio.run(test())