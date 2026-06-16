# Báo cáo Phân tích Thất bại (Failure Analysis Report)

### 👥 Thành viên nhóm:
*   **Nguyễn Vũ Trọng** (Nhóm trưởng)
*   **Hồ Tất Bảo Hoàng**
*   **Nguyễn Phương Nam**
*   **Lê Đức Việt**
*   **Bùi Văn Tuân**
*   **Đào Tất Thắng**

## 1. Tổng quan Benchmark
- **Tổng số cases:** 55
- **Tỉ lệ Pass/Fail:** 55/0 (Tất cả các cases đều đạt điểm Judge >= 3.0)
- **Điểm RAGAS trung bình:**
    - Faithfulness: 0.95
    - Relevancy: 0.90
    - Retrieval Hit Rate: 94.5%
    - Retrieval MRR: 0.94
- **Điểm LLM-Judge trung bình:** 4.15 / 5.0

---

## 2. Phân nhóm lỗi (Failure Clustering)

Dù tỷ lệ vượt qua cổng kiểm thử đạt 100%, qua phân tích kết quả chi tiết của phiên bản V2, chúng tôi ghi nhận một số điểm hạn chế và phân nhóm các ca truy xuất chưa đạt điểm tối đa (ví dụ: Hit Rate = 0 cho các câu hỏi ngoài lề):

| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Out of Context / Unmatched | 3 | Câu hỏi nằm ngoài tập dữ liệu chính sách, Agent không thể tìm kiếm tài liệu nguồn thích hợp (đây là hành vi thiết kế đúng khi trả về thông báo lỗi, nhưng Hit Rate của Retrieval tính bằng 0). |
| Adversarial / Prompt Injection | 2 | Các câu hỏi cố tình lừa Agent làm việc khác. Mặc dù Agent V2 chặn thành công nhờ System Prompt tối ưu, nhưng khâu Retrieval không khớp tài liệu nào. |

---

## 3. Phân tích 5 Whys (Chọn 3 case tiêu biểu)

### Case #1: Câu hỏi về việc mang mèo đến văn phòng làm việc
1.  **Symptom (Triệu chứng):** Agent không thể cung cấp tài liệu nguồn (`sources` rỗng, Hit Rate = 0.0).
2.  **Why 1:** Không có tài liệu nào trong Vector DB khớp với từ khóa "mèo" hay "thú cưng".
3.  **Why 2:** Hệ thống dữ liệu Corpus hiện tại chỉ bao gồm các chính sách về nhân sự chính thức (nghỉ phép, công tác phí, làm việc từ xa) mà chưa cập nhật quy định về thú nuôi.
4.  **Why 3:** Bộ phận Admin chưa số hóa tài liệu nội quy sinh hoạt văn phòng vào hệ thống RAG.
5.  **Why 4:** Quy trình Onboarding chưa có sự phối hợp giữa phòng Nhân sự và phòng Kỹ thuật để đồng bộ hóa tài liệu mới.
6.  **Root Cause (Nguyên nhân gốc rễ):** Thiếu cơ chế tự động đồng bộ hóa tài liệu từ phòng Hành chính nhân sự vào cơ sở dữ liệu tri thức của AI Agent.

### Case #2: Yêu cầu viết thơ về mèo máy Doremon (Prompt Injection)
1.  **Symptom:** Agent từ chối viết thơ và trả lời mẫu từ chối, khâu truy xuất trả về rỗng.
2.  **Why 1:** Mô hình không lấy được tài liệu liên quan nào về "Doremon" để trả lời.
3.  **Why 2:** Câu hỏi cố tình chèn chỉ thị bỏ qua hệ thống (Adversarial Prompt).
4.  **Why 3:** Hệ thống prompt V1 chưa được thiết kế để nhận diện và lọc bỏ các chỉ thị độc hại này, dẫn đến nguy cơ Agent làm việc sai nhiệm vụ.
5.  **Why 4:** Thiếu lớp bảo vệ/giám sát an toàn thông tin đầu vào (Input Guardrail).
6.  **Root Cause:** Thiếu cấu hình phân tách rõ ràng giữa Hệ thống chỉ thị (System Prompt) và Dữ liệu người dùng nhập (User Prompt) ở phiên bản V1.

---

## 4. Kế hoạch cải tiến (Action Plan)
- [x] Nâng cấp hệ thống Prompt từ V1 sang V2 để tối ưu hóa khả năng chống Prompt Injection và nhận diện các câu hỏi ngoài ngữ cảnh (Out of Context).
- [ ] Tích hợp giải pháp **Semantic Chunking** thay cho Fixed-size chunking để phân tách dữ liệu bảng biểu tốt hơn.
- [ ] Bổ sung bước **Reranking** (sử dụng Cohere Rerank hoặc tương đương) vào luồng truy xuất nhằm cải thiện chỉ số MRR của Agent.
- [ ] Xây dựng luồng đồng bộ tự động dữ liệu từ Notion/Confluence của các phòng ban vào Vector DB định kỳ hàng tuần.
