# Báo cáo So sánh Hiệu năng & Ước tính Chi phí: ReACT vs Reflexion Agent (Golden Dataset)

Báo cáo này cung cấp đánh giá chi tiết và so sánh định lượng giữa hai kiến trúc agent: **ReACT (Reasoning + Acting)** và **Reflexion (Self-Reflection)** dựa trên kết quả chạy thực nghiệm thực tế với 20 câu hỏi cho mỗi agent từ bộ dữ liệu **`hotpot_golden.json`** (tổng cộng 40 lượt đánh giá) sử dụng mô hình ngôn ngữ lớn **Qwen/Qwen2.5-7B-Instruct**.

---

## 1. Thông tin Cấu hình & Siêu dữ liệu (Metadata)

- **Bộ dữ liệu nguồn:** [hotpot_golden.json](file:///D:/user/Desktop/Github/phase1-track3-lab1-advanced-agent-Vinh/data/hotpot_golden.json)
- **Số lượng mẫu chạy:** 20 mẫu cho mỗi Agent
- **Mô hình LLM:** `Qwen/Qwen2.5-7B-Instruct`
- **Địa chỉ API Endpoint:** `https://swore-explode-thievish.ngrok-free.dev/v1`
- **Các Extensions đã triển khai:**
  - `structured_evaluator`
  - `reflection_memory`
  - `benchmark_report_json`
  - `mock_mode_for_autograding`

---

## 2. Bảng So sánh Hiệu năng Tổng quan (Golden Dataset)

Dưới đây là bảng thống kê chi tiết các chỉ số hiệu năng đo được từ thực tế chạy 20 câu hỏi trên mỗi agent:

| Chỉ số (Metric) | ReAct Agent | Reflexion Agent | Chênh lệch (Delta) | Tỷ lệ thay đổi (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Tỷ lệ đúng (Exact Match - EM)** | **0.8000** (16/20) | **0.9000** (18/20) | **+0.1000** | **+12.50%** |
| **Số lần thử trung bình (Avg Attempts)** | 1.0000 | 1.3000 | +0.3000 | +30.00% |
| **Tổng số lần gọi LLM (Total LLM Calls)** | 20 | 26 | +6 | +30.00% |
| **Số token trung bình / câu hỏi** | 840.45 | 1,344.65 | +504.20 | +59.99% |
| **Tổng số token tiêu thụ (20 câu)** | 16,809 | 26,893 | +10,084 | +59.99% |
| **Thời gian chạy trung bình / câu hỏi** | 10.63s (10,627.10 ms) | 14.37s (14,370.50 ms) | +3.74s | +35.22% |
| **Tổng thời gian chạy (Running Time)** | **3m 32s** (212.54s) | **4m 47s** (287.41s) | **+1m 15s** | +35.22% |

> [!NOTE]
> **Tỷ lệ sửa lỗi thành công (Recovery Rate):** Reflexion đã sửa thành công **2 câu hỏi** trong số **4 câu hỏi** mà ReACT làm sai ban đầu, đạt tỷ lệ khôi phục thành công là **50.00%** (2/4).
> So với bộ dữ liệu chính `hotpot_100.json`, tập dữ liệu Golden này có độ phức tạp trung bình thấp hơn (token trung bình ít hơn và số lần thử trung bình của Reflexion giảm từ 2.14 xuống 1.30), giúp việc tự phản chiếu hội tụ nhanh hơn.

---

## 3. Bảng Ước tính Chi phí & Thời gian Chạy (Cost & Running Time Estimation)

Ước tính chi phí được xây dựng dưới hai kịch bản:
1. **Kịch bản A (Cloud API):** Giá trung bình $0.06 / 1 triệu tokens.
2. **Kịch bản B (Self-hosted GPU):** Vận hành trên máy trạm GPU vẽ dòng ~400W, đơn giá điện 3,500 VND / kWh (~$0.14/kWh).

### A. Chi phí cho đợt thử nghiệm thực tế (20 câu hỏi mỗi Agent)

| Tiêu chí | ReAct Agent | Reflexion Agent | Chênh lệch (Delta) | Tỷ lệ tăng |
| :--- | :---: | :---: | :---: | :---: |
| **Thời gian chạy thực tế** | 3.54 phút | 4.79 phút | +1.25 phút | 1.35 lần |
| **Tổng số Token thực tế** | 16,809 tokens | 26,893 tokens | +10,084 tokens | 1.60 lần |
| **Chi phí Cloud API ($)** | $0.0010 | $0.0016 | +$0.0006 | 1.60 lần |
| **Điện năng tiêu thụ (Self-hosted)**| 0.0236 kWh | 0.0319 kWh | +0.0083 kWh | 1.35 lần |
| **Chi phí tiền điện thực tế (VND)** | **83 VND** | **112 VND** | **+29 VND** | 1.35 lần |

### B. Ước tính khi mở rộng quy mô (Extrapolation cho 10,000 câu hỏi)

| Tiêu chí | ReAct Agent | Reflexion Agent | Chênh lệch (Delta) |
| :--- | :---: | :---: | :---: |
| **Tổng thời gian chạy dự kiến** | **29.52 giờ** | **39.92 giờ** | **+10.40 giờ** |
| **Tổng số Token dự kiến** | 8,404,500 tokens | 13,446,500 tokens | +5,042,000 tokens |
| **Chi phí Cloud API ước tính ($)** | **$0.50** | **$0.81** | **+$0.31** |
| **Điện năng tiêu thụ ước tính** | 11.81 kWh | 15.97 kWh | +4.16 kWh |
| **Chi phí tiền điện ước tính (VND)** | **41,328 VND** (~$1.65) | **55,888 VND** (~$2.24) | **+14,560 VND** (~$0.58) |

---

## 4. Phân tích Chi tiết Lỗi (Failure Modes Analysis)

### Thống kê phân phối lỗi

| Phân loại lỗi | ReAct Agent | Reflexion Agent | Xu hướng thay đổi |
| :--- | :---: | :---: | :--- |
| **Không có lỗi (none / Correct)** | 16 (80.0%) | 18 (90.0%) | Tăng (+10% tuyệt đối) |
| **Câu trả lời cuối cùng sai (wrong_final_answer)** | 4 (20.0%) | 2 (10.0%) | Giảm (-10% tuyệt đối) |

### Phân tích nguyên nhân lỗi còn tồn đọng trên bộ Golden

Mặc dù độ chính xác của Reflexion đạt mức rất cao là **90%**, vẫn còn **2 lỗi** `wrong_final_answer` xuất hiện:
1. **QID: gold7 (Frank Darabont - Academy Awards):**
   - ReAct trả lời sai vì Frank Darabont nhận nhiều đề cử Oscar nhưng chưa từng thắng giải nào (đáp án đúng là "no Academy Award win"). Ở lượt đầu tiên, ReAct kết luận sai.
   - Khi chuyển sang Reflexion, dù qua 3 lượt thử, Agent vẫn không phân tích chính xác mối quan hệ giữa "đề cử" và "thắng giải" để đưa ra đúng cụm từ khoá "no Academy Award win" do sự nhạy cảm trong cách so khớp Exact Match (EM) của đáp án.
2. **QID: gold17 (Rãnh đại dương ở phía đông Nhật Bản):**
   - Đáp án đúng là "Challenger Deep" (nằm ở phía nam/đông nam trong vùng mảng kiến tạo Thái Bình Dương giáp Nhật). ReAct bị nhầm sang rãnh Nhật Bản (Japan Trench) hoặc không đưa ra độ sâu/tên gọi chính xác.
   - Reflexion đã cố gắng sửa sai ở các lượt sau, nhưng do sự mơ hồ trong context địa lý được cung cấp nên phản chiếu vẫn kết luận sai về mặt tên địa danh rãnh đại dương.

---

## 5. Kết luận (Discussion & Trade-offs)

Trên bộ dữ liệu Golden:
- **Ưu điểm lớn:** Sự đánh đổi của Reflexion trên bộ Golden là cực kỳ tối ưu. EM tăng từ 80% lên 90% (+12.5%) chỉ với sự gia tăng nhẹ về token (+60%) và độ trễ (+35%). Sự chênh lệch này thấp hơn rất nhiều so với bộ `hotpot_100.json` (tăng gần gấp 3 lần về cả token lẫn latency).
- **Kết luận:** Bộ Golden có độ hội tụ phản chiếu rất nhanh. Điều này cho thấy chất lượng prompt và evaluator hoạt động đặc biệt hiệu quả khi các câu hỏi có cấu trúc multi-hop rõ ràng và ngắn gọn.
