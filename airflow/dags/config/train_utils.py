from config.connection import get_client
import json 
import logging
from io import BytesIO
from PIL import Image
from .category_data import SEASON, ITEM_CATEGORIES
import base64
import requests

def load_instruction_dataset(bucket_name="model-training-data", key="train/instruction_dataset.json"):
    client = get_client()
    logging.info("버킷 연결중 ...")
    response = client.get_object(Bucket=bucket_name, Key=key)
    logging.info("버킷 연결완료")
    body = response["Body"].read().decode("utf-8")
    logging.info("데이터 로드 완료")
    return json.loads(body)

def load_image_from_url(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert("RGB")

def encode_image(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    logging.info("이미지 변환 완료")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def evaluate_key_metrics(predictions, full_responses):
    """핵심 메트릭 2가지: 계절 언급 + 실제 카테고리 언급"""
    
    season_count = 0
    category_count = 0
    total = len(predictions)
    
    # 체크할 요소들
    
    for pred in predictions:
        pred_str = str(pred)
        
        # 1. 계절 언급 체크
        if any(season in pred_str for season in SEASON):
            season_count += 1
        
        # 2. 실제 카테고리 언급 체크  
        if any(category in pred_str for category in ITEM_CATEGORIES):
            category_count += 1
    
    return {
        "season_mention_rate": season_count / total if total > 0 else 0,
        "item_category_mention_rate": category_count / total if total > 0 else 0,
        "both_requirements_rate": sum(1 for pred in predictions 
                                    if any(season in str(pred) for season in SEASON) and 
                                       any(cat in str(pred) for cat in ITEM_CATEGORIES)) / total if total > 0 else 0
    }