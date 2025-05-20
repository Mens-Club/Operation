# 메인 카테고리 랜덤 채워주는 함수 
import random
import re

SHOES_CATEGORIES = {
    "캔버스/단화",
    "패션스니커즈화",
    "앵클/숏 부츠",
    "미들/하프 부츠",
    "워커",
    "더비 슈즈",
    "스트레이트 팁",
    "로퍼",
    "모카신",
    "쪼리/플립플랍",
    "스포츠/캐주얼 샌들"
}

COLOR_PALETTE_BY_SEASON = {
    "봄": ['오트밀', '아이보리', '화이트', '블랙', '베이지', '네이비', "흑청", "진청", "연청", "중청"],
    "여름": ['스카이블루', '네이비', '화이트', '블랙', "연청", "중청", "흑청"],
    "가을": ['화이트', '블랙', '버건디', '오트밀', '아이보리', '카키', '베이지', '브라운', "흑청", "진청", "중청"],
    "겨울": ['화이트', '그레이', '블랙', '네이비', '카키', "흑청", "진청", "중청"]
}

def get_random_item_id(cursor, category_name):
    # 카테고리가 신발 리스트에 포함돼 있으면 shoes 테이블에서 조회
    table_name = "shoes" if category_name in SHOES_CATEGORIES else "clothes"
    
    query = f"""
        SELECT id FROM {table_name}
        WHERE sub_category = %s
    """
    cursor.execute(query, (category_name,))
    results = cursor.fetchall()
    return random.choice(results)['id'] if results else None

def get_price(cursor, item_id):
    if not item_id:
        return 0
    cursor.execute("SELECT price FROM clothes WHERE id = %s", (item_id,))
    result = cursor.fetchone()
    return result['price'] if result else 0

def fetch_recommendations_to_process(cursor):
    cursor.execute("""
        SELECT r.id, r.top_id, r.bottom_id, r.outer_id, r.shoes_id, r.style, r.answer, r.reasoning_text, p.id AS picked_id
        FROM recommend_recommendation r
        JOIN recommend_bookmark p ON r.id = p.recommendation_id
        WHERE (r.top_id IS NULL OR r.bottom_id IS NULL OR r.shoes_id IS NULL OR r.outer_id IS NULL)
          AND p.whether_main = 0
    """)
    return cursor.fetchall()

def update_whether_main(cursor, picked_id):
    cursor.execute("""
        UPDATE recommend_bookmark SET whether_main = 1 WHERE id = %s
    """, (picked_id,))

def extract_clothing_name(answer: str) -> str:
    match = re.search(r'상품은 (.+?)로 보이며', answer)
    return match.group(1) if match else None

def process_recommendations(cursor):
    rows = fetch_recommendations_to_process(cursor)
    for row in rows:
        top_id = row['top_id']
        bottom_id = row['bottom_id']
        outer_id = row['outer_id']
        shoes_id = row['shoes_id']
        style = row['style']
        reasoning_text = row['reasoning_text']
        answer = row['answer']
        picked_id = row['picked_id']

        clothing_name = extract_clothing_name(answer)
        if not clothing_name:
            print('clothing_name')
            continue

        filled_id = get_random_item_id(cursor, clothing_name)
        if not filled_id:
            print('filled_id')
            continue

        if not top_id:
            top_id = filled_id
        elif not bottom_id:
            bottom_id = filled_id
        elif not shoes_id:
            shoes_id = filled_id
        elif not outer_id and '여름' not in answer:
            outer_id = filled_id

        total_price = (
            get_price(cursor, top_id) +
            get_price(cursor, bottom_id) +
            get_price(cursor, outer_id) +
            get_price(cursor, shoes_id)
        )

        cursor.execute("""
            INSERT INTO recommend_main_recommendation (top_id, bottom_id, outer_id, shoes_id, style, total_price, reasoning_text, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            top_id, bottom_id, outer_id, shoes_id, style, total_price, reasoning_text
        ))

        # 처리 후 picked의 whether_main 값을 1로 업데이트
        update_whether_main(cursor, picked_id)

        print(f"Inserted main_recommend from recommend.id={row['id']} (picked.id={picked_id})")