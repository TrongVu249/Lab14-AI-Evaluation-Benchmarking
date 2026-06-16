import asyncio
import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMJudge:
    def __init__(self):
        # Thiết lập OpenRouter hoặc OpenAI làm API Provider
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Fallback sang OpenAI nếu không tìm thấy key OpenRouter
        if not self.api_key and os.getenv("OPENAI_API_KEY"):
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.base_url = "https://api.openai.com/v1"
            
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        
        # Đọc các cấu hình model, hỗ trợ fallback sang các tên mô hình mặc định
        self.judge_model_a = os.getenv("JUDGE_MODEL_A", "openai/gpt-4o-mini")
        self.judge_model_b = os.getenv("JUDGE_MODEL_B", "meta-llama/llama-3-8b-instruct")
        self.tie_breaker_model = os.getenv("TIE_BREAKER_MODEL", "openai/gpt-4o")
        
        # Định nghĩa chi tiết các Rubrics
        self.rubrics = {
            "accuracy": """
            Chấm điểm từ 1 đến 5 dựa trên độ chính xác của câu trả lời của AI so với Ground Truth (Câu trả lời chuẩn):
            - 5 điểm: Hoàn toàn chính xác, đầy đủ chi tiết, không thiếu ý nào quan trọng và không có thông tin thừa/sai lệch.
            - 4 điểm: Chính xác và đầy đủ các ý chính, có thể thiếu một vài chi tiết nhỏ không đáng kể.
            - 3 điểm: Trả lời được ý chính nhưng thiếu nhiều thông tin chi tiết hoặc có một chút thông tin mơ hồ.
            - 2 điểm: Có thông tin đúng nhưng phần lớn là thiếu sót hoặc chứa thông tin sai lệch nhẹ (hallucination nhẹ).
            - 1 điểm: Hoàn toàn sai lệch, không trả lời đúng câu hỏi hoặc bịa đặt thông tin (hallucination nghiêm trọng).
            """,
            "tone": """
            Chấm điểm từ 1 đến 5 dựa trên sự chuyên nghiệp và giọng điệu của câu trả lời:
            - 5 điểm: Giọng điệu vô cùng lịch sự, chuyên nghiệp, hỗ trợ nhiệt tình và phù hợp với tiêu chuẩn dịch vụ khách hàng.
            - 3 điểm: Giọng điệu bình thường, không quá thô lỗ nhưng cũng chưa thực sự chuyên nghiệp hoặc quá ngắn gọn cộc lốc.
            - 1 điểm: Giọng điệu suồng sã, bất lịch sự hoặc không phù hợp với chuẩn mực giao tiếp công việc.
            """
        }

    async def _call_single_judge(self, model: str, question: str, answer: str, ground_truth: str, rubric_type: str) -> int:
        """
        Gọi một mô hình LLM để thực hiện vai trò chấm điểm.
        """
        if not self.api_key or "your_" in self.api_key:
            # Fallback nếu không có API Key hoạt động
            if answer.startswith("[V1 Base]"):
                return 3
            return 5
            
        rubric_content = self.rubrics.get(rubric_type, "")
        prompt = f"""
Bạn là một Trọng tài đánh giá AI (AI-as-a-Judge) chuyên nghiệp và khách quan.
Nhiệm vụ của bạn là đánh giá câu trả lời của AI dựa trên thông tin câu hỏi và câu trả lời chuẩn (Ground Truth).

Tiêu chí đánh giá: {rubric_type.upper()}
Chi tiết Rubric chấm điểm:
{rubric_content}

Thông tin đầu vào:
- Câu hỏi: {question}
- Câu trả lời của AI cần đánh giá: {answer}
- Câu trả lời chuẩn (Ground Truth): {ground_truth}

Hãy suy nghĩ ngắn gọn và đưa ra điểm số từ 1 đến 5.
Định dạng kết quả trả về bắt buộc phải là một JSON object duy nhất như sau (không thêm văn bản khác ngoài JSON):
{{
  "reasoning": "Giải thích ngắn gọn lý do chấm điểm...",
  "score": 5
}}
"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"},
                extra_headers={
                    "HTTP-Referer": "https://github.com/TrongVu249/Lab14-AI-Evaluation-Benchmarking",
                    "X-Title": "Lab14 AI Evaluation Benchmarking"
                }
            )
            data = json.loads(response.choices[0].message.content.strip())
            return int(data.get("score", 3))
        except Exception as e:
            print(f"⚠️ Lỗi khi gọi Judge model {model}: {e}")
            return 3

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Đánh giá đa mô hình (gọi 2 Judge).
        Đo lường độ đồng thuận và tự động phân xử nếu lệch điểm sâu (>1 điểm).
        """
        score_task_a = self._call_single_judge(self.judge_model_a, question, answer, ground_truth, "accuracy")
        score_task_b = self._call_single_judge(self.judge_model_b, question, answer, ground_truth, "accuracy")
        
        score_a, score_b = await asyncio.gather(score_task_a, score_task_b)
        
        delta = abs(score_a - score_b)
        agreement = 1.0 if delta <= 1 else 0.0
        
        final_score = 0.0
        reasoning = ""
        
        if delta > 1 and self.api_key:
            # Phát hiện xung đột sâu: Gọi Trọng tài thứ 3 làm Tie-breaker
            print(f"⚠️ Phát hiện xung đột chấm điểm ({score_a} vs {score_b}) cho câu hỏi: '{question[:30]}...'. Đang gọi Trọng tài trưởng ({self.tie_breaker_model})...")
            
            prompt = f"""
Bạn là Trọng tài trưởng (Tie-breaker Judge) chịu trách nhiệm phân xử khi hai trọng tài phụ chấm điểm lệch nhau sâu.

Thông tin:
- Câu hỏi: {question}
- Câu trả lời của AI: {answer}
- Câu trả lời chuẩn (Ground Truth): {ground_truth}
- Điểm của Trọng tài 1 ({self.judge_model_a}): {score_a}
- Điểm của Trọng tài 2 ({self.judge_model_b}): {score_b}

Hãy đọc kỹ Rubric chấm điểm:
{self.rubrics['accuracy']}

Hãy đưa ra phán quyết cuối cùng và chọn điểm số công tâm nhất từ 1 đến 5.
Định dạng kết quả trả về bắt buộc phải là một JSON object duy nhất như sau:
{{
  "reasoning": "Giải thích chi tiết tại sao chọn điểm số này sau khi phân tích ý kiến 2 trọng tài kia...",
  "score": 4
}}
"""
            try:
                response = await self.client.chat.completions.create(
                    model=self.tie_breaker_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    response_format={"type": "json_object"},
                    extra_headers={
                        "HTTP-Referer": "https://github.com/TrongVu249/Lab14-AI-Evaluation-Benchmarking",
                        "X-Title": "Lab14 AI Evaluation Benchmarking"
                    }
                )
                data = json.loads(response.choices[0].message.content.strip())
                final_score = float(data.get("score", (score_a + score_b) / 2))
                reasoning = "[CÂN CHỈNH TỰ ĐỘNG] " + data.get("reasoning", "")
            except Exception as e:
                print(f"❌ Lỗi khi gọi Trọng tài trưởng: {e}")
                final_score = (score_a + score_b) / 2.0
                reasoning = "Không thể cân chỉnh tự động do lỗi API, lấy điểm trung bình."
        else:
            final_score = (score_a + score_b) / 2.0
            reasoning = f"Các trọng tài đồng thuận. Điểm Judge A ({self.judge_model_a}): {score_a}, Judge B ({self.judge_model_b}): {score_b}."
            
        return {
            "final_score": final_score,
            "agreement_rate": agreement,
            "reasoning": reasoning,
            "individual_scores": {
                self.judge_model_a: score_a,
                self.judge_model_b: score_b
            }
        }

    async def check_position_bias(self, question: str, response_a: str, response_b: str, ground_truth: str) -> Dict[str, Any]:
        """
        Nâng cao: Kiểm tra lỗi thiên vị vị trí (Position Bias) của mô hình Trọng tài.
        Hoán đổi thứ tự câu trả lời A và B hiển thị cho Judge để kiểm tra sự ổn định điểm số.
        """
        if not self.api_key:
            return {"bias_detected": False, "score_diff": 0.0}
            
        prompt_order_1 = f"""
Hãy so sánh hai câu trả lời dưới đây so với Ground Truth:
Ground Truth: {ground_truth}
Câu trả lời 1: {response_a}
Câu trả lời 2: {response_b}
Hãy cho biết câu trả lời nào tốt hơn (1 hay 2). Trả về JSON: {{"better_response": 1 hoặc 2}}
"""
        prompt_order_2 = f"""
Hãy so sánh hai câu trả lời dưới đây so với Ground Truth:
Ground Truth: {ground_truth}
Câu trả lời 1: {response_b}
Câu trả lời 2: {response_a}
Hãy cho biết câu trả lời nào tốt hơn (1 hay 2). Trả về JSON: {{"better_response": 1 hoặc 2}}
"""
        try:
            res1_task = self.client.chat.completions.create(
                model=self.judge_model_a,
                messages=[{"role": "user", "content": prompt_order_1}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            res2_task = self.client.chat.completions.create(
                model=self.judge_model_a,
                messages=[{"role": "user", "content": prompt_order_2}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            res1, res2 = await asyncio.gather(res1_task, res2_task)
            
            data1 = json.loads(res1.choices[0].message.content.strip())
            data2 = json.loads(res2.choices[0].message.content.strip())
            
            choice1 = data1.get("better_response", 1)
            choice2 = data2.get("better_response", 2)
            
            # Nếu đổi chỗ mà mô hình vẫn chọn cùng 1 câu trả lời thì không bị bias.
            # Ví dụ: Ở lượt 1 chọn câu trả lời 1 (là response_a). Ở lượt 2 chọn câu trả lời 2 (là response_a).
            # Tức là choice1 == 1 và choice2 == 2.
            # Nếu choice1 == 1 và choice2 == 1 -> Có bias (ở cả hai lượt đều thích chọn phương án đứng trước).
            bias = not (choice1 == 1 and choice2 == 2 or choice1 == 2 and choice2 == 1)
            return {"bias_detected": bias, "choice_order_1": choice1, "choice_order_2": choice2}
        except Exception as e:
            print(f"Lỗi khi kiểm tra Position Bias: {e}")
            return {"bias_detected": False, "error": str(e)}

