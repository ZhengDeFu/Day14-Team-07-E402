import asyncio
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except ImportError:
    client = None

class ResponseReranker:
    """
    Reranking module để cải thiện retrieval quality.
    Sử dụng semantic similarity để rerank retrieved documents.
    """
    
    def __init__(self):
        self.model = "gpt-4o-mini"
    
    async def rerank_documents(self, query: str, documents: List[Dict], top_k: int = 3) -> List[Dict]:
        """
        Rerank documents dựa trên semantic relevance với query.
        """
        if not documents or not client:
            return documents[:top_k]
        
        # Tạo prompt để LLM đánh giá relevance
        doc_text = "\n\n".join([
            f"[{i}] {doc.get('content', '')[:200]}"
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""Bạn là chuyên gia đánh giá mức độ liên quan của tài liệu.

Câu hỏi: {query}

Tài liệu:
{doc_text}

Hãy xếp hạng các tài liệu theo mức độ liên quan từ cao nhất đến thấp nhất.
Trả về JSON: {{"ranking": [<index>, <index>, ...]}}"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            import json, re
            content = response.choices[0].message.content
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                ranking_data = json.loads(json_match.group())
                ranking = ranking_data.get("ranking", list(range(len(documents))))
                
                reranked = [documents[i] for i in ranking if i < len(documents)]
                return reranked[:top_k]
        except Exception as e:
            pass
        
        return documents[:top_k]
    
    async def calculate_semantic_similarity(self, query: str, document: str) -> float:
        """
        Tính semantic similarity giữa query và document.
        """
        if not client:
            return 0.5
        
        prompt = f"""Đánh giá mức độ liên quan từ 0 đến 1:
Query: {query}
Document: {document[:200]}

Trả về JSON: {{"similarity": <số từ 0 đến 1>}}"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            import json, re
            content = response.choices[0].message.content
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                data = json.loads(json_match.group())
                return float(data.get("similarity", 0.5))
        except Exception:
            pass
        
        return 0.5

if __name__ == "__main__":
    async def test():
        reranker = ResponseReranker()
        docs = [
            {"id": "1", "content": "VF8 là xe SUV điện"},
            {"id": "2", "content": "VF9 là xe SUV lớn"},
            {"id": "3", "content": "VF8 có pin 82 kWh"}
        ]
        
        result = await reranker.rerank_documents("VF8 là gì?", docs)
        print(result)
    
    asyncio.run(test())
