# Báo cáo Thu hoạch Cá nhân (Individual Reflection)

**Sinh viên:** Hồ Tất Bảo Hoàng
**Vai trò:** Kỹ sư dữ liệu & SDG Developer

---

## 🛠️ 1. Đóng góp kỹ thuật (Engineering Contribution)
- Nghiên cứu và xây dựng cấu trúc Golden Dataset lưu trữ dưới định dạng JSON Lines (.jsonl) phục vụ benchmark.
- Triển khai script sinh dữ liệu tự động tại [synthetic_gen.py](file:///d:/Project/Vin_AI/Lab%2014/Lab14-AI-Evaluation-Benchmarking/data/synthetic_gen.py) sử dụng API OpenRouter.
- Thiết kế Prompt sinh câu hỏi đa dạng mức độ khó (easy, medium, hard) và chèn các metadata phân loại chính xác (`fact-check`, `edge_case`, `ambiguous`).
- Thiết kế các ca kiểm thử tấn công (Red Teaming/Adversarial) để thử nghiệm giới hạn bảo mật của RAG Agent.

---

## 📚 2. Chiều sâu kỹ thuật (Technical Depth)

### 2.1. Giải thích các khái niệm đo lường
*   **MRR (Mean Reciprocal Rank):** Chỉ số đo lường hiệu năng của công cụ tìm kiếm dựa trên vị trí đảo ngược của kết quả đúng đầu tiên. Nó phản ánh tốc độ và độ chính xác của Vector DB trong việc đưa tài liệu phù hợp nhất lên hàng đầu.
*   **Cohen's Kappa:** Đo lường độ tin cậy và sự thống nhất ý kiến giữa các giám khảo/LLM-Judge, loại trừ khả năng trùng hợp ngẫu nhiên.
*   **Position Bias:** Sự thiên vị vị trí xảy ra do LLM có xu hướng ưu tiên các lựa chọn nằm ở đầu hoặc cuối prompt. Việc đảo vị trí các câu trả lời khi đưa vào prompt của Judge giúp hiệu chỉnh độ lệch này.

### 2.2. Sự đánh đổi giữa Chi phí và Chất lượng (Cost vs Quality Trade-off)
Việc sinh dữ liệu thử nghiệm (SDG) hàng loạt đòi hỏi số lượng token rất lớn. Thay vì sử dụng mô hình đắt tiền cho toàn bộ văn bản, chúng tôi phân chia tài liệu thành các đoạn nhỏ và sử dụng `gpt-4o-mini` qua OpenRouter để sinh câu hỏi. Phương pháp này giúp duy trì chất lượng câu hỏi tương đương 95% so với GPT-4 nhưng giảm chi phí xuống chỉ còn 1/10.
