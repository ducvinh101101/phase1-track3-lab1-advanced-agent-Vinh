# Báo cáo So sánh Hiệu năng & Ước tính Chi phí: ReACT vs Reflexion Agent

Báo cáo này cung cấp cái nhìn chi tiết và so sánh định lượng giữa hai kiến trúc agent: **ReACT (Reasoning + Acting)** và **Reflexion (Self-Reflection)** dựa trên kết quả chạy thử nghiệm thực tế với 50 câu hỏi cho mỗi agent từ bộ dữ liệu `hotpot_100.json` (tổng cộng 100 lượt đánh giá) sử dụng mô hình ngôn ngữ lớn **Qwen/Qwen2.5-7B-Instruct**.

---

## 1. Thông tin Cấu hình & Siêu dữ liệu (Metadata)

- **Bộ dữ liệu nguồn:** [hotpot_100.json](file:///D:/user/Desktop/Github/phase1-track3-lab1-advanced-agent-Vinh/data/hotpot_100.json)
- **Số lượng mẫu chạy:** 50 mẫu cho mỗi Agent
- **Mô hình LLM:** `Qwen/Qwen2.5-7B-Instruct`
- **Địa chỉ API Endpoint:** `https://swore-explode-thievish.ngrok-free.dev/v1`
- **Các Extensions đã triển khai:**
  - `structured_evaluator` (Đánh giá cấu trúc kết quả)
  - `reflection_memory` (Lưu trữ lịch sử phản chiếu lỗi)
  - `benchmark_report_json` (Tự động xuất báo cáo định dạng JSON)
  - `mock_mode_for_autograding` (Chế độ giả lập phục vụ tự động chấm điểm)

---

## 2. Bảng So sánh Hiệu năng Tổng quan

Dưới đây là bảng thống kê chi tiết các chỉ số hiệu năng đo được từ thực tế chạy 50 câu hỏi trên mỗi agent:

| Chỉ số (Metric) | ReAct Agent | Reflexion Agent | Chênh lệch (Delta) | Tỷ lệ thay đổi (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Tỷ lệ đúng (Exact Match - EM)** | **0.3800** (19/50) | **0.6000** (30/50) | **+0.2200** | **+57.89%** |
| **Số lần thử trung bình (Avg Attempts)** | 1.0000 | 2.1400 | +1.1400 | +114.00% |
| **Tổng số lần gọi LLM (Total LLM Calls)** | 50 | 107 | +57 | +114.00% |
| **Số token trung bình / câu hỏi** | 1,274.80 | 3,690.32 | +2,415.52 | +189.48% |
| **Tổng số token tiêu thụ (50 câu)** | 63,740 | 184,516 | +120,776 | +189.48% |
| **Thời gian chạy trung bình / câu hỏi** | 12.15s (12,150.58 ms) | 35.55s (35,549.82 ms) | +23.40s | +192.58% |
| **Tổng thời gian chạy (Running Time)** | **10m 7s** (607.53s) | **29m 37s** (1,777.49s) | **+19m 30s** | +192.58% |

> [!NOTE]
> **Tỷ lệ sửa lỗi thành công (Recovery Rate):** Reflexion đã cứu được **11 câu hỏi** trong số **31 câu hỏi** mà ReACT đã làm sai ở lượt thử đầu tiên, tương đương với tỷ lệ khôi phục thành công là **35.48%** (11/31). Điều này chứng minh cơ chế Self-Reflection hoạt động hiệu quả trên các tác vụ suy luận phức tạp.

---

## 3. Bảng Ước tính Chi phí & Thời gian Chạy (Cost & Running Time Estimation)

Để có cái nhìn thực tế về chi phí triển khai trong sản xuất, chúng tôi xây dựng ước tính chi phí dưới hai kịch bản:
1. **Kịch bản A (Cloud API):** Sử dụng các bên cung cấp API bên thứ ba (như Together AI, OpenRouter) với mức giá trung bình cho dòng mô hình Qwen 2.5 7B là **$0.06 / 1 triệu tokens** (áp dụng đồng giá cho cả Input và Output).
2. **Kịch bản B (Self-hosted GPU):** Tự vận hành mô hình trên phần cứng cá nhân (ví dụ: RTX 3090 hoặc RTX 4090). Công suất tiêu thụ trung bình của hệ thống là **400W (0.4 kW)** và đơn giá điện sinh hoạt/kinh doanh tạm tính là **3,500 VND / kWh (~$0.14/kWh)**.

### A. Chi phí cho đợt thử nghiệm thực tế (50 câu hỏi mỗi Agent)

| Tiêu chí | ReAct Agent | Reflexion Agent | Chênh lệch (Delta) | Tỷ lệ tăng |
| :--- | :---: | :---: | :---: | :---: |
| **Thời gian chạy thực tế** | 10.13 phút | 29.62 phút | +19.49 phút | 2.92 lần |
| **Tổng số Token thực tế** | 63,740 tokens | 184,516 tokens | +120,776 tokens | 2.89 lần |
| **Chi phí Cloud API ($)** | $0.0038 | $0.0111 | +$0.0073 | 2.89 lần |
| **Điện năng tiêu thụ (Self-hosted)**| 0.0675 kWh | 0.1975 kWh | +0.1300 kWh | 2.92 lần |
| **Chi phí tiền điện thực tế (VND)** | **236 VND** | **691 VND** | **+455 VND** | 2.92 lần |

### B. Ước tính khi mở rộng quy mô (Extrapolation cho 10,000 câu hỏi)

Khi triển khai trên quy mô lớn 10,000 câu hỏi (ví dụ: chạy trên toàn bộ tập dữ liệu HotpotQA đầy đủ), các chỉ số được dự báo như sau:

| Tiêu chí | ReAct Agent | Reflexion Agent | Chênh lệch (Delta) |
| :--- | :---: | :---: | :---: |
| **Tổng thời gian chạy dự kiến** | **33.75 giờ** (1.4 ngày) | **98.75 giờ** (4.1 ngày) | **+65 giờ** (2.7 ngày) |
| **Tổng số Token dự kiến** | 12,748,000 tokens | 36,903,200 tokens | +24,155,200 tokens |
| **Chi phí Cloud API ước tính ($)** | **$0.76** | **$2.21** | **+$1.45** |
| **Điện năng tiêu thụ ước tính** | 13.50 kWh | 39.50 kWh | +26.00 kWh |
| **Chi phí tiền điện ước tính (VND)** | **47,250 VND** (~$1.89) | **138,250 VND** (~$5.53) | **+91,000 VND** (~$3.64) |

---

## 4. Phân tích Chi tiết Lỗi (Failure Modes Analysis)

### Thống kê phân phối lỗi

| Phân loại lỗi | ReAct Agent | Reflexion Agent | Xu hướng thay đổi |
| :--- | :---: | :---: | :--- |
| **Không có lỗi (none / Correct)** | 19 (38.0%) | 30 (60.0%) | Tăng đáng kể (+22% tuyệt đối) |
| **Câu trả lời cuối cùng sai (wrong_final_answer)** | 31 (62.0%) | 20 (40.0%) | Giảm mạnh (-22% tuyệt đối) |

### Phân tích nguyên nhân & cơ chế hoạt động

1. **Tại sao Reflexion giúp cải thiện độ chính xác?**
   - **Khắc phục lỗi trôi dạt thực thể (Entity Drift):** Ở các câu hỏi multi-hop, ReAct thường bị nhầm lẫn thực thể ở hop thứ 2 khi không tìm thấy thông tin phù hợp ở hop 1. Khi Evaluator chấm điểm sai, Reflector phân tích lý do và tạo ra bộ nhớ phản chiếu (`reflection_memory`), lưu ý Actor tránh tìm kiếm sai hướng hoặc chỉ ra thực thể chính xác cần truy vấn lại.
   - **Bổ sung thông tin thiếu hụt:** Trong các trường hợp ReAct kết luận quá sớm ("không đủ thông tin"), Reflector sẽ yêu cầu Actor tìm kiếm sâu hơn hoặc thay đổi từ khóa truy vấn trong các lượt thử tiếp theo.

2. **Tại sao vẫn còn 40% (20 câu) bị lỗi `wrong_final_answer` ở Reflexion?**
   - **Giới hạn của Reflector:** Nếu mô hình Reflector không chỉ ra được nguyên nhân cốt lõi tại sao câu trả lời trước đó sai hoặc đề xuất chiến thuật mơ hồ, Actor sẽ lặp lại lỗi cũ trong các lượt thử sau.
   - **Ngưỡng số lần thử tối đa (Max Attempts = 3):** Một số câu hỏi cực kỳ phức tạp yêu cầu nhiều hơn 3 lượt suy luận để sửa đổi thông tin. Agent bị buộc dừng lại khi chạm giới hạn này.
   - **Hạn chế của tài liệu ngữ cảnh (Context Constraints):** Nếu thông tin chính xác không hề tồn tại trong context được cung cấp, dù phản chiếu bao nhiêu lần thì Agent vẫn không thể đưa ra đáp án đúng.

---

## 5. Kết luận & Đề xuất Tối ưu hóa (Discussion & Trade-offs)

### Đánh giá Trade-off (Đổi chác)

Cơ chế **Reflexion** mang lại sự cải thiện vượt trội về chất lượng câu trả lời (EM tăng **57.89%**), tuy nhiên đổi lại là chi phí vận hành rất cao:
- **Tốn tài nguyên hơn:** Số lượng Token tiêu thụ tăng **189.48%** do phải truyền lại toàn bộ lịch sử hội thoại kèm theo bộ nhớ phản chiếu.
- **Tăng độ trễ (Latency):** Thời gian phản hồi tăng **192.58%**, khiến Reflexion không phù hợp cho các ứng dụng yêu cầu phản hồi thời gian thực (Real-time chatbot) mà phù hợp hơn cho các tác vụ phân tích ngoại tuyến (Offline batch processing), giải toán hoặc nghiên cứu khoa học.

### Đề xuất tối ưu hóa hệ thống

Để giảm bớt các nhược điểm về chi phí và thời gian của Reflexion, chúng ta có thể áp dụng các cải tiến sau:
1. **Dynamic Max Attempts (Số lần thử động):** Chỉ kích hoạt lượt thử tiếp theo nếu điểm số của Evaluator ở mức trung bình (ví dụ: cần chỉnh sửa nhỏ), thay vì luôn cố gắng chạy tối đa 3 lần cho những câu hoàn toàn sai hoặc context thiếu thông tin.
2. **Memory Compression (Nén bộ nhớ phản chiếu):** Rút gọn nội dung phản chiếu của các lượt trước, chỉ giữ lại các từ khóa thực thể quan trọng thay vì lưu toàn bộ đoạn văn bản suy luận dài dòng để giảm số lượng Input Token.
3. **Sử dụng mô hình nhỏ hơn làm Evaluator/Reflector:** Dùng mô hình lớn (như GPT-4 hoặc Qwen 72B) làm Actor để suy luận tốt nhất, nhưng dùng mô hình nhỏ, nhanh và rẻ hơn (như Qwen 1.5B/7B hoặc GPT-4o-mini) làm Evaluator và Reflector để tối ưu hóa thời gian và chi phí.
