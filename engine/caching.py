import hashlib
import json
from typing import Dict, Optional
from datetime import datetime, timedelta

class ResponseCache:
    """
    Caching mechanism để giảm cost và latency.
    Lưu trữ responses và reuse cho similar queries.
    """
    
    def __init__(self, ttl_minutes: int = 60):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_saved_cost": 0.0
        }
    
    def _hash_query(self, query: str) -> str:
        """Hash query để dùng làm cache key."""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict]:
        """Lấy cached response nếu có."""
        key = self._hash_query(query)
        
        if key in self.cache:
            cached_item = self.cache[key]
            if datetime.now() < cached_item["expires_at"]:
                self.stats["hits"] += 1
                return cached_item["response"]
            else:
                del self.cache[key]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, query: str, response: Dict, cost: float = 0.0):
        """Lưu response vào cache."""
        key = self._hash_query(query)
        self.cache[key] = {
            "response": response,
            "expires_at": datetime.now() + self.ttl,
            "cost": cost,
            "timestamp": datetime.now().isoformat()
        }
        self.stats["total_saved_cost"] += cost
    
    def get_stats(self) -> Dict:
        """Lấy cache statistics."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "total_saved_cost": round(self.stats["total_saved_cost"], 4)
        }
    
    def clear(self):
        """Xóa toàn bộ cache."""
        self.cache.clear()
        self.stats = {"hits": 0, "misses": 0, "total_saved_cost": 0.0}

class QueryNormalizer:
    """
    Normalize queries để tăng cache hit rate.
    Ví dụ: "VF8 là gì?" và "VF8 là cái gì?" được coi là cùng query.
    """
    
    @staticmethod
    def normalize(query: str) -> str:
        """Normalize query."""
        # Lowercase
        query = query.lower()
        
        # Remove extra spaces
        query = " ".join(query.split())
        
        # Remove punctuation
        import string
        query = query.translate(str.maketrans('', '', string.punctuation))
        
        return query
    
    @staticmethod
    def are_similar(query1: str, query2: str, threshold: float = 0.8) -> bool:
        """Check if 2 queries are similar."""
        from difflib import SequenceMatcher
        
        q1 = QueryNormalizer.normalize(query1)
        q2 = QueryNormalizer.normalize(query2)
        
        ratio = SequenceMatcher(None, q1, q2).ratio()
        return ratio >= threshold

if __name__ == "__main__":
    cache = ResponseCache()
    
    # Test
    response = {"answer": "VF8 là xe SUV điện"}
    cache.set("VF8 là gì?", response, cost=0.001)
    
    result = cache.get("VF8 là gì?")
    print(f"Cached: {result}")
    print(f"Stats: {cache.get_stats()}")
