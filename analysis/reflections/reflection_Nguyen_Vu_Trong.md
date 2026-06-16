# Báo cáo Thu hoạch Cá nhân (Individual Reflection)

**Sinh viên:** Nguyễn Vũ Trọng
**Vai trò:** Nhóm trưởng & Kỹ sư tích hợp RAG

---

## 🛠️ 1. Đóng góp kỹ thuật (Engineering Contribution)
- Thiết kế kiến trúc tổng thể cho hệ thống **Evaluation Factory**, điều phối hoạt động phát triển của các thành viên.
- Phát triển và cải tiến RAG Agent tại [main_agent.py](file:///d:/Project/Vin_AI/Lab%2014/Lab14-AI-Evaluation-Benchmarking/agent/main_agent.py): Thiết lập cơ chế tìm kiếm keyword matching trên tập dữ liệu chính sách doanh nghiệp thực tế.
- Tích hợp kết nối OpenRouter API, cấu hình các mô hình tối ưu chi phí (như `gpt-4o-mini`) và thiết lập cơ chế tự động Fallback bảo vệ hệ thống khi mất mạng hoặc không có API Key.
- Phát triển logic **Release Gate** tự động so sánh phiên bản cũ V1 và V2 dựa trên các ngưỡng chỉ số an toàn.

---

## 📚 2. Chiều sâu kỹ thuật (Technical Depth)

### 2.1. Giải thích các khái niệm đo lường
*   **MRR (Mean Reciprocal Rank):** Đo lường chất lượng tìm kiếm dựa trên vị trí xuất hiện của tài liệu chính xác đầu tiên trong kết quả trả về. Nếu tài liệu đúng nằm ở vị trí đầu tiên, Rank = 1 (MRR = 1/1 = 1.0). Nếu nằm ở vị trí thứ $i$, MRR = $1/i$. Chỉ số này rất quan trọng để đánh giá độ nhạy của Vector DB.
*   **Cohen's Kappa:** Hệ số dùng để đo lường mức độ đồng thuận giữa các Judge (Trọng tài LLM) sau khi đã loại bỏ yếu tố ngẫu nhiên. Kappa chạy từ -1 đến 1. Giá trị càng gần 1 thể hiện các Judge chấm điểm rất nhất quán và khách quan, ngược lại nếu Kappa thấp chứng tỏ rubrics chấm điểm chưa rõ ràng.
*   **Position Bias (Thiên vị vị trí):** Hiện tượng mô hình Judge có xu hướng chấm điểm cao hơn cho câu trả lời đứng ở vị trí đầu tiên (hoặc vị trí sau cùng) bất kể chất lượng thực tế. Cách khắc phục là hoán đổi thứ tự hiển thị câu trả lời A-B và B-A khi gọi Judge rồi lấy điểm trung bình.

### 2.2. Sự đánh đổi giữa Chi phí và Chất lượng (Cost vs Quality Trade-off)
Trong môi trường doanh nghiệp, sử dụng mô hình lớn như `gpt-4o` hay `claude-3-5-sonnet` cho 100% các lượt đánh giá sẽ cực kỳ tốn kém khi tập test lớn. Chúng tôi đề xuất giải pháp tối ưu:
- Sử dụng mô hình cực rẻ nhưng hiệu quả cao như `gpt-4o-mini` cho các vòng đánh giá cơ bản.
- Chỉ kích hoạt mô hình lớn đóng vai trò **Trọng tài trưởng (Tie-breaker)** khi có sự xung đột điểm số sâu giữa các trọng tài phụ (lệch > 1 điểm), giúp giảm tới 80% chi phí mà không suy giảm độ chính xác của hệ thống.
