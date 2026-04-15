# Báo Cáo Nhóm — Lab Day 10: Data Pipeline & Data Observability

**Tên nhóm:** C401-F3 
**Thành viên:**
| Tên | Vai trò (Day 10) | Nhiệm vụ chính |
|-----|------------------|----------------|
| Lưu Lê Gia Bảo | Ingestion / Raw Owner | CLI, Logging, Manifest structure |
| Thái Doãn Minh Hải | Cleaning Owner | transform/cleaning_rules.py (3 rules) |
| Hoàng Quốc Hùng | Quality Owner | quality/expectations.py (2 rules, Halt/Warn) |
| Khương Hải Lâm | Embed & Idempotency | ChromaDB Upsert, Pruning logic |
| Đặng Tuấn Anh | Eval & Quality Report | eval_retrieval.py, Quality Report, Sprint 3 Injection |
| Lương Trung Kiên| Monitoring & Docs | 2-boundary freshness, Runbook, Architecture |

**Ngày nộp:** 2026-04-15  
**Repo:** https://github.com/Applied-AI-Talent-Program-C401-F3/Lecture-Day-10.git
**Độ dài khuyến nghị:** 600–1000 từ

---

## 1. Pipeline tổng quan (150–200 từ)

Nguồn dữ liệu raw của nhóm là `data/raw/policy_export_dirty.csv`, một file CSV mô phỏng dữ liệu xuất từ database nguồn chứa nhiều lỗi về format, duplicate và stale version. Chuỗi lệnh chạy end-to-end của nhóm là:
`python etl_pipeline.py run --run-id 2026-04-15T07-26Z`

`run_id` được sinh tự động dựa trên UTC timestamp và được ghi lại trong tất cả các log file, manifest, và metadata của vector store để đảm bảo tính lineage (truy vết).

**Lệnh chạy một dòng:**
`python etl_pipeline.py run`

---

## 2. Cleaning & expectation (150–200 từ)

### 2a. Bảng metric_impact (bắt buộc — chống trivial)

| Rule / Expectation mới | Trước (số liệu) | Sau / khi inject (số liệu) | Chứng cứ |
|-------------------------|------------------|-----------------------------|----------|
| **Raw Records** | 10 | 10 | `run.log` |
| **Cleaned Records** | 0 | 6 | `run.log` |
| **Quarantine Records** | 0 | 4 | `quarantine_*.csv` |
| Rule: Refund Window Fix | 14-day policy | 7-day policy | `cleaned_*.csv` |
| Rule: HR Version Filter | 10-day leave | 12-day leave | `cleaned_*.csv` |
| E: Min Doc Coverage | 0 docs | PASS (distinct_docs=4) | `run.log` |
| E: Refund No Stale | 1 violation | PASS (violations=0) | `run.log` |

---

## 3. Before / after ảnh hưởng retrieval hoặc agent (200–250 từ)

**Kịch bản inject (Sprint 3):**
Chúng tôi đã mô phỏng việc "bỏ quên" quy tắc làm sạch dữ liệu bằng cách sử dụng flag `--no-refund-fix`. Trong kịch bản này, dữ liệu lỗi chứa chính sách hoàn tiền 14 ngày (stale) thay vì 7 ngày (current) được đẩy vào ChromaDB.

**Kết quả định lượng (từ grading_run.jsonl):**
- **Trước khi Clean (Inject Bad):** Câu hỏi `gq_d10_01` về thời gian hoàn tiền cho kết quả `hits_forbidden: true`. Điều này có nghĩa là RAG agent tìm thấy thông tin "14 ngày" và có nguy cơ trả lời sai cho khách hàng.
- **Sau khi Clean (Standard Run):** Kết quả đạt `contains_expected: true` và `hits_forbidden: false`. Chênh lệch này chứng minh pipeline đã loại bỏ thành công nhiễu (noise) từ dữ liệu cũ, giúp Agent chỉ tiếp cận được nguồn thông tin "v4" chuẩn xác (7 ngày).
- **Versioning:** Hệ thống cũng chứng minh khả năng ưu tiên `top1_doc_id` cho các tài liệu HR 2026 so với bản cũ, đảm bảo tính nhất quán về thời gian hiệu lực.

---

## 4. Freshness & monitoring (100–150 từ)

Nhóm thiết lập SLA freshness là **168 giờ (7 ngày)** để phù hợp với chu kỳ cập nhật chính sách của doanh nghiệp. 
- **Kết quả Audit:** Manifest ghi nhận ranh giới `source_to_ingest` là 119-121 giờ. 
- **Ý nghĩa:** Mặc dù pipeline chạy hàng ngày (`ingest_to_publish` < 1 giờ), nhưng dữ liệu nguồn từ HR/Admin đã 5 ngày chưa có bản export mới. Với SLA 168h, hệ thống báo **PASS**. Nếu dùng SLA 24h mặc định, hệ thống sẽ báo **FAIL**, cảnh báo cho admin rằng nguồn cấp dữ liệu đang bị "đóng băng" (stale source).

---

## 5. Liên hệ Day 09 (50–100 từ)

Dữ liệu sau khi embed bởi pipeline này được lưu trữ trong collection `day10_kb`. Khác với Day 09 chỉ đọc các file tĩnh (txt), pipeline Day 10 cho phép multi-agent truy cập vào kho tri thức "sống" được cập nhật liên tục từ CSV/DB. Điều này giải quyết bài toán "Hallucination by stale data" (Ảo giác do dữ liệu cũ) mà các agent Day 09 thường gặp phải khi chính sách thay đổi nhưng file text chưa được sửa thủ công.

---

## 6. Rủi ro còn lại & việc chưa làm

- **Deduplication nâng cao:** Hiện tại pipeline chỉ dedupe dựa trên `chunk_text` thô, chưa xử lý được các trường hợp hai đoạn văn cùng ý nghĩa nhưng khác câu chữ (Semantic Deduplication).
- **Auto-Alert:** Hệ thống monitoring mới dừng lại ở việc xuất file JSON, chưa tích hợp gửi thông báo chủ động (Webhook) khi `freshness_check` trả về FAIL.
- **Rollback:** Chưa có cơ chế tự động quay lại (rollback) phiên bản vector store trước đó nếu bản cập nhật mới nhất bị lỗi chất lượng nghiêm trọng.
