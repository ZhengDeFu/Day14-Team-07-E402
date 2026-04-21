import asyncio
import time
from typing import List, Dict, Any
from engine.retrieval_eval import RetrievalEvaluator

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator  # RAGAS-style evaluator
        self.judge = judge  # Multi-judge
        self.retrieval_eval = RetrievalEvaluator()

    async def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.perf_counter()

        try:
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
                response.get("answer", ""),
                test_case.get("expected_answer", "")
            )

            # Determine pass/fail
            status = "pass" if judge_result.get("final_score", 0) >= 3.0 else "fail"

            return {
                "test_case": test_case["question"],
                "expected_answer": test_case.get("expected_answer", ""),
                "agent_response": response.get("answer", ""),
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
        except Exception as exc:
            latency = time.perf_counter() - start_time
            return {
                "test_case": test_case.get("question", ""),
                "expected_answer": test_case.get("expected_answer", ""),
                "agent_response": "",
                "retrieved_ids": [],
                "latency": round(latency, 3),
                "tokens_used": 0,
                "ragas": {"faithfulness": 0, "relevancy": 0},
                "retrieval": {"hit_rate": 0, "mrr": 0},
                "judge": {"final_score": 0, "agreement_rate": 0},
                "status": "fail",
                "error": str(exc)
            }

    async def run_all(self, dataset: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
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

    async def run_regression_comparison(
        self,
        v1_results: List[Dict[str, Any]],
        v2_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare V1 and V2 results for regression testing.
        """
        def calc_avg_score(results: List[Dict[str, Any]]) -> float:
            scores = [r.get("judge", {}).get("final_score", 0) for r in results]
            return sum(scores) / len(scores) if scores else 0

        def calc_avg_retrieval(results: List[Dict[str, Any]]) -> Dict[str, float]:
            hit_rates = [r.get("retrieval", {}).get("hit_rate", 0) for r in results]
            mrrs = [r.get("retrieval", {}).get("mrr", 0) for r in results]
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
            "v1_retrieval": {
                "hit_rate": round(v1_retrieval["hit_rate"], 3),
                "mrr": round(v1_retrieval["mrr"], 3)
            },
            "v2_retrieval": {
                "hit_rate": round(v2_retrieval["hit_rate"], 3),
                "mrr": round(v2_retrieval["mrr"], 3)
            },
            "delta_hit_rate": round(delta_hit_rate, 3),
            "decision": decision
        }