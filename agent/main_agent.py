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

# Simple in-memory vector store for evaluation
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
            """Simple keyword-based search."""
            query_lower = query.lower()
            scores = []
            
            for i, doc in enumerate(self.documents):
                score = 0
                query_words = query_lower.split()
                content_lower = doc["content"].lower()
                
                for word in query_words:
                    if len(word) > 2:
                        if word in content_lower:
                            score += 1
                
                scores.append((i, score))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            
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
    
vector_store = SimpleVectorStore()

# Load documents into vector store
def load_documents():
        """Load all articles into the vector store."""
        articles_dir = "articles"
        
        if not os.path.exists(articles_dir):
            return
        
        for filename in os.listdir(articles_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(articles_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if len(content) > 5000:
                        content = content[:5000] + "..."
                    vector_store.add(filename, content, {"source": filename})

load_documents()
print(f"✅ Loaded {len(vector_store.documents)} documents into SimpleVectorStore")

class MainAgentV1:
    """
    Agent Version 1 - Baseline (weaker version)
    - Simple retrieval without reranking
    - Basic prompt
    """
    def __init__(self):
        self.name = "VF8SupportAgent-v1"
        self.system_prompt = """Bạn là trợ lý VinFast. Trả lời câu hỏi."""

    async def query(self, question: str) -> Dict:
        # Step 1: Retrieval (basic keyword search)
        retrieved_docs = vector_store.search(question, top_k=2)  # V1: chỉ lấy 2 docs
        
        context = "\n\n".join([
            f"[{doc['id']}]: {doc['content'][:300]}" 
            for doc in retrieved_docs
        ])
        
        # Step 2: Generation (basic prompt)
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # V1: dùng model rẻ hơn
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Context:\n{context}\n\nCâu hỏi: {question}\n\nTrả lời:"}
                    ],
                    max_tokens=300,
                    temperature=0.5  # V1: temperature cao hơn
                )
                answer = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage else 0
            except Exception as e:
                answer = f"Xin lỗi, có lỗi: {str(e)}"
                tokens_used = 0
        else:
            answer = f"Trả lời từ V1 cho: {question}"
            tokens_used = 50
        
        return {
            "answer": answer,
            "contexts": [doc["content"] for doc in retrieved_docs],
            "retrieved_ids": [doc["id"] for doc in retrieved_docs],
            "metadata": {
                "model": "gpt-4o-mini" if client else "mock",
                "tokens_used": tokens_used,
                "version": "v1"
            }
        }

class MainAgentV2:
    """
    Agent Version 2 - Optimized (improved version)
    - Better retrieval with more context
    - Improved prompt with detailed instructions
    - Lower temperature for consistency
    """
    def __init__(self):
        self.name = "VF8SupportAgent-v2"
        self.system_prompt = """Bạn là trợ lý hỗ trợ khách hàng VinFast chuyên nghiệp.
Hãy trả lời câu hỏi dựa trên thông tin từ sách hướng dẫn sử dụng VF8.

Yêu cầu:
1. Trả lời đầy đủ và chi tiết nhất có thể
2. Nếu có thông tin trong context, hãy sử dụng nó
3. Trả lời ngắn gọn nhưng đủ thông tin
4. Sử dụng bullet points khi liệt kê nhiều mục"""

    async def query(self, question: str) -> Dict:
        # Step 1: Retrieval (improved - more docs)
        retrieved_docs = vector_store.search(question, top_k=3)  # V2: lấy 3 docs
        
        context = "\n\n".join([
            f"[{doc['id']}]: {doc['content'][:500]}"  # V2: lấy nhiều context hơn
            for doc in retrieved_docs
        ])
        
        # Step 2: Generation (improved prompt)
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Dựa trên thông tin sau:\n\n{context}\n\nCâu hỏi: {question}\n\nTrả lời:"}
                    ],
                    max_tokens=500,
                    temperature=0.3  # V2: temperature thấp hơn
                )
                answer = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage else 0
            except Exception as e:
                answer = f"Xin lỗi, có lỗi xảy ra: {str(e)}"
                tokens_used = 0
        else:
            answer = f"Dựa trên tài liệu hướng dẫn, tôi xin trả lời câu hỏi '{question}'"
            tokens_used = 50
        
        return {
            "answer": answer,
            "contexts": [doc["content"] for doc in retrieved_docs],
            "retrieved_ids": [doc["id"] for doc in retrieved_docs],
            "metadata": {
                "model": "gpt-4o-mini" if client else "mock",
                "tokens_used": tokens_used,
                "version": "v2"
            }
        }

# Alias for backward compatibility
class MainAgent(MainAgentV2):
    pass

if __name__ == "__main__":
    async def test():
        print("Testing V1...")
        v1 = MainAgentV1()
        resp1 = await v1.query("VF8 là dòng xe gì?")
        print(f"V1: {resp1['answer'][:100]}...")
        
        print("\nTesting V2...")
        v2 = MainAgentV2()
        resp2 = await v2.query("VF8 là dòng xe gì?")
        print(f"V2: {resp2['answer'][:100]}...")
    
    asyncio.run(test())