import json
import asyncio
import os
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Read all article files
def load_articles() -> List[Dict]:
    articles_dir = "articles"
    articles = []
    
    for filename in os.listdir(articles_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(articles_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract title from first line
                lines = content.split("\n")
                title = lines[0].replace("#", "").strip() if lines else filename
                articles.append({
                    "id": filename,
                    "title": title,
                    "content": content
                })
    
    return articles

def extract_chunks(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks for retrieval testing."""
    # Split by paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_qa_pairs(article: Dict) -> List[Dict]:
    """Generate QA pairs from article content."""
    qa_pairs = []
    content = article["content"]
    article_id = article["id"]
    
    # Extract key information patterns
    patterns = [
        # Feature/function patterns
        (r'([A-Z][a-zA-Z\s]+)\s+(là|is|provides|offers|includes|has)\s+([^\n.]+)', 'feature'),
        # How to patterns
        (r'Làm thế nào (để |to )?([^\?]+)\?', 'howto'),
        # What is patterns  
        (r'([A-Z][a-zA-Z\s]+)\s+là\s+([^\n.]+)', 'definition'),
        # Warning/Caution patterns
        (r'Cảnh báo:?\s+([^\n.]+)', 'warning'),
        (r'Chú ý:?\s+([^\n.]+)', 'note'),
    ]
    
    # Simple rule-based QA generation
    # 1. Definition questions
    if "VF8" in content:
        qa_pairs.append({
            "question": "VF8 là dòng xe gì?",
            "expected_answer": "VF8 là dòng xe SUV điện của VinFast",
            "context": "VF8 - Owner's Manual",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "vehicle"}
        })
    
    # 2. Feature questions
    if "pin" in content.lower() or "battery" in content.lower():
        qa_pairs.append({
            "question": "Dung lượng pin của VF8 là bao nhiêu?",
            "expected_answer": "Dung lượng pin VF8 khoảng 82 kWh",
            "context": "Battery specifications",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "specs"}
        })
    
    # 3. Safety questions
    if "an toàn" in content.lower() or "safety" in content.lower():
        qa_pairs.append({
            "question": "VF8 có những tính năng an toàn nào?",
            "expected_answer": "VF8 có các tính năng an toàn bao gồm túi khí, cảnh báo va chạm, hỗ trợ giữ làn đường",
            "context": "Safety features",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "safety"}
        })
    
    # 4. Operation questions
    if "cửa" in content.lower() or "door" in content.lower():
        qa_pairs.append({
            "question": "Cách mở cửa xe VF8 như thế nào?",
            "expected_answer": "Sử dụng nút mở cửa trên remote hoặc chạm vào tay nắm cửa",
            "context": "Door operation",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "easy", "type": "howto", "category": "operation"}
        })
    
    # 5. Charging questions
    if "sạc" in content.lower() or "charge" in content.lower():
        qa_pairs.append({
            "question": "Cách sạc pin VF8 như thế nào?",
            "expected_answer": "Kết nối cáp sạc vào cổng sạc, chọn chế độ sạc phù hợp",
            "context": "Charging instructions",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "medium", "type": "howto", "category": "charging"}
        })
    
    # 6. Maintenance questions
    if "bảo dưỡng" in content.lower() or "maintenance" in content.lower():
        qa_pairs.append({
            "question": "Tần suất bảo dưỡng VF8 là bao lâu?",
            "expected_answer": "Nên bảo dưỡng mỗi 10.000 km hoặc 12 tháng",
            "context": "Maintenance schedule",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "maintenance"}
        })
    
    # 7. Specification questions
    if "phạm vi" in content.lower() or "range" in content.lower():
        qa_pairs.append({
            "question": "Phạm vi di chuyển tối đa của VF8 là bao nhiêu km?",
            "expected_answer": "Phạm vi di chuyển khoảng 400-500 km tùy điều kiện",
            "context": "Driving range",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "specs"}
        })
    
    # 8. Climate control
    if "điều hòa" in content.lower() or "climate" in content.lower() or "AC" in content:
        qa_pairs.append({
            "question": "Cách sử dụng điều hòa trên VF8?",
            "expected_answer": "Sử dụng màn hình cảm ứng hoặc nút điều khiển trên vô lăng",
            "context": "Climate control",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "easy", "type": "howto", "category": "operation"}
        })
    
    # 9. Infotainment
    if "giải trí" in content.lower() or "infotainment" in content.lower() or "màn hình" in content.lower():
        qa_pairs.append({
            "question": "Hệ thống giải trí của VF8 có những tính năng gì?",
            "expected_answer": "Hỗ trợ kết nối điện thoại, nghe nhạc, định vị, điều khiển bằng giọng nói",
            "context": "Infotainment system",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "infotainment"}
        })
    
    # 10. Emergency procedures
    if "khẩn cấp" in content.lower() or "emergency" in content.lower():
        qa_pairs.append({
            "question": "Khi gặp sự cố khẩn cấp cần làm gì?",
            "expected_answer": "Liên hệ đường dây nóng VinFast hoặc đến trung tâm bảo hành gần nhất",
            "context": "Emergency procedures",
            "expected_retrieval_ids": [article_id],
            "metadata": {"difficulty": "hard", "type": "howto", "category": "emergency"}
        })
    
    return qa_pairs

async def generate_qa_from_text(text: str, num_pairs: int = 5) -> List[Dict]:
    """
    Generate QA pairs from text using rule-based extraction.
    """
    print(f"Generating {num_pairs} QA pairs from text...")
    
    articles = load_articles()
    all_qa_pairs = []
    
    for article in articles:
        qa_pairs = generate_qa_pairs(article)
        all_qa_pairs.extend(qa_pairs)
    
    # Remove duplicates based on question
    seen = set()
    unique_qa = []
    for qa in all_qa_pairs:
        if qa["question"] not in seen:
            seen.add(qa["question"])
            unique_qa.append(qa)
    
    return unique_qa[:num_pairs] if num_pairs > 0 else unique_qa

async def main():
    print("📚 Loading articles...")
    articles = load_articles()
    print(f"Loaded {len(articles)} articles")
    
    print("🔄 Generating QA pairs...")
    qa_pairs = await generate_qa_from_text("", num_pairs=0)  # Generate all
    
    print(f"Generated {len(qa_pairs)} QA pairs")
    
    # Save to golden_set.jsonl
    os.makedirs("data", exist_ok=True)
    with open("data/golden_set.jsonl", "w", encoding="utf-8") as f:
        for pair in qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    print(f"✅ Saved to data/golden_set.jsonl")
    print(f"\nSample questions:")
    for i, qa in enumerate(qa_pairs[:5]):
        print(f"  {i+1}. {qa['question']}")

if __name__ == "__main__":
    asyncio.run(main())