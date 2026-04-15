# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Lưu Lê Gia Bảo
**Vai trò:** Ingestion / Raw Owner  
**Ngày nộp:** 2026-04-15  
**Độ dài yêu cầu:** 400–650 từ

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

- `etl_pipeline.py`: Xây dựng CLI entrypoint, hệ thống logging và quản lý `run_id`.
- `contracts/data_contract.yaml`: Định nghĩa metadata cho nguồn dữ liệu raw.
- `data/raw/`: Phân tích cấu trúc file CSV bẩn để lập bản đồ schema.

**Kết nối với thành viên khác:**
Tôi cung cấp `run_id` và các tham số đầu vào cho Thái Doãn Minh Hải (Cleaning) và Hoàng Quốc Hùng (Quality). Tôi cũng đảm bảo log được ghi đồng nhất để Student F có thể tổng hợp báo cáo kiến trúc.

**Bằng chứng (commit / comment trong code):**

- Hàm `cmd_run` trong `etl_pipeline.py` khởi tạo log path dựa trên `run_id`.
- Khai báo các đường dẫn mặc định `RAW_DEFAULT`, `LOG_DIR`, `MAN_DIR`.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Tôi quyết định sử dụng **UTC ISO format** cho `run_id` (ví dụ: `2026-04-15T07-26Z`) thay vì dùng số thứ tự đơn giản. Quyết định này giúp việc truy vết (lineage) trở nên chính xác tuyệt đối khi hệ thống chạy trên nhiều môi trường khác nhau.

Ngoài ra, tôi thiết kế hàm `_log` để tự động tạo thư mục cha nếu chưa tồn tại. Điều này giúp pipeline "tự phục hồi" khi người dùng xóa thư mục `artifacts/` giữa các phiên chạy. Tôi cũng chọn lưu `manifest.json` chứa toàn bộ metadata của run đó để Lương Trung Kiên có thể kiểm tra freshness một cách dễ dàng mà không cần đọc lại file log văn bản thô.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Trong quá trình ingest dữ liệu raw, tôi phát hiện cột `exported_at` trong file CSV thỉnh thoảng bị thiếu hoặc có giá trị rỗng. Điều này làm cho hệ thống freshness check của Lương Trung Kiên bị crash vì không có dữ liệu để so sánh.

**Triệu chứng:** Log hiển thị `ValueError: max() arg is an empty sequence` khi tính toán `latest_exported_at`.
**Xử lý:** Tôi đã thêm giá trị mặc định `default=""` trong hàm `max()` và bổ sung logic kiểm tra `if cleaned:` trước khi ghi manifest. Đồng thời, tôi phối hợp với Thái Doãn Minh Hải để đảm bảo cột này được giữ lại trong quá trình transform kể cả khi nó rỗng, giúp pipeline không bị ngắt quãng giữa chừng.

---

## 4. Bằng chứng trước / sau (80–120 từ)

- **Run ID:** `2026-04-15T07-26Z`
- **Trước (Log):** `ERROR: raw file not found: ...` (do sai đường dẫn mặc định).
- **Sau (Log Trích Xuất):**

```
run_id=2026-04-15T07-26Z
raw_records=10
cleaned_records=6
quarantine_records=4
manifest_written=artifacts/manifests/manifest_2026-04-15T07-26Z.json
```

---

## 5. Cải tiến tiếp theo (40–80 từ)

Nếu có thêm 2 giờ, tôi sẽ tích hợp thư viện `structlog` để ghi log dưới dạng JSON ngay từ đầu. Điều này sẽ giúp các công cụ monitoring tự động dễ dàng phân tích dữ liệu log mà không cần dùng regex phức tạp để tách `raw_records` hay `run_id`.
