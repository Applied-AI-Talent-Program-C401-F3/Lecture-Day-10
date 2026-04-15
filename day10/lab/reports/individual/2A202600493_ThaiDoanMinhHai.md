# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Thái Doãn Minh Hải
**Vai trò:** Cleaning / Transform Owner  
**Ngày nộp:** 2026-04-15  
**Độ dài yêu cầu:** 400–650 từ

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**

- `transform/cleaning_rules.py`: Hiện thực hóa toàn bộ logic làm sạch dữ liệu.
- `data/raw/policy_export_dirty.csv`: Trực tiếp xử lý các lỗi trong file dữ liệu mẫu.

**Kết nối với thành viên khác:**
Tôi nhận dữ liệu thô từ etl_pipeline.py (giai đoạn ingest/export) và chuyển giao cleaned_rows cho quality/validation.py để kiểm định. Kết quả làm sạch của tôi ảnh hưởng trực tiếp đến hiệu quả retrieval của retrieval/vector_store.py.

**Bằng chứng (commit / comment trong code):**

- Hàm clean_rows với các rule mới 7, 8, 9.
- Logic chuẩn hóa effective_date và fix stale_refund_window.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Tôi quyết định bổ sung Rule 9: Future Date Check cho cột exported_at. Trong môi trường thực tế, dữ liệu export không bao giờ có thể đến từ tương lai. Việc đưa các bản ghi này vào quarantine thay vì cố gắng sửa chúng là một quyết định bảo thủ nhưng an toàn, tránh làm sai lệch báo cáo freshness của observability/metrics_logger.py.

Ngoài ra, tôi sử dụng re.sub(r"(?i)it helpdesk", "IT Helpdesk", fixed_text) để đảm bảo việc chuẩn hóa casing không bị ảnh hưởng bởi cách viết hoa/thường ban đầu của nhân viên nhập liệu. Việc thêm marker [cleaned: ...] vào cuối text giúp retrieval/query_engine.py dễ dàng nhận diện những đoạn text đã bị can thiệp khi debug kết quả retrieval, tăng tính minh bạch cho toàn bộ pipeline.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Tôi gặp vấn đề với các dấu câu dư thừa ở cuối chunk text (ví dụ: "...", ",,,", hoặc kết thúc bằng dấu phẩy). Những ký tự này làm ảnh hưởng đến việc tính toán hash cho chunk_id và đôi khi làm bộ lọc trùng lặp (duplicate_chunk_text) trong transform/deduplication.py bỏ sót các nội dung thực sự giống nhau.

Triệu chứng: cleaned_records cao hơn dự kiến do các chunk giống nội dung nhưng khác dấu câu cuối cùng được coi là khác nhau.

Xử lý: Tôi triển khai Rule 8: Punctuation Cleanup để strip các ký tự .,;: ở cuối text. Kết quả là số lượng bản ghi trùng lặp bị phát hiện tăng lên, dữ liệu cleaned trở nên gọn gàng hơn và chunk_id trở nên ổn định (stable) hơn.

---

## 4. Bằng chứng trước / sau (80–120 từ)

- **Run ID:** `2026-04-15T07-26Z`
- **Dòng CSV quarantine thực tế (artifacts/quarantine/):**
  `doc_id,reason`
  `legacy_catalog_xyz_zzz,unknown_doc_id`
  `hr_leave_policy,stale_hr_policy_effective_date`
  `policy_refund_v4,missing_chunk_text`
- **Metric Impact:**
  - `raw_records=10` -> `cleaned_records=6`.
  - `quarantine_records=4` (do dính rule doc_id lạ và HR version cũ).

---

## 5. Cải tiến tiếp theo (40–80 từ)

Tôi muốn áp dụng thư viện `unidecode` để loại bỏ dấu tiếng Việt hoặc chuẩn hóa Unicode dựng sẵn/tổ hợp. Điều này cực kỳ quan trọng vì dữ liệu từ các nguồn khác nhau thường bị lỗi font hoặc sai bảng mã, gây khó khăn cho việc search và dedupe.
