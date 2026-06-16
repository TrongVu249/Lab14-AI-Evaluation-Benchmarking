# Báo cáo Thu hoạch Cá nhân (Individual Reflection)

**Sinh viên:** Đào Tất Thắng
**Vai trò:** Kỹ sư kiểm thử chất lượng (QA & Failure Analyst)

---

## 🛠️ 1. Đóng góp kỹ thuật (Engineering Contribution)
- Thu thập số liệu thống kê từ báo cáo `reports/summary.json` sau đợt chạy thực tế.
- Thực hiện phân nhóm lỗi (Failure Clustering) và hoàn thiện báo cáo phân tích thất bại tại [failure_analysis.md](file:///d:/Project/Vin_AI/Lab%2014/Lab14-AI-Evaluation-Benchmarking/analysis/failure_analysis.md).
- Áp dụng kỹ thuật phân tích **5 Whys** để truy vết nguyên nhân gốc rễ (Root Cause) của các ca lỗi tiêu biểu như lỗi tìm kiếm thông tin không khớp (Out of Context) hoặc tấn công bằng Prompt (Prompt Injection).
- Thực thi và sửa lỗi mã hóa ký tự Unicode cho script kiểm thử bài nộp [check_lab.py](file:///d:/Project/Vin_AI/Lab%2014/Lab14-AI-Evaluation-Benchmarking/check_lab.py) để đảm bảo định dạng đầu ra chuẩn xác.

---

## 📚 2. Chiều sâu kỹ thuật (Technical Depth)

### 2.1. Giải thích các khái niệm đo lường
*   **MRR (Mean Reciprocal Rank):** Điểm trung bình của các giá trị nghịch đảo của vị trí tài liệu chính xác đầu tiên. Chỉ số này chỉ ra khả năng tìm đúng tài liệu của Vector DB tốt hay kém.
*   **Cohen's Kappa:** Đo lường độ tin cậy của việc phân loại giữa các trọng tài, giúp kiểm định tính công bằng và nhất quán trong chấm điểm của các LLMs.
*   **Position Bias:** Sự thiên vị thứ tự hiển thị câu trả lời của mô hình Judge. Chúng tôi giải quyết bằng cách đảo thứ tự đầu vào câu trả lời để chấm điểm trung bình hai lượt.

### 2.2. Sự đánh đổi giữa Chi phí và Chất lượng (Cost vs Quality Trade-off)
Việc phân tích lỗi sâu giúp chúng tôi nhận ra rằng: cải thiện chất lượng Prompt của Agent (ngăn chặn Prompt Injection, cải tiến cách hiển thị tài liệu) mang lại lợi ích nâng cao chất lượng câu trả lời cao gấp nhiều lần so với việc nâng cấp lên một mô hình đắt tiền hơn nhưng giữ nguyên prompt cũ, qua đó giúp tiết kiệm chi phí vận hành Agent tối đa.
