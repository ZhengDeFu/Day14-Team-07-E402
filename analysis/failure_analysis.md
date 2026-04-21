# 🔍 Failure Analysis Report

## 📊 Tổng quan Benchmark Results

| Metric | Value |
|--------|-------|
| Total Test Cases | 10 |
| Pass Rate | 90% (9/10) |
| Judge Score (avg) | 4.14/5.0 |
| Hit Rate | 90% |
| MRR | 0.63 |
| Agreement Rate | 85% |
| Estimated Cost | $0.0143 |
| Avg Latency | 2.16s |

---

## ❌ Failed Test Cases

### Case 1: "Tần suất bảo dưỡng VF8 là bao lâu?"

**Expected Answer**: Nên bảo dưỡng mỗi 10.000 km hoặc 12 tháng

**Agent Response**: "Thông tin về tần suất bảo dưỡng cụ thể cho VinFast VF8 không được cung cấp trong tài liệu hiện có..."

**Judge Scores**:
- gpt-4o: 3.8
- gpt-4o-mini: 2.8
- **Final Score**: 2.8/5.0 (FAIL)

**Retrieval Metrics**:
- Hit Rate: 0.0 ❌
- MRR: 0.0 ❌
- Precision@3: 0.0 ❌

**Judge Reasoning**: "Câu trả lời không chính xác vì không cung cấp thông tin về tần suất bảo dưỡng cụ thể..."

---

## 🔬 Root Cause Analysis (5 Whys)

### Why 1: Tại sao Agent không trả lời được câu hỏi?
**Answer**: Agent không tìm thấy thông tin bảo dưỡng trong tài liệu.

### Why 2: Tại sao không tìm thấy thông tin?
**Answer**: Retrieval stage trả về 0 relevant documents (hit_rate = 0).

### Why 3: Tại sao Retrieval thất bại?
**Answer**: Thông tin bảo dưỡng có thể không có trong các article files hoặc keyword matching không đủ.

### Why 4: Tại sao keyword matching thất bại?
**Answer**: Từ khóa "bảo dưỡng" không xuất hiện trong các documents được load, hoặc chunking strategy không tách được đúng context.

### Why 5: Nguyên nhân gốc rễ?
**Answer**: **Ingestion Pipeline** - Tài liệu gốc (VF8 manual) có thể không chứa đầy đủ thông tin bảo dưỡng, HOẶC chunking strategy không tối ưu cho việc retrieve thông tin dạng bảng/lịch.

---

## 📋 Failure Clustering

| Failure Type | Count | Percentage |
|--------------|-------|------------|
| Retrieval Failure | 1 | 100% |

### Chi tiết:
- **Retrieval Failure**: 1 case (10%) - Agent không tìm được context liên quan đến lịch bảo dưỡng

---

## 📈 Multi-Judge Analysis

| Judge Model | Avg Score | Agreement with Other Judge |
|-------------|-----------|---------------------------|
| gpt-4o | 4.28 | 85% |
| gpt-4o-mini | 4.00 | 85% |

**Observations**:
- gpt-4o tends to give slightly higher scores (0.28 difference)
- Agreement rate: 85% - shows good consensus between judges
- Disagreement case: "Tần suất bảo dưỡng" - gpt-4o gave 3.8, gpt-4o-mini gave 2.8

---

## 💡 Recommendations

### 1. Cải thiện Ingestion Pipeline
- Thêm đầy đủ thông tin bảo dưỡng vào knowledge base
- Sử dụng PDF parser tốt hơn để extract thông tin dạng bảng

### 2. Tối ưu Chunking Strategy
- Sử dụng semantic chunking thay vì fixed-size
- Thêm overlap giữa các chunks để capture context tốt hơn

### 3. Fallback Strategy
- Khi retrieval fail, sử dụng web search fallback
- Hoặc train model với more diverse examples

### 4. Cost Optimization (30% reduction)
- Hiện tại: $0.0143/run với 10 test cases
- Đề xuất: Sử dụng gpt-4o-mini cho cả 2 judges thay vì gpt-4o
- Ước tính giảm: ~50% chi phí

---

## 📊 Performance by Category

| Category | Avg Score | Pass Rate |
|----------|-----------|-----------|
| Vehicle Info | 5.0 | 100% |
| Specs | 4.65 | 100% |
| Safety | 4.3 | 100% |
| Operation | 4.23 | 100% |
| Charging | 4.5 | 100% |
| Infotainment | 3.3 | 100% |
| Emergency | 3.5 | 100% |
| Maintenance | 2.8 | 0% ❌ |

---

## 📈 Regression Comparison

| Metric | V1 | V2 | Delta |
|--------|-----|-----|-------|
| Judge Score | 4.18 | 4.14 | -0.04 |
| Hit Rate | 0.9 | 0.9 | 0.0 |
| MRR | 0.63 | 0.63 | 0.0 |
| Agreement Rate | 85% | 85% | 0% |

**Decision**: BLOCK RELEASE (delta < 0)

---

*Generated: 2026-04-21*
*System: AI Evaluation Factory v1.0*
*Judges: gpt-4o + gpt-4o-mini*