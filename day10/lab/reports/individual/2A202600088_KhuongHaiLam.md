# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Khương Hải Lâm 
**Vai trò:** Embed / Idempotency Owner  
**Ngày nộp:** 2026-04-15  
**Độ dài yêu cầu:** 400–650 từ

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**
- `etl_pipeline.py` (hàm `cmd_embed_internal`): Xử lý việc đẩy dữ liệu vào ChromaDB.
- `requirements.txt`: Quản lý các dependency liên quan đến SentenceTransformers và ChromaDB.
- `runbook.md`

**Kết nối với thành viên khác:**
Tôi nhận file CSV đã qua kiểm định từ Hoàng Quốc Hùng, và tôi đảm bảo rằng kết quả làm sạch của Thái Doãn Minh Hải được phản ánh chính xác trong Vector Store để Đặng Tuấn Anh thực hiện đánh giá retrieval.

**Bằng chứng (commit / comment trong code):**
- Sử dụng `col.upsert` thay vì `col.add` để đảm bảo idempotency.
- Logic `embed_prune_removed` để xóa các vector cũ không còn trong cleaned CSV.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Quyết định kỹ thuật quan trọng nhất của tôi là thực hiện **Pruning (dọn dẹp)** vector store sau mỗi lần chạy. Trong RAG, nếu một tài liệu cũ bị xóa khỏi hệ thống nguồn nhưng vẫn tồn tại trong Vector DB, mô hình AI sẽ tiếp tục truy xuất thông tin lỗi thời đó. 

Tôi đã cài đặt logic: lấy toàn bộ `ids` hiện có trong collection, so sánh với `ids` của run hiện tại, và xóa những ID thừa. Điều này biến Vector Store thành một "snapshot" chính xác của dữ liệu đã được publish. Mặc dù việc này tốn thêm một lượt truy vấn (`col.get`), nhưng nó giải quyết triệt để vấn đề "ma mị" (ghosting data) trong hệ thống AI, đảm bảo tính nhất quán (consistency) giữa Data Lake và Vector Database.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Khi chạy pipeline nhiều lần với cùng một bộ dữ liệu, tôi nhận thấy số lượng vector trong ChromaDB tăng lên gấp đôi, gấp ba mặc dù nội dung không thay đổi.

**Triệu chứng:** `col.count()` tăng liên tục sau mỗi lần `python etl_pipeline.py run`.
**Xử lý:** Tôi phát hiện ra việc sử dụng `chunk_id` ngẫu nhiên hoặc không ổn định là nguyên nhân. Tôi đã phối hợp với Student B để chuyển sang sử dụng `_stable_chunk_id` (tính toán dựa trên hash của nội dung và doc_id). Sau đó, trong code embed, tôi chuyển từ hàm `.add()` sang `.upsert()`. Nhờ vậy, ChromaDB sẽ tự động cập nhật bản ghi cũ nếu trùng ID thay vì tạo bản ghi mới, giúp tiết kiệm bộ nhớ và giữ cho kết quả tìm kiếm không bị nhiễu bởi các bản sao.

---

## 4. Bằng chứng trước / sau (80–120 từ)

- **Run ID:** `2026-04-15T07-26Z`
- **Log Embed (Thành công):**
```
embed_upsert count=6 collection=day10_kb
```
- **Kết quả:** Pipeline đã đẩy thành công 6 bản ghi (sau khi loại bỏ 4 bản ghi lỗi) vào collection `day10_kb`. Sử dụng `model: all-MiniLM-L6-v2` đảm bảo tốc độ embed nhanh ngay cả trên CPU.

---

## 5. Cải tiến tiếp theo (40–80 từ)

Tôi muốn triển khai cơ chế **Collection Versioning**. Thay vì ghi đè lên collection `day10_kb`, tôi sẽ tạo các collection theo `run_id` và chỉ tráo đổi (swap) alias sau khi embedding hoàn tất thành công. Điều này giúp hệ thống online không bao giờ bị gián đoạn hoặc gặp dữ liệu "nửa vời" khi pipeline đang chạy.
