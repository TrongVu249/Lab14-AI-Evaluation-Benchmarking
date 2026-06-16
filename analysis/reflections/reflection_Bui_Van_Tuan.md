# Báo cáo Thu hoạch Cá nhân (Individual Reflection)

**Sinh viên:** Bùi Văn Tuân
**Vai trò:** Kỹ sư tối ưu hiệu năng (Performance & Concurrency Engineer)

---

## 🛠️ 1. Đóng góp kỹ thuật (Engineering Contribution)
- Phát triển và tối ưu bộ điều phối chạy bất đồng bộ tại [runner.py](file:///d:/Project/Vin_AI/Lab%2014/Lab14-AI-Evaluation-Benchmarking/engine/runner.py).
- Sử dụng `asyncio.Semaphore` để giới hạn số lượng luồng chạy đồng thời (`max_concurrency`), tránh hoàn toàn lỗi API Rate Limit (429 Too Many Requests).
- Tích hợp logic đo lường thời gian trễ (latency) cho từng test case.
- Thiết lập bộ đếm token sử dụng và tính toán chi phí (Cost USD) thực tế của đợt chạy dựa trên thông tin phản hồi của API.

---

## 📚 2. Chiều sâu kỹ thuật (Technical Depth)

### 2.1. Giải thích các khái niệm đo lường
*   **MRR (Mean Reciprocal Rank):** Đo lường mức độ hiệu quả của việc tìm kiếm tài liệu nguồn thông qua giá trị nghịch đảo thứ hạng kết quả khớp đầu tiên.
*   **Cohen's Kappa:** Hệ số thống kê đánh giá tính đồng nhất ý kiến giữa các giám khảo đánh giá, giúp đảm bảo kết quả chấm điểm là khách quan.
*   **Position Bias:** Lỗi thiên vị vị trí của LLM. Chúng ta kiểm soát lỗi này bằng cách hoán đổi vị trí câu trả lời khi hiển thị cho mô hình và so sánh điểm số hai lần chấm.

### 2.2. Sự đánh đổi giữa Chi phí và Chất lượng (Cost vs Quality Trade-off)
Khi triển khai chạy song song bất đồng bộ (Async), nếu không có kiểm soát luồng (`Semaphore`), hệ thống sẽ gửi hàng loạt yêu cầu cùng một lúc, gây ra lỗi nghẽn hoặc vượt ngưỡng Rate Limit, dẫn đến lãng phí chi phí gọi API lỗi. Việc giới hạn `max_concurrency=10` giúp cân bằng giữa hiệu năng tốc độ chạy (hoàn thành 55 cases chỉ trong chưa đầy 2 giây) và độ ổn định của API.
