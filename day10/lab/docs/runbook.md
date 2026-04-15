# Runbook — Lab Day 10 (Incident Vận Hành)

Tài liệu hướng dẫn xử lý sự cố cho Data Pipeline & RAG Ingestion.

---

## 1. Sự cố: Freshness SLA FAIL (Boundary 1 hoặc 2)

- **Symptom:** Log pipeline báo `freshness_check=FAIL`. User thấy thông tin AI trả về bị cũ.
- **Detection:** Metric `source_to_ingest` hoặc `ingest_to_publish` trong manifest vượt quá `FRESHNESS_SLA_HOURS`.
- **Diagnosis:**
    1. Kiểm tra `artifacts/manifests/*.json` để xem `latest_exported_at`.
    2. Nếu `source_to_ingest` FAIL: Lỗi do hệ thống nguồn (Upstream) chậm export.
    3. Nếu `ingest_to_publish` FAIL: Lỗi do pipeline ETL bị treo hoặc không được trigger đúng lịch.
- **Mitigation:**
    - Liên hệ Upstream team để trigger export lại.
    - Rerun `python etl_pipeline.py run` thủ công.
- **Prevention:** Thiết lập cảnh báo (alert) Slack/Email khi manifest không được cập nhật quá 12 giờ.

---

## 2. Sự cố: Pipeline Halt (Expectation Failure)

- **Symptom:** Ingestion bị dừng, dữ liệu mới không được đẩy vào ChromaDB.
- **Detection:** Log ghi `PIPELINE_HALT: expectation suite failed (halt)`.
- **Diagnosis:** 
    - Kiểm tra `expectation[min_doc_coverage_3] FAIL` hoặc `expectation[refund_no_stale_14d_window] FAIL`.
    - Mở `artifacts/quarantine/*.csv` để tìm `reason`.
- **Mitigation:**
    - Fix dữ liệu raw nếu lỗi do nhập liệu.
    - Cập nhật `transform/cleaning_rules.py` nếu logic clean quá chặt hoặc sai sót.
    - Dùng `--skip-validate` (chỉ khi khẩn cấp và đã hiểu rủi ro).
- **Prevention:** Thêm Unit Test cho `cleaning_rules.py` để đảm bảo logic transform ổn định.

---

## 3. Sự cố: Retrieval Trả Về Dữ Liệu Cũ (Ghosting Data)

- **Symptom:** Agent trả về "14 ngày hoàn tiền" dù pipeline đã báo "cleaned".
- **Detection:** Chạy `python eval_retrieval.py` thấy `hits_forbidden=True`.
- **Diagnosis:** 
    - Kiểm tra `embed_prune_removed` trong log. Nếu bằng 0 khi vừa xóa data, logic pruning bị lỗi.
    - Kiểm tra `collection.count()` trong ChromaDB.
- **Mitigation:** Xóa collection Chroma và chạy `run` lại từ đầu (Full Re-indexing).
- **Prevention:** Đảm bảo sử dụng `col.upsert()` với Stable ID (hash-based) để tránh trùng lặp.
