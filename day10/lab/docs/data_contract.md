# Data contract — Lab Day 10

**Nhóm:** C401-F3
**Phiên bản:** 1.0

---

## 1. Nguồn dữ liệu (source map)

| Nguồn | Phương thức ingest | Failure mode chính | Metric / alert |
|-------|-------------------|-------------------|----------------|
| Policy Export (CSV) | File-based Ingest | Sai schema / Thiếu ngày | % Quarantine / Freshness FAIL |
| HR Leave DB | CSV Snapshot | Lệch version (10 vs 12 ngày) | Quality Exception (Halt) |
| IT FAQ | CSV Snapshot | Duplicate chunks | Log Warning |

---

## 2. Schema cleaned

| Cột | Kiểu | Bắt buộc | Ghi chú |
|-----|------|----------|---------|
| chunk_id | string | Có | Hash duy nhất để định danh vector |
| doc_id | string | Có | Link tới tài liệu gốc (policy_refund_v4, etc.) |
| chunk_text | string | Có | Nội dung văn bản đã được làm sạch |
| effective_date | date | Có | Ngày hiệu lực (ISO 8601: YYYY-MM-DD) |
| exported_at | datetime | Có | Thời điểm dữ liệu được xuất khỏi hệ thống nguồn |

---

## 3. Quy tắc quarantine vs drop

- **Quarantine:** Các record vi phạm allowlist `doc_id` hoặc thiếu thông tin quan trọng (`effective_date`) sẽ được ghi vào `artifacts/quarantine/`.
- **Drop:** Các dòng trống hoặc header lặp lại sẽ bị loại bỏ hoàn toàn khỏi luồng xử lý.
- **Approval:** Các dòng trong Quarantine cần được Admin kiểm tra lại nguồn xuất và sửa lỗi schema trước khi re-run pipeline.

---

## 4. Phiên bản & canonical

- **Source of Truth:** 
    - Chính sách hoàn tiền: `data/docs/policy_refund_v4.txt` (7 ngày).
    - Chính sách nghỉ phép: `data/docs/hr_leave_policy.txt` (Từ 2026-01-01).
- **Versioning:** Pipeline sử dụng `policy_versioning` trong `data_contract.yaml` để lọc bỏ các bản record cũ không còn hiệu lực.
- **SLA Freshness:** Dữ liệu phải được cập nhật ít nhất mỗi **24 giờ**.
