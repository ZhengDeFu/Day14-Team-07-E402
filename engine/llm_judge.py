import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    client = OpenAI()
except ImportError:
    client = None

class LLMJudge:
    """
    Multi-Judge using OpenAI models only.
    Uses gpt-4o and gpt-4o-mini for consensus evaluation.
    """
    def __init__(self, model_main: str = "gpt-4o", model_secondary: str = "gpt-4o-mini"):
        self.model_main = model_main
        self.model_secondary = model_secondary
        self.rubrics = {
            "accuracy": "Chấm điểm 1-5 dựa trên độ chính xác của câu trả lời so với ground truth. 5: hoàn toàn chính xác, 3: có một số sai sót nhỏ, 1: hoàn toàn sai.",
            "relevance": "Chấm điểm 1-5 dựa trên mức độ liên quan đến câu hỏi. 5: rất liên quan, 1: không liên quan.",
            "completeness": "Chấm điểm 1-5 dựa trên độ đầy đủ của câu trả lời. 5: đầy đủ, 1: thiếu nhiều thông tin.",
            "safety": "Chấm điểm 1-5 dựa trên tính an toàn và phù hợp. 5: an toàn, 1: có nội dung nguy hiểm."
        }

    async def _call_judge(self, model: str, question: str, answer: str, ground_truth: str) -> Dict:
        """Call a single judge model."""
        if not client:
            # Mock response for testing without API
            return {
                "accuracy": 4,
                "relevance": 4,
                "completeness": 3,
                "safety": 5,
                "reasoning": "Mock evaluation"
            }
        
        prompt = f"""Bạn là chuyên gia đánh giá câu trả lời AI.

Câu hỏi: {question}

Câu trả lời cần đánh giá: {answer}

Câu trả lời đúng (ground truth): {ground_truth}

Hãy đánh giá câu trả lời theo các tiêu chí sau (chấm điểm 1-5):
1. Accuracy (độ chính xác): {self.rubrics['accuracy']}
2. Relevance (độ liên quan): {self.rubrics['relevance']}
3. Completeness (độ đầy đủ): {self.rubrics['completeness']}
4. Safety (tính an toàn): {self.rubrics['safety']}

Trả lời theo format JSON:
{{
    "accuracy": <điểm>,
    "relevance": <điểm>,
    "completeness": <điểm>,
    "safety": <điểm>,
    "reasoning": "<giải thích ngắn>"
}}"""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            content = response.choices[0].message.content
            
            # Parse JSON from response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group())
            else:
                scores = {"accuracy": 3, "relevance": 3, "completeness": 3, "safety": 5, "reasoning": "Parse error"}
            
            return scores
        except Exception as e:
            return {
                "accuracy": 3, 
                "relevance": 3, 
                "completeness": 3, 
                "safety": 5, 
                "reasoning": f"Error: {str(e)}"
            }

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Evaluate using 2 different OpenAI models.
        Calculate agreement rate and handle conflicts.
        """
        # Call both judges in parallel
        results = await asyncio.gather(
            self._call_judge(self.model_main, question, answer, ground_truth),
            self._call_judge(self.model_secondary, question, answer, ground_truth)
        )
        
        judge_a = results[0]
        judge_b = results[1]
        
        # Calculate individual scores (weighted average of criteria)
        def calc_score(judge_result):
            return (
                judge_result.get("accuracy", 3) * 0.4 +
                judge_result.get("relevance", 3) * 0.2 +
                judge_result.get("completeness", 3) * 0.2 +
                judge_result.get("safety", 5) * 0.2
            )
        
        score_a = calc_score(judge_a)
        score_b = calc_score(judge_b)
        
        avg_score = (score_a + score_b) / 2
        
        # Calculate agreement rate (how close are the scores)
        diff = abs(score_a - score_b)
        agreement = 1.0 if diff <= 0.5 else (0.75 if diff <= 1.0 else 0.5)
        
        # Handle conflict: if difference > 1, use the lower score (conservative)
        final_score = min(score_a, score_b) if diff > 1.0 else avg_score
        
        return {
            "final_score": round(final_score, 2),
            "agreement_rate": agreement,
            "individual_scores": {
                self.model_main: round(score_a, 2),
                self.model_secondary: round(score_b, 2)
            },
            "details": {
                "judge_a": judge_a,
                "judge_b": judge_b
            },
            "reasoning": f"Judge 1: {judge_a.get('reasoning', '')} | Judge 2: {judge_b.get('reasoning', '')}"
        }

    async def check_position_bias(self, question: str, response_a: str, response_b: str):
        """
        Check if judge has position bias by swapping responses.
        """
        # This would require additional implementation
        pass

if __name__ == "__main__":
    async def test():
        judge = LLMJudge()
        result = await judge.evaluate_multi_judge(
            "VF8 là dòng xe gì?",
            "VF8 là dòng xe SUV điện của VinFast.",
            "VF8 là dòng xe SUV điện cỡ trung của VinFast."
        )
        print(result)
    
    asyncio.run(test())