# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Đặng Tuấn Anh 
**Vai trò:** Eval / Quality Reporter  
**Ngày nộp:** 2026-04-15  

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**
- `eval_retrieval.py`: Chạy các câu hỏi test để đánh giá chất lượng tìm kiếm.
- `docs/quality_report_template.md`: Tổng hợp bằng chứng về sự cải thiện của dữ liệu.
- `artifacts/eval/`: Lưu trữ các file kết quả so sánh trước và sau khi fix lỗi.

**Kết nối với thành viên khác:**
Tôi là người "kiểm chứng" thành quả của cả nhóm. Tôi phối hợp với Hải để biết các kịch bản lỗi (inject) và Lâm để đảm bảo dữ liệu đã được nạp vào Chroma trước khi chạy eval.

**Bằng chứng (commit / comment trong code):**
- Thực hiện các lệnh chạy eval với các flag `--out` khác nhau.
- Phân tích cột `hits_forbidden` để phát hiện dữ liệu bẩn.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Tôi quyết định tập trung vào metric **`hits_forbidden`** hơn là chỉ nhìn vào `top1_doc_matches`. Trong bài toán quan sát dữ liệu (data observability), việc AI tìm thấy câu trả lời đúng là chưa đủ; chúng ta cần đảm bảo nó **không** tìm thấy các thông tin đã bị loại bỏ hoặc lỗi thời. 

Ví dụ, khi hỏi về cửa sổ hoàn tiền, nếu hệ thống trả về cả chunk "7 ngày" (đúng) và "14 ngày" (sai/stale) trong top-k, thì đó vẫn là một thất bại về mặt dữ liệu. Quyết định này giúp tôi phát hiện ra các lỗi "rò rỉ" dữ liệu (data leakage) từ các phiên bản cũ, điều mà các bộ test RAG thông thường hay bỏ qua. Tôi đã cấu hình script eval để quét toàn bộ context thay vì chỉ câu trả lời cuối cùng.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Trong đợt chạy đầu tiên, kết quả retrieval cho câu hỏi về chính sách nghỉ phép của HR luôn trả về kết quả từ năm 2025 thay vì 2026, mặc dù Student B khẳng định đã làm sạch.

**Triệu chứng:** `contains_expected=false` và nội dung chứa từ khóa "10 ngày phép".
**Xử lý:** Tôi đã truy vấn trực tiếp vào metadata của ChromaDB thông qua script debug và phát hiện ra rằng Student D chưa thực hiện `prune` các bản ghi cũ. Dữ liệu năm 2025 vẫn nằm trong DB và có độ tương đồng vector cao hơn bản 2026 do câu chữ ngắn gọn hơn. Tôi đã yêu cầu Student D sửa lại logic dọn dẹp và sau khi chạy lại, kết quả eval đã nhảy sang bản 2026 một cách chính xác.

---

## 4. Bằng chứng trước / sau (80–120 từ)

- **Run ID:** `2026-04-15T07-26Z`
- **Trạng thái Dữ liệu Ready:** 
Pipeline đã cung cấp 6 bản ghi sạch (`cleaned_records=6`). 
- **Scenario Dự Kiến (Refund Window):**
  - **Sau khi fix (Cleaned):**
    - `query: "Thời gian hoàn tiền?"`
    - `retrieved: "... trong vòng 7 ngày làm việc [cleaned: stale_refund_window]"`
    - `hits_forbidden: False` (Dữ liệu 14 ngày đã bị loại bỏ thành công).

---

## 5. Cải tiến tiếp theo (40–80 từ)

Tôi muốn xây dựng một **Golden Dataset** lớn hơn (khoảng 50 câu hỏi) và sử dụng LLM làm giám khảo (LLM-as-a-judge) để đánh giá độ liên quan của context một cách tự động, thay vì chỉ dựa vào so khớp từ khóa (keyword matching) đơn giản như hiện tại.
