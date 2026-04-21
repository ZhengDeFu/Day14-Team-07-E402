import asyncio
import json
import os
import time
from engine.runner import BenchmarkRunner
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge
from agent.main_agent import MainAgentV1, MainAgentV2
from dotenv import load_dotenv

load_dotenv()

# RAGAS-style evaluator (simplified)
class ExpertEvaluator:
    async def score(self, case, resp):
        return {
            "faithfulness": 0.85,
            "relevancy": 0.80,
            "context_precision": 0.75,
            "context_recall": 0.70
        }

async def run_benchmark_with_results(agent, agent_version: str):
    print(f"\n🚀 Khởi động Benchmark cho {agent_version}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng.")
        return None, None

    print(f"📊 Loaded {len(dataset)} test cases")

    evaluator = ExpertEvaluator()
    judge = LLMJudge()
    
    runner = BenchmarkRunner(agent, evaluator, judge)
    results = await runner.run_all(dataset)

    # Calculate summary metrics
    total = len(results)
    
    avg_judge_score = sum(r["judge"]["final_score"] for r in results) / total
    avg_agreement = sum(r["judge"]["agreement_rate"] for r in results) / total
    avg_hit_rate = sum(r["retrieval"]["hit_rate"] for r in results) / total
    avg_mrr = sum(r["retrieval"]["mrr"] for r in results) / total
    avg_faithfulness = sum(r["ragas"]["faithfulness"] for r in results) / total
    avg_relevancy = sum(r["ragas"]["relevancy"] for r in results) / total
    avg_latency = sum(r["latency"] for r in results) / total
    total_tokens = sum(r["tokens_used"] for r in results)
    
    cost_per_1k_tokens = 0.002
    estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens

    summary = {
        "metadata": {
            "version": agent_version,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "metrics": {
            "avg_score": round(avg_judge_score, 2),
            "avg_judge_score": round(avg_judge_score, 2),
            "agreement_rate": round(avg_agreement, 2),
            "hit_rate": round(avg_hit_rate, 2),
            "mrr": round(avg_mrr, 2),
            "faithfulness": round(avg_faithfulness, 2),
            "relevancy": round(avg_relevancy, 2),
            "avg_latency_sec": round(avg_latency, 3),
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(estimated_cost, 4)
        },
        "pass_rate": round(sum(1 for r in results if r["status"] == "pass") / total * 100, 1)
    }
    
    return results, summary

async def main():
    print("=" * 60)
    print("🏭 AI EVALUATION FACTORY - BENCHMARK RUNNER")
    print("=" * 60)
    
    # Run V1 (baseline)
    v1_agent = MainAgentV1()
    v1_results, v1_summary = await run_benchmark_with_results(v1_agent, "Agent_V1_Base")
    
    if not v1_summary:
        print("❌ Không thể chạy Benchmark.")
        return

    print(f"\n📈 V1 Results:")
    print(f"   Judge Score: {v1_summary['metrics']['avg_judge_score']}")
    print(f"   Hit Rate: {v1_summary['metrics']['hit_rate']}")
    print(f"   MRR: {v1_summary['metrics']['mrr']}")
    print(f"   Pass Rate: {v1_summary['pass_rate']}%")
    
    # Run V2 (optimized)
    v2_agent = MainAgentV2()
    v2_results, v2_summary = await run_benchmark_with_results(v2_agent, "Agent_V2_Optimized")
    
    print(f"\n📈 V2 Results:")
    print(f"   Judge Score: {v2_summary['metrics']['avg_judge_score']}")
    print(f"   Hit Rate: {v2_summary['metrics']['hit_rate']}")
    print(f"   MRR: {v2_summary['metrics']['mrr']}")
    print(f"   Pass Rate: {v2_summary['pass_rate']}%")

    # Regression Analysis
    print("\n" + "=" * 60)
    print("📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    print("=" * 60)
    
    delta = v2_summary['metrics']['avg_judge_score'] - v1_summary['metrics']['avg_judge_score']
    delta_hit = v2_summary['metrics']['hit_rate'] - v1_summary['metrics']['hit_rate']
    delta_mrr = v2_summary['metrics']['mrr'] - v1_summary['metrics']['mrr']
    delta_latency = v2_summary['metrics']['avg_latency_sec'] - v1_summary['metrics']['avg_latency_sec']
    delta_cost = v2_summary['metrics']['estimated_cost_usd'] - v1_summary['metrics']['estimated_cost_usd']
    
    print(f"V1 Judge Score: {v1_summary['metrics']['avg_judge_score']}")
    print(f"V2 Judge Score: {v2_summary['metrics']['avg_judge_score']}")
    print(f"Delta Score: {'+' if delta >= 0 else ''}{delta:.2f}")
    print(f"Delta Hit Rate: {'+' if delta_hit >= 0 else ''}{delta_hit:.2f}")
    print(f"Delta MRR: {'+' if delta_mrr >= 0 else ''}{delta_mrr:.2f}")
    print(f"Delta Latency: {'+' if delta_latency >= 0 else ''}{delta_latency:.3f}s")
    print(f"Delta Cost: {'+' if delta_cost >= 0 else ''}${delta_cost:.4f}")
    print(f"V2 Pass Rate: {v2_summary['pass_rate']}%")
    print(f"V2 Est. Cost: ${v2_summary['metrics']['estimated_cost_usd']:.4f}")

    # Auto-Gate Decision
    print("\n" + "-" * 40)
    if delta >= 0 and delta_hit >= 0:
        print("✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE)")
    else:
        print("❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE)")
    print("-" * 40)

    # Save reports
    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)
    
    # Save V1 results for comparison
    with open("reports/v1_results.json", "w", encoding="utf-8") as f:
        json.dump(v1_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Reports saved to reports/")

if __name__ == "__main__":
    asyncio.run(main())