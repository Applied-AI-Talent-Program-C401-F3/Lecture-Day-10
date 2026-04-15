# Kiến trúc pipeline — Lab Day 10

**Nhóm:** C401-F3
**Cập nhật:** 2026-04-15

---

## 1. Sơ đồ luồng (bắt buộc có 1 diagram: Mermaid / ASCII)

```text
[ Raw Export (CSV) ] 
       │
       ▼
[ Ingest ] ───▶ ( Log: raw_count, run_id )
       │
       ▼
[ Transform ] ─┬─▶ [ Cleaned CSV ] ───▶ ( Artifact: cleaned/ )
       │       └─▶ [ Quarantine CSV ] ─▶ ( Artifact: quarantine/ )
       │
       ▼
[ Quality (Expectations) ] ──▶ ( HALT if Fail / Warn in logs )
       │
       ▼
[ Embed (ChromaDB) ] ───▶ ( Upsert chunk_id + Prune old )
       │
       ▼
[ Monitoring (Freshness) ] ──▶ [ Manifest JSON ] ──▶ ( Status: PASS/FAIL )
```

> **Ghi chú:** Điểm đo **freshness** nằm ở bước cuối cùng sau khi sinh ra **Manifest JSON**, so sánh `run_timestamp` và `latest_exported_at` với mốc thời gian hiện tại.

---

## 2. Ranh giới trách nhiệm

| Thành phần | Input | Output | Owner nhóm |
|------------|-------|--------|--------------|
| Ingest | `data/raw/*.csv` | In-memory Rows | Ingestion Owner |
| Transform | In-memory Rows | Cleaned / Quarantine CSV | Cleaning Owner |
| Quality | Cleaned Rows | Validation Results | Quality Owner |
| Embed | Cleaned CSV | ChromaDB Collection | Embed Owner |
| Monitor | Manifest JSON | Freshness Report (SLA) | Student D (Monitoring) |

---

## 3. Idempotency & rerun

- **Chiến lược:** Sử dụng `col.upsert` trong ChromaDB dựa trên `chunk_id`. 
- **Rerun:** Nếu chạy lại cùng một file 2 lần với cùng `chunk_id`, dữ liệu cũ sẽ bị ghi đè thay vì tạo bản sao (No duplicate vectors).
- **Pruning:** Pipeline tự động xóa các `id` cũ không còn xuất hiện trong lần chạy (run) hiện tại để đảm bảo Vector Store luôn khớp với bản snapshot mới nhất.

---

## 4. Liên hệ Day 09

- Pipeline này đóng vai trò "hệ quản trị tri thức" (Knowledge Base Management). 
- Thay vì RAG đọc trực tiếp từ `data/docs/` (tĩnh), nó sẽ đọc từ **ChromaDB** đã được pipeline này cập nhật và làm sạch từ các nguồn xuất (export) động của doanh nghiệp.

---

## 5. Rủi ro đã biết

- **Stale Data:** Nếu nguồn CSV không được HR/Admin export mới, pipeline sẽ báo `FAIL` ở bước `source_to_ingest` dù code chạy tốt.
- **Halt Pipeline:** Nếu các quy tắc Quality (Expectations) quan trọng bị vi phạm, pipeline sẽ dừng lại (Halt) để ngăn chặn dữ liệu sai lệch đi vào Vector Store.
