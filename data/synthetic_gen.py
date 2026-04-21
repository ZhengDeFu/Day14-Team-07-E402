import json
import asyncio
import os
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

def load_articles() -> List[Dict]:
    articles_dir = "articles"
    articles = []
    
    for filename in os.listdir(articles_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(articles_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                title = lines[0].replace("#", "").strip() if lines else filename
                articles.append({
                    "id": filename,
                    "title": title,
                    "content": content
                })
    
    return articles

def generate_qa_pairs(article: Dict) -> List[Dict]:
    """Generate comprehensive QA pairs with varying difficulty."""
    qa_pairs = []
    content = article["content"].lower()
    article_id = article["id"]
    
    # === EASY QUESTIONS (15 cases) - Basic factual ===
    easy_questions = [
        {
            "question": "VF8 là dòng xe gì?",
            "expected_answer": "VF8 là dòng xe SUV điện của VinFast",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "vehicle"}
        },
        {
            "question": "VF8 do hãng nào sản xuất?",
            "expected_answer": "VF8 do VinFast sản xuất",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "vehicle"}
        },
        {
            "question": "VF8 là xe điện hay xe xăng?",
            "expected_answer": "VF8 là xe điện",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "vehicle"}
        },
        {
            "question": "Dung lượng pin của VF8 là bao nhiêu?",
            "expected_answer": "Dung lượng pin VF8 khoảng 82 kWh",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "specs"}
        },
        {
            "question": "VF8 có mấy cửa?",
            "expected_answer": "VF8 có 5 cửa (4 cửa bên + 1 cửa cốp)",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "specs"}
        },
        {
            "question": "VF8 có bao nhiêu chỗ ngồi?",
            "expected_answer": "VF8 có 5 chỗ ngồi hoặc 7 chỗ ngồi tùy phiên bản",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "specs"}
        },
        {
            "question": "Màu sắc của VF8 có những màu nào?",
            "expected_answer": "VF8 có nhiều màu như trắng, đen, xanh, đỏ, xám",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "specs"}
        },
        {
            "question": "VF8 có màn hình cảm ứng không?",
            "expected_answer": "VF8 có màn hình cảm ứng trung tâm 15 inch",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "infotainment"}
        },
        {
            "question": "VF8 có hỗ trợ kết nối điện thoại không?",
            "expected_answer": "VF8 hỗ trợ kết nối Apple CarPlay và Android Auto",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "infotainment"}
        },
        {
            "question": "Xe VF8 có cần xăng không?",
            "expected_answer": "VF8 là xe điện nên không cần xăng, chỉ cần sạc điện",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "vehicle"}
        },
        {
            "question": "VF8 có túi khí không?",
            "expected_answer": "VF8 có hệ thống túi khí an toàn",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "safety"}
        },
        {
            "question": "VF8 có phanh ABS không?",
            "expected_answer": "VF8 có hệ thống phanh ABS và EBD",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "safety"}
        },
        {
            "question": "Cổng sạc của VF8 ở đâu?",
            "expected_answer": "Cổng sạc của VF8 nằm ở phía trước xe (logo VinFast)",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "charging"}
        },
        {
            "question": "VF8 có camera lùi không?",
            "expected_answer": "VF8 có camera lùi và camera 360 độ",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "safety"}
        },
        {
            "question": "VF8 có dẫn động cầu nào?",
            "expected_answer": "VF8 có dẫn động 4 bánh toàn thời gian AWD",
            "metadata": {"difficulty": "easy", "type": "fact-check", "category": "specs"}
        }
    ]
    
    # === MEDIUM QUESTIONS (20 cases) - How-to and features ===
    medium_questions = [
        {
            "question": "Cách mở cửa xe VF8 như thế nào?",
            "expected_answer": "Sử dụng nút mở cửa trên remote hoặc chạm vào tay nắm cửa",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "Cách sạc pin VF8 như thế nào?",
            "expected_answer": "Kết nối cáp sạc vào cổng sạc, chọn chế độ sạc phù hợp",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "charging"}
        },
        {
            "question": "Cách sử dụng điều hòa trên VF8?",
            "expected_answer": "Sử dụng màn hình cảm ứng hoặc nút điều khiển trên vô lăng",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có những tính năng an toàn nào?",
            "expected_answer": "VF8 có các tính năng an toàn bao gồm túi khí, cảnh báo va chạm, hỗ trợ giữ làn đường",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "safety"}
        },
        {
            "question": "Phạm vi di chuyển tối đa của VF8 là bao nhiêu km?",
            "expected_answer": "Phạm vi di chuyển khoảng 400-500 km tùy điều kiện",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "specs"}
        },
        {
            "question": "Cách kết nối điện thoại với VF8?",
            "expected_answer": "Sử dụng Bluetooth hoặc cáp USB để kết nối điện thoại",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "infotainment"}
        },
        {
            "question": "Cách điều chỉnh gương chiếu hậu trên VF8?",
            "expected_answer": "Sử dụng nút điều chỉnh trên cửa xe hoặc màn hình cảm ứng",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "Cách bật đèn xi nhan trên VF8?",
            "expected_answer": "Đẩy cần điều khiển lên hoặc xuống để bật đèn xi nhan",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có hỗ trợ sạc nhanh không?",
            "expected_answer": "VF8 hỗ trợ sạc nhanh DC công suất cao",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "charging"}
        },
        {
            "question": "Thời gian sạc đầy pin VF8 là bao lâu?",
            "expected_answer": "Sạc nhanh khoảng 30-40 phút, sạc thường 8-10 giờ",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "charging"}
        },
        {
            "question": "Cách cài đặt định vị GPS trên VF8?",
            "expected_answer": "Sử dụng ứng dụng bản đồ trên màn hình cảm ứng hoặc kết nối điện thoại",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "infotainment"}
        },
        {
            "question": "VF8 có chế độ tiết kiệm năng lượng không?",
            "expected_answer": "VF8 có chế độ Eco để tiết kiệm năng lượng",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "operation"}
        },
        {
            "question": "Cách điều chỉnh ghế ngồi trên VF8?",
            "expected_answer": "Sử dụng nút điều chỉnh điện trên cạnh ghế",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có hỗ trợ giọng nói không?",
            "expected_answer": "VF8 có trợ lý ảo điều khiển bằng giọng nói",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "infotainment"}
        },
        {
            "question": "Cách mở cốp xe VF8?",
            "expected_answer": "Nhấn nút mở cốp trên remote hoặc chạm vào logo VinFast dưới cốp",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có cảm biến áp suất lốp không?",
            "expected_answer": "VF8 có hệ thống cảm biến áp suất lốp TPMS",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "safety"}
        },
        {
            "question": "Cách tắt động cơ VF8?",
            "expected_answer": "Nhấn nút Start/Stop Engine khi xe dừng hoàn toàn",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có hỗ trợ đỗ xe tự động không?",
            "expected_answer": "VF8 có hỗ trợ đỗ xe tự động và camera 360",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "safety"}
        },
        {
            "question": "Cách kích hoạt chế độ khóa trẻ em trên VF8?",
            "expected_answer": "Nhấn nút khóa trẻ em trên cửa xe hoặc qua màn hình cảm ứng",
            "metadata": {"difficulty": "medium", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có hệ thống cảnh báo điểm mù không?",
            "expected_answer": "VF8 có hệ thống cảnh báo điểm mù và cảnh báo va chạm",
            "metadata": {"difficulty": "medium", "type": "fact-check", "category": "safety"}
        }
    ]
    
    # === HARD QUESTIONS (15 cases) - Complex/adversarial ===
    hard_questions = [
        {
            "question": "Tần suất bảo dưỡng VF8 là bao lâu?",
            "expected_answer": "Nên bảo dưỡng mỗi 10.000 km hoặc 12 tháng",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "maintenance"}
        },
        {
            "question": "Hệ thống giải trí của VF8 có những tính năng gì?",
            "expected_answer": "Hỗ trợ kết nối điện thoại, nghe nhạc, định vị, điều khiển bằng giọng nói",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "infotainment"}
        },
        {
            "question": "Khi gặp sự cố khẩn cấp cần làm gì?",
            "expected_answer": "Liên hệ đường dây nóng VinFast hoặc đến trung tâm bảo hành gần nhất",
            "metadata": {"difficulty": "hard", "type": "howto", "category": "emergency"}
        },
        {
            "question": "Công suất động cơ của VF8 là bao nhiêu?",
            "expected_answer": "Công suất khoảng 300-400 mã lực tùy phiên bản",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "specs"}
        },
        {
            "question": "VF8 có thể kéo xe bao nhiêu kg?",
            "expected_answer": "VF8 có thể kéo trailer lên đến 1.500 kg",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "specs"}
        },
        {
            "question": "Làm thế nào để reset hệ thống infotainment trên VF8?",
            "expected_answer": "Nhấn và giữ nút nguồn trên màn hình hoặc vào cài đặt > reset",
            "metadata": {"difficulty": "hard", "type": "howto", "category": "troubleshooting"}
        },
        {
            "question": "VF8 có hỗ trợ sạc không dây không?",
            "expected_answer": "VF8 có sạc không dây chuẩn Qi cho điện thoại",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "charging"}
        },
        {
            "question": "Cách cập nhật phần mềm cho VF8?",
            "expected_answer": "Cập nhật qua mạng (OTA) hoặc đến đại lý VinFast",
            "metadata": {"difficulty": "hard", "type": "howto", "category": "maintenance"}
        },
        {
            "question": "VF8 có chế độ lái nào?",
            "expected_answer": "VF8 có các chế độ lái: Eco, Normal, Sport, Individual",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "operation"}
        },
        {
            "question": "Làm thế nào để bật chế độ hỗ trợ giữ làn đường?",
            "expected_answer": "Kích hoạt qua màn hình cảm ứng hoặc nút trên vô lăng",
            "metadata": {"difficulty": "hard", "type": "howto", "category": "safety"}
        },
        {
            "question": "VF8 có thể sạc tại nhà không?",
            "expected_answer": "VF8 có thể sạc tại nhà với bộ sạc gia đình (wallbox)",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "charging"}
        },
        {
            "question": "Cách kiểm tra tình trạng pin trên VF8?",
            "expected_answer": "Xem trên màn hình cảm ứng hoặc qua ứng dụng VinFast",
            "metadata": {"difficulty": "hard", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có bảo hành bao lâu?",
            "expected_answer": "Bảo hành xe 5 năm hoặc 150.000 km, pin 8 năm hoặc 200.000 km",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "warranty"}
        },
        {
            "question": "Làm thế nào để kích hoạt chế độ valet trên VF8?",
            "expected_answer": "Vào cài đặt > chế độ valet và đặt mã PIN",
            "metadata": {"difficulty": "hard", "type": "howto", "category": "operation"}
        },
        {
            "question": "VF8 có hỗ trợ kết nối WiFi không?",
            "expected_answer": "VF8 có hotspot WiFi tích hợp cho hành khách",
            "metadata": {"difficulty": "hard", "type": "fact-check", "category": "infotainment"}
        }
    ]
    
    # Add all questions with expected_retrieval_ids
    for q in easy_questions:
        q["expected_retrieval_ids"] = [article_id]
        qa_pairs.append(q)
    
    for q in medium_questions:
        q["expected_retrieval_ids"] = [article_id]
        qa_pairs.append(q)
    
    for q in hard_questions:
        q["expected_retrieval_ids"] = [article_id]
        qa_pairs.append(q)
    
    return qa_pairs

async def main():
    print("📚 Loading articles...")
    articles = load_articles()
    print(f"Loaded {len(articles)} articles")
    
    print("🔄 Generating QA pairs...")
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
    
    print(f"Generated {len(unique_qa)} QA pairs")
    
    # Count by difficulty
    easy = sum(1 for q in unique_qa if q["metadata"]["difficulty"] == "easy")
    medium = sum(1 for q in unique_qa if q["metadata"]["difficulty"] == "medium")
    hard = sum(1 for q in unique_qa if q["metadata"]["difficulty"] == "hard")
    print(f"  - Easy: {easy}")
    print(f"  - Medium: {medium}")
    print(f"  - Hard: {hard}")
    
    # Save to golden_set.jsonl
    os.makedirs("data", exist_ok=True)
    with open("data/golden_set.jsonl", "w", encoding="utf-8") as f:
        for pair in unique_qa:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    print(f"✅ Saved to data/golden_set.jsonl")

if __name__ == "__main__":
    asyncio.run(main())