# 🔍 Failure Analysis Report

## 📊 Tổng quan Benchmark Results

| Metric | Value |
|--------|-------|
| Total Test Cases | 50 |
| Pass Rate | 88% (44/50) |
| Judge Score (avg) | 4.09/5.0 |
| Hit Rate | 100% |
| MRR | 0.90 |
| Agreement Rate | 94% |
| Estimated Cost | $0.0678 |
| Avg Latency | 1.61s |

---

## 📈 Performance by Difficulty

| Difficulty | Count | Pass Rate | Avg Score |
|------------|-------|-----------|-----------|
| Easy | 15 | 100% | 4.85 |
| Medium | 20 | 95% | 4.12 |
| Hard | 15 | 67% | 3.28 |

---

## ❌ Failed Test Cases (6 cases)

### 1. "Màu sắc của VF8 có những màu nào?"
- **Score**: 2.8/5.0
- **Reason**: Agent không cung cấp được thông tin cụ thể về màu sắc

### 2. "VF8 có hỗ trợ giọng nói không?"
- **Score**: 2.6/5.0
- **Reason**: Agent trả lời sai (nói không có nhưng thực tế có)

### 3. "VF8 có hỗ trợ đỗ xe tự động không?"
- **Score**: 2.4/5.0
- **Reason**: Agent trả lời sai (nói không có nhưng thực tế có)

### 4. "Tần suất bảo dưỡng VF8 là bao lâu?"
- **Score**: 2.8/5.0
- **Reason**: Không tìm thấy thông tin trong tài liệu

### 5. "VF8 có hỗ trợ sạc không dây không?"
- **Score**: 2.6/5.0
- **Reason**: Agent trả lời sai (nói không có nhưng thực tế có)

### 6. "VF8 có bảo hành bao lâu?"
- **Score**: 2.9/5.0
- **Reason**: Không cung cấp được thông tin bảo hành cụ thể

---

## 🔬 Root Cause Analysis (5 Whys)

### Why 1: Tại sao có 6 cases fail?
**Answer**: Agent cung cấp thông tin không chính xác hoặc không đầy đủ.

### Why 2: Tại sao thông tin không chính xác?
**Answer**: Retrieval lấy được context nhưng LLM sinh câu trả lời sai (hallucination).

### Why 3: Tại sao LLM sinh câu trả lời sai?
**Answer**: Prompt không yêu cầu rõ ràng hoặc context không đủ chi tiết.

### Why 4: Tại sao một số thông tin không có trong context?
**Answer**: Một số thông tin (bảo hành, màu sắc) có thể không có trong articles.

### Why 5: Nguyên nhân gốc rễ?
**Answer**: 
1. **Prompt Engineering** - Prompt cần cải thiện để yêu cầu câu trả lời chính xác hơn
2. **Knowledge Gap** - Cần bổ sung thêm tài liệu về bảo hành, màu sắc

---

## 📋 Failure Clustering

| Failure Type | Count | Percentage |
|--------------|-------|------------|
| Hallucination (LLM sinh sai) | 3 | 50% |
| Missing Information (KB không có) | 3 | 50% |

---

## 📈 Multi-Judge Analysis

| Judge Model | Avg Score | Agreement |
|-------------|-----------|-----------|
| gpt-4o | 4.18 | 94% |
| gpt-4o-mini | 4.00 | 94% |

**Observations**:
- Agreement rate: 94% - excellent consensus
- gpt-4o gives slightly higher scores (+0.18)
- No position bias detected

---

## 💡 Recommendations

### 1. Cải thiện Prompt
- Thêm instruction: "Nếu không chắc chắn, hãy nói không biết"
- Yêu cầu cite nguồn trong câu trả lời

### 2. Bổ sung Knowledge Base
- Thêm tài liệu về bảo hành, màu sắc, tính năng chi tiết

### 3. Fallback Strategy
- Khi confidence thấp, fallback sang web search

### 4. Cost Optimization
- Hiện tại: $0.0678/50 cases
- Đề xuất: Dùng gpt-4o-mini cho cả 2 judges → giảm ~50% chi phí

---

## 📊 Regression Comparison

| Metric | V1 | V2 | Delta |
|--------|-----|-----|-------|
| Judge Score | 4.12 | 4.09 | -0.03 |
| Hit Rate | 1.0 | 1.0 | 0.0 |
| MRR | 0.9 | 0.9 | 0.0 |
| Agreement Rate | 94% | 94% | 0% |

**Decision**: BLOCK RELEASE (delta < 0)

---

## � Technical Metrics Explanation

### MRR (Mean Reciprocal Rank)
- **Definition**: Trung bình cộng của 1/rank của kết quả relevant đầu tiên
- **Current**: 0.90 - Rất tốt, thường relevant document ở vị trí 1-2

### Hit Rate
- **Definition**: Tỷ lệ queries có ít nhất 1 relevant document trong top-k
- **Current**: 100% - Tất cả queries đều retrieve được relevant docs

### Agreement Rate
- **Definition**: Tỷ lệ 2 judges đồng ý (chênh lệch ≤ 0.5 điểm)
- **Current**: 94% - Cao, cho thấy đánh giá khách quan

### Cohen's Kappa (for future)
- **Definition**: Đo lường agreement giữa 2 judges sau khi loại bỏ random agreement
- **Estimated**: ~0.85 (substantial agreement)

---

*Generated: 2026-04-21*
*System: AI Evaluation Factory v1.0*
*Judges: gpt-4o + gpt-4o-mini*
*Runtime: ~80 seconds for 50 cases*