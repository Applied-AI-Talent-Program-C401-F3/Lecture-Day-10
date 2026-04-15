# Quality report — Lab Day 10 (nhóm)

**run_id:** `2026-04-15T08-59Z`  
**Ngày:** `2026-04-15`

---

## 1. Tóm tắt số liệu

| Chỉ số | Trước (Raw/Inject) | Sau (Cleaned) | Ghi chú |
|--------|-------|-----|---------|
| raw_records | 10 | 10 | Tương đương số record từ CSV nguồn |
| cleaned_records | 6 | 6 | Số record vượt qua validate ban đầu |
| quarantine_records | 4 | 4 | Số record đưa vào diện cách ly do cũ/lỗi |
| Expectation halt? | Fail (nhưng skip) | No (Pass toàn bộ) | Dữ liệu sau clean đi qua Expectation an toàn |

---

## 2. Before / after retrieval (bắt buộc)

> Tham khảo kết quả chạy test và eval: 
> - [Sau tiêm lỗi](../artifacts/eval/after_inject_bad.csv)
> - [Kết quả mới ngặt từ bộ grading mới](../artifacts/eval/grading_test.jsonl)

**Câu hỏi then chốt:** refund window (`gq_d10_01` - thay thế cho `q_refund_window`)  
**Trước (Inject Bad Data):** `hits_forbidden = yes` (Ghi chú: Pipeline giữ lại chính sách cũ, dẫn đến việc chatbot/quy trình trích xuất nhầm đoạn văn mang số "14 ngày làm việc")  
**Sau (Grading Test):** `{"id": "gq_d10_01", "contains_expected": true, "hits_forbidden": false}` 
*(Ghi chú: Luật 14 ngày đã bị xóa bỏ hoàn toàn, thay thế bằng đáp án 7 ngày hợp lệ)*

**Merit (khuyến nghị):** versioning HR — `gq_d10_03` (thay thế cho `q_leave_version`)

**Trước:** Đã đúng form vì tài liệu chưa tiêm lỗi liên quan HR.
**Sau (Grading Test):** `{"id": "gq_d10_03", "contains_expected": true, "hits_forbidden": false, "top1_doc_matches": true}`  
*(Ghi chú: doc_id chính xác (`hr_leave_policy`) đã lọt top 1 của RAG truy vấn, pipeline đã quarantine đúng HR policy cũ)*

---

## 3. Freshness & monitor

> Kết quả `freshness_check` (PASS/WARN/FAIL) và giải thích SLA bạn chọn.

**Kết quả:** FAIL
**Giải thích:**
```json
{"run_id": "2026-04-15T08-59Z", "sla_hours": 24.0, "boundaries": {"source_to_ingest": {"age_hours": 121.0, "status": "FAIL"}, "ingest_to_publish": {"age_hours": 0.0, "status": "PASS"}}}
```
Hệ thống thiết lập SLA = 24h. Do dữ liệu policy_export_dirty.csv có thông tin xuất từ `2026-04-10T08:00:00` (đã qua 121h kể từ thời gian hiện tại 2026-04-15), Phase 1 (`source_to_ingest`) báo FAIL. Pha pipeline `ingest_to_publish` diễn ra nhanh nên đánh PASS.

---

## 4. Corruption inject (Sprint 3)

> Mô tả cố ý làm hỏng dữ liệu kiểu gì (duplicate / stale / sai format) và cách phát hiện.

**Tiêm lỗi (Inject Corruption):**
Cố ý bỏ qua file config fix lỗi hoàn tiền bằng lệnh cờ `--no-refund-fix` và tiếp tục lưu embedding mà không validate (`--skip-validate`). Việc này đẩy chính sách đổi trả bị stale (hoàn tiền trong 14 ngày) vào ChromaDB.

**Cách phát hiện:**
- Nếu không skip-validate: Dòng Expectation sẽ cảnh báo và ngắt pipeline: `expectation[refund_no_stale_14d_window] FAIL (halt) :: violations=1`
- Khi làm retrieval eval: Output `hits_forbidden` cho `q_refund_window` đã biến thành `yes` (chứa keyword cấm -> luật 14 ngày). Sau quá trình làm sạch bình thường, nó quay lại là `no`, chứng tỏ pipeline sửa được lỗi này.

---

## 5. Hạn chế & việc chưa làm

- Cần đồng bộ và update thêm nhiều luật check (expectations) mới từ code rules và expectation vào file này sau cùng.
