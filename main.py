import asyncio
import json
import os
import time
import sys

# Cấu hình UTF-8 cho terminal trên Windows để tránh lỗi UnicodeEncodeError khi print emoji
if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from engine.runner import BenchmarkRunner
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge
from agent.main_agent import MainAgent

async def run_benchmark_with_results(agent_instance, agent_version: str):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    # Khởi tạo các bộ đánh giá thực tế thay vì mock
    evaluator = RetrievalEvaluator()
    judge = LLMJudge()
    
    runner = BenchmarkRunner(agent_instance, evaluator, judge, max_concurrency=10)
    results = await runner.run_all(dataset)

    total = len(results)
    avg_score = sum(r["judge"]["final_score"] for r in results) / total
    hit_rate = sum(r["ragas"]["retrieval"]["hit_rate"] for r in results) / total
    agreement_rate = sum(r["judge"]["agreement_rate"] for r in results) / total
    total_cost = sum(r.get("cost_usd", 0.0) for r in results)
    avg_latency = sum(r["latency"] for r in results) / total

    summary = {
        "metadata": {
            "version": agent_version, 
            "total": total, 
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "avg_latency_sec": avg_latency,
            "total_cost_usd": total_cost
        },
        "metrics": {
            "avg_score": avg_score,
            "hit_rate": hit_rate,
            "agreement_rate": agreement_rate
        }
    }
    return results, summary

async def run_benchmark(agent_instance, version):
    _, summary = await run_benchmark_with_results(agent_instance, version)
    return summary

async def main():
    # Khởi tạo các Agent phiên bản V1 và V2
    agent_v1 = MainAgent(version="v1")
    agent_v2 = MainAgent(version="v2")

    # 1. Chạy đánh giá phiên bản V1 Base
    v1_results, v1_summary = await run_benchmark_with_results(agent_v1, "Agent_V1_Base")
    
    # 2. Chạy đánh giá phiên bản V2 Optimized
    v2_results, v2_summary = await run_benchmark_with_results(agent_v2, "Agent_V2_Optimized")
    
    if not v1_summary or not v2_summary:
        print("❌ Không thể chạy Benchmark. Kiểm tra lại data/golden_set.jsonl.")
        return

    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    v1_score = v1_summary["metrics"]["avg_score"]
    v2_score = v2_summary["metrics"]["avg_score"]
    delta = v2_score - v1_score
    
    print(f"V1 Score (Base): {v1_score:.2f}")
    print(f"V2 Score (Optimized): {v2_score:.2f}")
    print(f"Delta: {'+' if delta >= 0 else ''}{delta:.2f}")
    
    v2_hit_rate = v2_summary["metrics"]["hit_rate"]
    print(f"V2 Hit Rate: {v2_hit_rate*100:.1f}%")
    print(f"V2 Agreement Rate: {v2_summary['metrics']['agreement_rate']*100:.1f}%")
    print(f"V2 Total Cost: ${v2_summary['metadata']['total_cost_usd']:.5f}")
    print(f"V2 Avg Latency: {v2_summary['metadata']['avg_latency_sec']:.3f} sec")

    # Lưu kết quả V2 Optimized (để check_lab.py kiểm tra)
    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    # Chốt kiểm soát Release Gate
    # Phát hành V2 nếu:
    # 1. Điểm trung bình V2 tốt hơn V1 (delta > 0)
    # 2. Hit Rate tối thiểu của V2 lớn hơn 0.7
    min_hit_rate = 0.7
    
    if delta > 0 and v2_hit_rate >= min_hit_rate:
        print("\n🟢 QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE RELEASE)")
    else:
        print("\n🔴 QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE)")
        if delta <= 0:
            print("  Lý do: Điểm trung bình của V2 không cải tiến so với V1.")
        if v2_hit_rate < min_hit_rate:
            print(f"  Lý do: Tỷ lệ Hit Rate ({v2_hit_rate*100:.1f}%) thấp hơn ngưỡng tối thiểu ({min_hit_rate*100:.1f}%).")

if __name__ == "__main__":
    asyncio.run(main())

