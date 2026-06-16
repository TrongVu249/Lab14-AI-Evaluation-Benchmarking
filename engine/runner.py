import asyncio
import time
from typing import List, Dict

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge, max_concurrency: int = 5):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge
        # Giới hạn số lượng request chạy song song cùng lúc để tránh Rate Limit của API
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def run_single_test(self, test_case: Dict) -> Dict:
        async with self.semaphore:
            start_time = time.perf_counter()
            
            # 1. Gọi Agent để lấy câu trả lời
            response = await self.agent.query(test_case["question"])
            latency = time.perf_counter() - start_time
            
            # Lấy thông tin ID tài liệu tìm kiếm được
            retrieved_ids = response.get("metadata", {}).get("sources", [])
            expected_ids = test_case.get("expected_retrieval_ids", [])
            
            # 2. Tính toán Hit Rate và MRR
            hit_rate = self.evaluator.calculate_hit_rate(expected_ids, retrieved_ids)
            mrr = self.evaluator.calculate_mrr(expected_ids, retrieved_ids)
            
            # Tạo dictionary điểm số RAGAS (giả lập hoặc từ bộ eval)
            ragas_scores = {
                "faithfulness": 0.95 if hit_rate > 0 else 0.5,
                "relevancy": 0.9 if hit_rate > 0 else 0.4,
                "retrieval": {
                    "hit_rate": hit_rate,
                    "mrr": mrr
                }
            }
            
            # 3. Chạy Multi-Judge chấm điểm
            judge_result = await self.judge.evaluate_multi_judge(
                test_case["question"], 
                response["answer"], 
                test_case["expected_answer"]
            )
            
            # 4. Tính toán Token và Chi phí sử dụng (Cost USD)
            tokens_used = response.get("metadata", {}).get("tokens_used", 0)
            
            # Quy ước giá (gpt-4o-mini qua OpenRouter khoảng $0.15/1M input, $0.60/1M output, lấy trung bình $0.30/1M tokens)
            cost_usd = (tokens_used / 1_000_000.0) * 0.3
            
            return {
                "test_case": test_case["question"],
                "agent_response": response["answer"],
                "latency": latency,
                "ragas": ragas_scores,
                "judge": judge_result,
                "cost_usd": cost_usd,
                "tokens_used": tokens_used,
                "status": "fail" if judge_result["final_score"] < 3.0 else "pass"
            }

    async def run_all(self, dataset: List[Dict]) -> List[Dict]:
        """
        Chạy song song toàn bộ dataset sử dụng asyncio.gather với Semaphore khống chế.
        """
        tasks = [self.run_single_test(case) for case in dataset]
        return await asyncio.gather(*tasks)

