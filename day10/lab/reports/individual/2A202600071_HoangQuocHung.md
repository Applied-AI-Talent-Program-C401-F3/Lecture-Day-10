# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Hoàng Quốc Hùng
**Vai trò:** Quality / Expectations Owner  
**Ngày nộp:** 2026-04-15  
**Độ dài yêu cầu:** 400–650 từ

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**
- `quality/expectations.py`: Thiết kế và cài đặt bộ quy tắc kiểm định chất lượng dữ liệu (Expectation Suite).
- `etl_pipeline.py`: Tích hợp logic `halt` để ngắt pipeline khi gặp lỗi nghiêm trọng.

**Kết nối với thành viên khác:**
Tôi đóng vai trò "người gác cổng" giữa Hải (Cleaning) và Lâm (Embedding). Nếu dữ liệu Hải làm sạch không đạt chuẩn, tôi sẽ yêu cầu dừng hệ thống để tránh làm nhiễm bẩn Vector Database của Lâm.

**Bằng chứng (commit / comment trong code):**
- Định nghĩa class `ExpectationResult`.
- Cài đặt 2 rule mới: `min_doc_coverage_3` và `chunk_min_words_5`.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Tôi đã quyết định phân loại lỗi thành hai mức độ: **Warn** và **Halt**. 
- Các lỗi như `chunk_min_words_5` chỉ ở mức **Warn** vì một chunk ngắn có thể vẫn có giá trị (ví dụ: một câu lệnh FAQ ngắn gọn). Chúng tôi ghi log nhưng vẫn cho phép embed.
- Ngược lại, lỗi `min_doc_coverage_3` được đặt là **Halt**. Nếu tập dữ liệu cleaned thiếu mất một loại policy quan trọng (như IT hoặc HR), RAG sẽ trả lời sai hoàn toàn. Việc "thà không có dữ liệu mới còn hơn có dữ liệu thiếu" là chiến lược để bảo vệ độ tin cậy của hệ thống AI. 

Tôi cũng chọn không sử dụng thư viện Great Expectations (GE) để giữ cho pipeline nhẹ và dễ debug, nhưng cấu trúc code của tôi đã sẵn sàng để chuyển sang GE nếu dự án mở rộng.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Trong đợt Sprint 3 khi Tuấn Anh thử nghiệm inject dữ liệu lỗi (bỏ fix refund), pipeline vẫn tiếp tục chạy và embed dữ liệu sai vào database.

**Triệu chứng:** Log ghi `FAIL` nhưng pipeline vẫn trả về `PIPELINE_OK`.
**Xử lý:** Tôi đã phát hiện lỗi logic trong hàm `cmd_run` ở `etl_pipeline.py`, nơi biến `halt` chưa được kiểm tra đúng cách trước khi gọi `cmd_embed_internal`. Tôi đã sửa code để trả về `exit 2` ngay khi có lỗi `halt`, đồng thời bổ sung flag `--skip-validate` dành riêng cho mục đích demo của Tuấn Anh, giúp việc thử nghiệm "before/after" vẫn thực hiện được mà không bị kẹt bởi cơ chế bảo vệ của tôi.

---

## 4. Bằng chứng trước / sau (80–120 từ)

- **Run ID:** `2026-04-15T07-26Z`
- **Dòng Log (Halt - PASS):**
`expectation[min_doc_coverage_3] OK (halt) :: distinct_docs=4` (Đạt yêu cầu tối thiểu 3 docs).
- **Dòng Log (Warn - PASS):**
`expectation[chunk_min_words_5] OK (warn) :: under_word_count=0` (Không có chunk nào quá ngắn).
- **Kết quả:** Pipeline chạy thông suốt với 8/8 expectation đạt trạng thái OK.

---

## 5. Cải tiến tiếp theo (40–80 từ)

Tôi sẽ tích hợp `pydantic` để thực hiện data validation ở mức schema chặt chẽ hơn. Việc này giúp tự động hóa việc kiểm tra kiểu dữ liệu (type hint) và cho phép xuất báo cáo lỗi chi tiết dưới dạng JSON để tích hợp vào Dashboard sau này.
