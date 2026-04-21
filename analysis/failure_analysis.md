# Failure Analysis - Lab Day 14: AI Evaluation Factory

**Dự án:** VinFast VF8 Chatbot Evaluation System  
**Team:** Team 07 - E402  
**Ngày:** 21/04/2026

---

## Executive Summary

Phân tích này áp dụng phương pháp "5 Whys" để tìm root causes của các vấn đề phát sinh trong quá trình xây dựng và chạy AI Evaluation Factory. Mục tiêu là xác định nguyên nhân gốc rễ và đưa ra giải pháp cải thiện hệ thống.

---

## 📊 Benchmark Results Overview

| Metric | V1 (Baseline) | V2 (Optimized) | Delta |
|--------|---------------|----------------|-------|
| Judge Score | 3.64/5.0 | 3.74/5.0 | +0.10 |
| Hit Rate | 0.96 | 0.98 | +0.02 |
| MRR | 1.0 | 1.0 | 0.00 |
| Pass Rate | 100% | 100% | 0% |
| Agreement Rate | 0.85 | 0.87 | +0.02 |
| Execution Time | <2 min | <2 min | 0 |
| Total Cost | $0.0419 | $0.0419 | $0.00 |
| Timestamp | 2026-04-21 18:35:20 | 2026-04-21 18:35:20 | - |

---

## Issue #1: V2 Slightly Better Than V1 (2.7% improvement)

### Hiện tượng:
```
V1 Judge Score: 3.64
V2 Judge Score: 3.74
Delta: +0.10 (2.7% improvement)
```

### 5 Whys Analysis:

**Why 1: Tại sao V2 chỉ tốt hơn V1 một chút?**
→ Sự khác biệt giữa V1 và V2 không đủ lớn

**Why 2: Tại sao sự khác biệt không đủ lớn?**
→ V1 đã khá tốt (3.64/5), V2 chỉ cải thiện prompt và retrieval

**Why 3: Tại sao không có sự khác biệt lớn hơn về architecture?**
→ Cả V1 và V2 đều dùng cùng retrieval method và model

**Why 4: Tại sao không implement reranking hoặc advanced techniques?**
→ Time constraint và focus vào evaluation framework hơn là agent optimization

**Why 5: Tại sao không có baseline yếu hơn để so sánh?**
→ V1 được thiết kế quá tốt, không phải truly "weak" baseline

### Root Cause:
**V1 baseline quá mạnh, thiếu differentiation rõ ràng giữa versions**

### Impact:
- ✅ Low: Vẫn đạt yêu cầu (V2 > V1)
- Khó demonstrate value of improvements
- ROI không rõ ràng ($0.00 cho 2.7% improvement)

### Recommendations:
1. 🔄 **TODO:** Tạo V1 yếu hơn (keyword search, weaker prompt)
2. 🔄 **TODO:** V2 implement reranking
3. 🔄 **TODO:** V2 use better model (GPT-4)
4. 🔄 **TODO:** Add more challenging test cases
5. 🔄 **TODO:** Implement RAG fusion hoặc advanced techniques

---

## Issue #2: Hit Rate Improvement (96% → 98%)

### Hiện tượng:
```
V1 Hit Rate: 0.96
V2 Hit Rate: 0.98
Delta: +0.02 (2% improvement)
```

### 5 Whys Analysis:

**Why 1: Tại sao V2 retrieve được tốt hơn?**
→ V2 có better retrieval strategy hoặc top_k cao hơn

**Why 2: Tại sao V1 miss 4% cases?**
→ Retrieval strategy không optimal hoặc top_k quá thấp

**Why 3: Tại sao không tăng top_k từ đầu?**
→ Trade-off giữa latency và recall

**Why 4: Tại sao không implement reranking?**
→ Time constraint, focus vào evaluation

**Why 5: Tại sao không test với different retrieval methods?**
→ SimpleVectorStore limitation, Supabase failed

### Root Cause:
**Retrieval strategy không optimal, thiếu reranking**

### Impact:
- ✅ Low: 96% → 98% vẫn acceptable
- 4% miss rate có thể ảnh hưởng user experience
- Opportunity để improve

### Recommendations:
1. 🔄 **TODO:** Implement reranking để improve hit rate
2. 🔄 **TODO:** Optimize top_k parameter
3. 🔄 **TODO:** Test different retrieval methods
4. 🔄 **TODO:** Add semantic similarity reranking
5. 🔄 **TODO:** Monitor hit rate in production

---

## Issue #3: Agreement Rate Improvement (85% → 87%)

### Hiện tượng:
```
V1 Agreement Rate: 0.85
V2 Agreement Rate: 0.87
Delta: +0.02 (2% improvement)
```

### 5 Whys Analysis:

**Why 1: Tại sao V2 judges đồng thuận hơn?**
→ V2 có better answer quality, judges agree more

**Why 2: Tại sao V1 judges không đồng thuận 100%?**
→ V1 answers ambiguous, judges interpret differently

**Why 3: Tại sao V1 answers ambiguous?**
→ Prompt không clear, retrieval context confusing

**Why 4: Tại sao không improve V1 prompt?**
→ Focus vào V2 optimization

**Why 5: Tại sao không implement prompt engineering?**
→ Time constraint

### Root Cause:
**V1 prompt không optimal, V2 prompt better**

### Impact:
- ✅ Low: 85% → 87% vẫn good agreement
- 13-15% disagreement acceptable
- Opportunity để improve consistency

### Recommendations:
1. 🔄 **TODO:** Improve V1 prompt clarity
2. 🔄 **TODO:** Add few-shot examples
3. 🔄 **TODO:** Implement prompt optimization
4. 🔄 **TODO:** Add consistency checks
5. 🔄 **TODO:** Monitor judge agreement in production
## Summary of Root Causes

1. **Differentiation:** V1/V2 không đủ khác biệt
2. **Cost:** Thiếu optimization và caching
3. **Performance:** Trade-off accepted nhưng có thể optimize
4. **Testing:** Thiếu adversarial và stress testing
5. **Chunking:** Không có proper chunking strategy
6. **Ingestion:** Thiếu automated pipeline

---

## Action Items

### High Priority:
1. 🔄 Add more challenging test cases
2. 🔄 Implement response caching
3. 🔄 Optimize token usage

### Medium Priority:
4. 🔄 Implement proper chunking
5. 🔄 Add monitoring and alerting
6. 🔄 Build ingestion pipeline

### Low Priority:
7. 🔄 Implement streaming responses
8. 🔄 Add chaos engineering
9. 🔄 Security testing
10. 🔄 Load testing

---

## Lessons Learned

1. **Cost matters:** Track and optimize from day 1
2. **Test edge cases:** 100% pass rate might mean tests too easy
3. **Chunking is critical:** Whole documents → Poor retrieval precision
4. **Automation is key:** Manual processes don't scale
5. **Simple can be effective:** In-memory store worked well for evaluation

---

## Conclusion

Hệ thống hoạt động tốt với 100% pass rate và high agreement rate. Phân tích đã phát hiện improvement opportunities:

- **Cost:** Cần optimization và caching
- **Testing:** Cần more challenging cases
- **Architecture:** Cần proper chunking và ingestion
- **Differentiation:** Cần stronger V1/V2 contrast

Những vấn đề này không phải critical failures mà là opportunities để improve system quality và production-readiness.

**Overall Assessment:** ✅ System meets requirements, ready for submission với clear roadmap for improvements.

---

*Generated: 2026-04-21*  
*System: AI Evaluation Factory v1.0*  
*Judges: GPT-4o-mini + Gemma-3-27B*  
*Runtime: <2 minutes for 50 cases*
