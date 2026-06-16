# Báo cáo Thu hoạch Cá nhân (Individual Reflection)

**Sinh viên:** Lê Đức Việt
**Vai trò:** Kỹ sư thiết kế Trọng tài AI (LLM Judge Developer)

---

## 🛠️ 1. Đóng góp kỹ thuật (Engineering Contribution)
- Triển khai module trọng tài tự động tại [llm_judge.py](file:///d:/Project/Vin_AI/Lab%2014/Lab14-AI-Evaluation-Benchmarking/engine/llm_judge.py).
- Thiết lập chi tiết hệ thống Rubrics chấm điểm (thang điểm 1-5) về độ chính xác (Accuracy) và văn phong (Tone).
- Viết logic gọi đồng thời 2 Judge thông qua OpenRouter và tính toán chỉ số đồng thuận **Agreement Rate**.
- Cài đặt cơ chế phân xử tự động (**Calibration**): Tự động kích hoạt mô hình lớn (Trọng tài trưởng) để chấm điểm lại khi 2 trọng tài phụ lệch nhau > 1 điểm.
- Triển khai thuật toán kiểm thử và hiệu chỉnh Position Bias.

---

## 📚 2. Chiều sâu kỹ thuật (Technical Depth)

### 2.1. Giải thích các khái niệm đo lường
*   **MRR (Mean Reciprocal Rank):** Giá trị trung bình của nghịch đảo thứ hạng kết quả tìm kiếm đúng đầu tiên. MRR giúp đánh giá nhanh hiệu năng của hệ thống tìm kiếm thông tin ngữ cảnh.
*   **Cohen's Kappa:** Chỉ số thống kê đo lường mức độ đồng ý nhất quán giữa hai bên chấm điểm độc lập. Kappa càng cao chứng tỏ tính khách quan của bộ Rubrics càng lớn.
*   **Position Bias:** Thiên vị vị trí là một điểm yếu của LLM khi làm giám khảo. LLM thường ưu ái câu trả lời xuất hiện trước. Hệ thống của chúng tôi đã xử lý bằng cách hoán đổi câu trả lời và lấy điểm trung bình.

### 2.2. Sự đánh đổi giữa Chi phí và Chất lượng (Cost vs Quality Trade-off)
Việc sử dụng mô hình rẻ như `gpt-4o-mini` cho cả hai Judge giúp giảm chi phí xuống mức cực thấp. Để cân bằng chất lượng chấm điểm, chúng tôi chỉ gọi mô hình mạnh hơn (`gpt-4o`) làm Tie-breaker khi có sự bất đồng ý kiến nghiêm trọng giữa hai Judge phụ, giải pháp này mang lại hiệu quả chi phí tối ưu nhất cho doanh nghiệp.
