# Báo cáo cá nhân – Monitoring và Docs Owner

## 1. Vai trò và Trách nhiệm
Trong lab này, tớ đã đảm nhiệm vai trò là **Monitoring và Docs Owner**. Các trách nhiệm chính bao gồm:
- Đảm bảo tính tươi mới (freshness) của dữ liệu trong pipeline.
- Phát triển và duy trì các tài liệu kỹ thuật quan trọng như `runbook.md`, `pipeline_architecture.md`, và `data_contract.md`.
- Thiết lập các cơ chế cảnh báo và giám sát pipeline.
- Đảm bảo các artifact được tạo ra và kiểm tra tính nhất quán của chúng.

## 2. Các nhiệm vụ đã hoàn thành
- **Cập nhật `data_contract.yaml`:** Đã cấu hình `owner_team` là "Team A" và `alert_channel` là "slack-alerts".
- **Phát triển `docs/data_contract.md`:** Đã tạo tài liệu chi tiết về hợp đồng dữ liệu, bao gồm nguồn dữ liệu, schema cleaned, quy tắc quarantine/drop và thông tin versioning.
- **Phát triển `docs/pipeline_architecture.md`:** Đã xây dựng tài liệu mô tả kiến trúc tổng thể của pipeline, các thành phần chính, luồng dữ liệu, artifact và hệ thống bên ngoài.
- **Phát triển `docs/runbook.md`:** Đã hoàn thiện tài liệu quy trình ứng phó sự cố, bao gồm các triệu chứng, cách phát hiện, chẩn đoán, các bước giảm thiểu và biện pháp phòng ngừa.
- **Kiểm tra Freshness:** Đã chạy kiểm tra freshness thông qua `etl_pipeline.py freshness`. Mặc dù ban đầu có cảnh báo (`WARN`) do trường `latest_exported_at` chưa được cập nhật đầy đủ, nhưng cơ chế kiểm tra đã hoạt động đúng.
- **Kiểm tra Artifacts:** Đã chạy `instructor_quick_check.py` để xác minh các artifact được tạo ra bởi pipeline.

## 3. Thách thức và Giải pháp
- **Lỗi ImportError/SyntaxError:** Ban đầu gặp phải các lỗi liên quan đến import module (`is_fresh` thay vì `check_manifest_freshness`) và lỗi cú pháp do ký tự xuống dòng (`
`) không được escape đúng cách trong các chuỗi đa dòng. Các lỗi này đã được giải quyết bằng cách:
    - Điều chỉnh tên hàm import từ `is_fresh` sang `check_manifest_freshness`.
    - Sửa lỗi escape ký tự xuống dòng thành `\n` trong các hàm `write_cleaned_csv` và `write_quarantine_csv` của `etl_pipeline.py`.
- **Xác định `project_root`:** Đã điều chỉnh cách xác định thư mục gốc của dự án (`project_root`) để đảm bảo pipeline hoạt động ổn định cả trong môi trường interactive Colab lẫn khi chạy dưới dạng script.

## 4. Các điểm cần cải thiện/Tiếp theo
- **Cải thiện báo cáo Freshness:** Hiện tại, trường `latest_exported_at` trong manifest chưa được cập nhật chính xác với thời gian xuất bản thực tế từ dữ liệu. Cần điều chỉnh logic trong `etl_pipeline.py` để lấy giá trị `max(exported_at)` từ `cleaned_rows` và ghi vào manifest để freshness check có thể hoạt động hiệu quả hơn và cho ra kết quả `PASS`.
- **Mở rộng Alerts:** Cân nhắc tích hợp các cảnh báo tự động thông qua `alert_channel` (ví dụ: Slack) khi có lỗi `HALT` trong quá trình chạy pipeline hoặc khi freshness check thất bại.
- **Kiểm tra thêm về Lineage:** Trong tương lai, có thể mở rộng các tài liệu để bao gồm lineage của dữ liệu, theo dõi nguồn gốc và các phép biến đổi được áp dụng.
- **Tối ưu hóa Performance:** Theo dõi hiệu suất của các bước trong pipeline, đặc biệt là quá trình embedding, để tìm cơ hội tối ưu hóa.

## 5. Tự đánh giá
- **Đóng góp vào vai trò:** Đã hoàn thành tốt các nhiệm vụ cốt lõi của 'Monitoring và Docs Owner', đảm bảo pipeline có tài liệu rõ ràng và cơ chế giám sát cơ bản.
- **Khả năng giải quyết vấn đề:** Đã chủ động debug và khắc phục các lỗi kỹ thuật phát sinh trong quá trình phát triển pipeline.
