from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Calculate Hit Rate: whether at least 1 expected_id is in top_k of retrieved_ids.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank.
        Find the first position of any expected_id in retrieved_ids.
        MRR = 1 / position (1-indexed). If not found, return 0.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    def calculate_precision_at_k(self, expected_ids: List[str], retrieved_ids: List[str], k: int = 3) -> float:
        """
        Calculate Precision@K: proportion of retrieved docs that are relevant.
        """
        if not retrieved_ids:
            return 0.0
        
        top_k = retrieved_ids[:k]
        relevant = sum(1 for doc_id in top_k if doc_id in expected_ids)
        return relevant / k

    def calculate_ndcg(self, expected_ids: List[str], retrieved_ids: List[str], k: int = 3) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG).
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        
        # DCG calculation
        dcg = 0.0
        for i, doc_id in enumerate(retrieved_ids[:k]):
            if doc_id in expected_ids:
                # Relevance is 1 if found
                dcg += 1.0 / (i + 1)
        
        # IDCG (ideal DCG)
        idcg = sum(1.0 / (i + 1) for i in range(min(k, len(expected_ids))))
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg

    async def evaluate_single(self, test_case: Dict, agent_response: Dict) -> Dict:
        """
        Evaluate retrieval for a single test case.
        """
        expected_ids = test_case.get("expected_retrieval_ids", [])
        retrieved_ids = agent_response.get("retrieved_ids", [])
        
        return {
            "hit_rate": self.calculate_hit_rate(expected_ids, retrieved_ids),
            "mrr": self.calculate_mrr(expected_ids, retrieved_ids),
            "precision_at_3": self.calculate_precision_at_k(expected_ids, retrieved_ids, k=3),
            "ndcg_at_3": self.calculate_ndcg(expected_ids, retrieved_ids, k=3)
        }

    async def evaluate_batch(self, dataset: List[Dict], results: List[Dict]) -> Dict:
        """
        Evaluate retrieval for entire dataset.
        """
        hit_rates = []
        mrrs = []
        
        for i, result in enumerate(results):
            if i < len(dataset):
                test_case = dataset[i]
                eval_result = await self.evaluate_single(test_case, result)
                hit_rates.append(eval_result["hit_rate"])
                mrrs.append(eval_result["mrr"])
        
        return {
            "avg_hit_rate": sum(hit_rates) / len(hit_rates) if hit_rates else 0.0,
            "avg_mrr": sum(mrrs) / len(mrrs) if mrrs else 0.0,
            "total_evaluated": len(hit_rates)
        }

if __name__ == "__main__":
    evaluator = RetrievalEvaluator()
    
    # Test
    expected = ["file1.md", "file2.md"]
    retrieved = ["file3.md", "file1.md", "file2.md"]
    
    print(f"Hit Rate: {evaluator.calculate_hit_rate(expected, retrieved)}")
    print(f"MRR: {evaluator.calculate_mrr(expected, retrieved)}")