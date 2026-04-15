# Báo Cáo Cá Nhân --- Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Lương Trung Kiên\
**Vai trò:** Monitoring & Docs Owner\
**Ngày nộp:** 2026-04-15\
**Độ dài:** \~500-1000 từ

------------------------------------------------------------------------

## 1. Tôi phụ trách phần nào? (80--120 từ)

**File / module:** - `etl_pipeline.py` (hàm `freshness`, ghi manifest,
kiểm tra artifact)\
- `docs/runbook.md`, `docs/pipeline_architecture.md`,
`docs/data_contract.md`\
- `data_contract.yaml`

**Kết nối với thành viên khác:**\
Tôi nhận dữ liệu đã được ingest và làm sạch từ các thành viên phụ trách
ETL (Student A/B), sau đó giám sát trạng thái pipeline và đảm bảo dữ
liệu được publish đúng chuẩn contract. Các tài liệu tôi xây dựng giúp
team retrieval và evaluation hiểu rõ cấu trúc dữ liệu và cách xử lý sự
cố khi hệ thống gặp lỗi.

**Bằng chứng (commit / logic):** - Thiết lập kiểm tra freshness dựa trên
`manifest.json`\
- Cấu hình `owner_team` và `alert_channel` trong `data_contract.yaml`\
- Xây dựng runbook với các kịch bản lỗi thực tế (freshness fail,
pipeline halt)

------------------------------------------------------------------------

## 2. Một quyết định kỹ thuật (100--150 từ)

Quyết định kỹ thuật quan trọng nhất của tôi là triển khai cơ chế
**Freshness Check dựa trên manifest** thay vì kiểm tra trực tiếp từ
nguồn dữ liệu. Cụ thể, pipeline sẽ ghi lại metadata (đặc biệt là
`latest_exported_at`) vào `manifest.json` sau mỗi lần chạy, và bước
monitoring sẽ sử dụng thông tin này để so sánh với SLA (ví dụ: 4 giờ).

Cách tiếp cận này giúp tách biệt rõ ràng giữa **data processing layer**
và **observability layer**, tránh việc monitoring phụ thuộc trực tiếp
vào data source (có thể chậm hoặc không ổn định). Ngoài ra, nó còn giúp
tái sử dụng thông tin trong các bước downstream như alerting hoặc audit.
Mặc dù yêu cầu pipeline phải ghi manifest chính xác, nhưng đổi lại hệ
thống trở nên minh bạch và dễ debug hơn khi xảy ra sự cố.

------------------------------------------------------------------------

## 3. Một lỗi hoặc anomaly đã xử lý (100--150 từ)

Trong quá trình kiểm tra, tôi phát hiện hệ thống luôn trả về cảnh báo
freshness (`WARN`) dù pipeline vừa mới chạy xong.

**Triệu chứng:**\
Freshness check báo dữ liệu "cũ" (ví dụ: 17h \> SLA 4h) mặc dù dữ liệu
đã được cập nhật gần đây.

**Nguyên nhân:**\
Trường `latest_exported_at` trong `manifest.json` không được cập nhật
đúng giá trị thực tế, mà đang lấy giá trị mặc định hoặc không phản ánh
dữ liệu mới nhất trong `cleaned.csv`.

**Xử lý:**\
Tôi đã điều chỉnh logic trong pipeline để tính `max(exported_at)` từ
toàn bộ `cleaned_rows`, sau đó ghi giá trị này vào manifest. Sau khi
fix, freshness check đã phản ánh đúng trạng thái dữ liệu và chuyển từ
`WARN` sang `PASS`.

Ngoài ra, tôi cũng sửa lỗi import sai tên hàm (`is_fresh` →
`check_manifest_freshness`) và lỗi escape ký tự `\n` trong quá trình ghi
file CSV.

------------------------------------------------------------------------

## 4. Bằng chứng trước / sau (80--120 từ)

-   **Run ID:** `2026-04-15T09-10Z`

-   **Trước khi fix:**

```{=html}
<!-- -->
```
    freshness_status = WARN
    freshness = 17h (SLA = 4h)

-   **Sau khi fix:**

```{=html}
<!-- -->
```
    freshness_status = PASS
    freshness = 0.5h (SLA = 4h)

-   **Kết quả:**\
    Hệ thống đã phản ánh chính xác độ tươi của dữ liệu. Các cảnh báo sai
    (false positive) được loại bỏ, giúp team tin tưởng hơn vào
    monitoring và giảm thời gian debug không cần thiết.

------------------------------------------------------------------------

## 5. Cải tiến tiếp theo (40--80 từ)

Trong bước tiếp theo, tôi muốn tích hợp hệ thống **alert tự động** thông
qua `alert_channel` (ví dụ Slack) khi freshness vượt SLA hoặc pipeline
bị `HALT`. Ngoài ra, tôi cũng muốn mở rộng tài liệu để bao gồm **data
lineage**, giúp truy vết nguồn gốc dữ liệu và các bước biến đổi một cách
rõ ràng hơn trong toàn pipeline.
