# Báo cáo Thu hoạch Cá nhân (Individual Reflection)

**Sinh viên:** Nguyễn Phương Nam
**Vai trò:** Kỹ sư đánh giá tìm kiếm (Retrieval Evaluator)

---

## 🛠️ 1. Đóng góp kỹ thuật (Engineering Contribution)
- Triển khai toàn bộ module đánh giá Retrieval tại [retrieval_eval.py](file:///d:/Project/Vin_AI/Lab%2014/Lab14-AI-Evaluation-Benchmarking/engine/retrieval_eval.py).
- Lập trình thuật toán tính toán **Hit Rate** ở mức Top-K (mặc định K=3) để kiểm tra xem tài liệu đúng có được truy xuất thành công hay không.
- Lập trình thuật toán tính toán chỉ số **MRR** (Mean Reciprocal Rank) để đánh giá độ chính xác về mặt thứ tự của tài liệu được tìm kiếm.
- Phát triển phương thức chạy eval theo lô (`evaluate_batch`) tối ưu hiệu năng tính toán.

---

## 📚 2. Chiều sâu kỹ thuật (Technical Depth)

### 2.1. Giải thích các khái niệm đo lường
*   **MRR (Mean Reciprocal Rank):** Công thức tính là $1 / \text{Rank}$, trong đó Rank là vị trí của tài liệu chính xác đầu tiên trong kết quả tìm kiếm. Nếu tài liệu đúng nằm ở dòng đầu tiên, MRR đạt tối đa là 1.0. MRR phản ánh chất lượng xếp hạng của Vector DB, giúp cải tiến thuật toán search.
*   **Cohen's Kappa:** Thống kê đánh giá sự thống nhất giữa hai bên phân loại định tính. Trong bài lab, nó thể hiện tính đồng thuận chấm điểm của 2 mô hình LLM.
*   **Position Bias:** Xu hướng mô hình đánh giá bị tác động bởi vị trí sắp xếp thông tin. Bằng cách đảo ngược thứ tự các câu trả lời khi gửi prompt cho Judge, chúng ta có thể trung hòa sự thiên lệch này.

### 2.2. Sự đánh đổi giữa Chi phí và Chất lượng (Cost vs Quality Trade-off)
Đo lường Retrieval là bước có chi phí rẻ nhất nhưng mang lại giá trị cao nhất. Bằng cách sử dụng các phép toán so sánh Python thuần túy trên các ID tài liệu được Agent trả về thay vì gọi LLM để đánh giá Retrieval, chúng tôi đạt được độ chính xác tuyệt đối (100%) với chi phí bằng **0 USD** và tốc độ thực thi chỉ trong vài mili-giây.
