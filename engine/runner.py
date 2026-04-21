import asyncio
import time
from typing import List, Dict
from engine.retrieval_eval import RetrievalEvaluator

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator  # RAGAS-style evaluator
        self.judge = judge  # Multi-judge
        self.retrieval_eval = RetrievalEvaluator()

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()
        
        # 1. Call Agent
        response = await self.agent.query(test_case["question"])
        latency = time.perf_counter() - start_time
        
        # 2. Run RAGAS-style evaluation (faithfulness, relevancy)
        ragas_scores = await self.evaluator.score(test_case, response)
        
        # 3. Run Retrieval Evaluation (Hit Rate, MRR)
        retrieval_scores = await self.retrieval_eval.evaluate_single(test_case, response)
        
        # 4. Run Multi-Judge Evaluation
        judge_result = await self.judge.evaluate_multi_judge(
            test_case["question"], 
            response["answer"], 
            test_case.get("expected_answer", "")
        )
        
        # Determine pass/fail
        status = "pass" if judge_result["final_score"] >= 3.0 else "fail"
        
        return {
            "test_case": test_case["question"],
            "expected_answer": test_case.get("expected_answer", ""),
            "agent_response": response["answer"],
            "retrieved_ids": response.get("retrieved_ids", []),
            "latency": round(latency, 3),
            "tokens_used": response.get("metadata", {}).get("tokens_used", 0),
            "ragas": {
                "faithfulness": ragas_scores.get("faithfulness", 0),
                "relevancy": ragas_scores.get("relevancy", 0)
            },
            "retrieval": retrieval_scores,
            "judge": judge_result,
            "status": status
        }

    async def run_all(self, dataset: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Run benchmark with async parallel execution.
        Uses batch_size to avoid rate limits.
        """
        results = []
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(dataset) + batch_size - 1)//batch_size}...")
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        return results

    async def run_regression_comparison(self, v1_results: List[Dict], v2_results: List[Dict]) -> Dict:
        """
        Compare V1 and V2 results for regression testing.
        """
        def calc_avg_score(results):
            return sum(r["judge"]["final_score"] for r in results) / len(results) if results else 0
        
        def calc_avg_retrieval(results):
            hit_rates = [r["retrieval"]["hit_rate"] for r in results]
            mrrs = [r["retrieval"]["mrr"] for r in results]
            return {
                "hit_rate": sum(hit_rates) / len(hit_rates) if hit_rates else 0,
                "mrr": sum(mrrs) / len(mrrs) if mrrs else 0
            }
        
        v1_score = calc_avg_score(v1_results)
        v2_score = calc_avg_score(v2_results)
        
        v1_retrieval = calc_avg_retrieval(v1_results)
        v2_retrieval = calc_avg_retrieval(v2_results)
        
        delta_score = v2_score - v1_score
        delta_hit_rate = v2_retrieval["hit_rate"] - v1_retrieval["hit_rate"]
        
        # Auto-gate decision
        decision = "APPROVE" if delta_score >= 0 and delta_hit_rate >= 0 else "BLOCK"
        
        return {
            "v1_score": round(v1_score, 2),
            "v2_score": round(v2_score, 2),
            "delta_score": round(delta_score, 2),
            "v1_retrieval": v1_retrieval,
            "v2_retrieval": v2_retrieval,
            "delta_hit_rate": round(delta_hit_rate, 2),
            "decision": decision
        }