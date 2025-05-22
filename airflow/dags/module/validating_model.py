import mlflow 
import os
import random
import requests
import time

import logging
import pandas as pd 
from config.train_utils import load_instruction_dataset, encode_image, load_image_from_url
from config.train_utils import evaluate_key_metrics
import json 
import os 

os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL")

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Validation_models")

def get_recommendation(base64_image):
    api_key = os.getenv('RUNPOD_API_KEY')
    api_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not api_id:
        raise ValueError("API 키 또는 엔드포인트 ID가 누락되었습니다.")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    prompt = """
    당신은 패션 추천 전문가입니다. 아래 이미지를 보고 판단하여 적절한 코디를 JSON 형식으로 추천해주세요.

    이미지를 참고하여 다음 형식에 맞춰 출력해주세요:
    { 
      "answer": "...", 
      "recommend": { 
          "상의": [...], 
          "아우터": [...], 
          "하의": [...], 
          "신발": [...] 
      } 
    }

    주의사항:
    1) "answer" 문장에 반드시 '해당 상품은 데님 팬츠로 보이며 봄에 잘 어울리는 스타일입니다'처럼 **계절**과 **아이템 카테고리**를 명시하세요.
    2) "recommend"의 각 카테고리에는 **최소 3개의 아이템**을 제시해야 합니다.
    3) 이미지에 나타난 **주요 아이템은 해당 카테고리에서 제외**하고, 나머지 카테고리에서는 추천을 제공합니다.
    4) "recommend" 항목에는 **season**, **sub_category**, **main_category** 등의 필드를 추가하지 마세요.
    5) 참고 가이드라인에서 특정 카테고리가 빈 리스트([])일 경우, **임의로 항목을 추가하지 말고 빈 리스트 그대로 출력**해야 합니다.
    """

    payload = {
        'input': {
            "image_base64": base64_image,
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 512
        }
    }

    url = f"https://api.runpod.ai/v2/{api_id}/run"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()

        # 동기 응답
        if "output" in result:
            raw_output = result["output"]
        elif "id" in result:  # 비동기 처리
            task_id = result["id"]
            status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"

            while True:
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()

                if status_data["status"] == "COMPLETED":
                    raw_output = status_data.get("output")
                    
                    if isinstance(raw_output, dict) and "generated_text" in raw_output:
                            raw_output = raw_output["generated_text"]
                    break
                elif status_data["status"] in ["FAILED", "CANCELLED"]:
                    raise Exception(f"RunPod 작업 실패: {status_data['status']}")
                time.sleep(2)
        else:
            raise Exception("RunPod 결과에 'output' 또는 'id'가 없습니다.")

        try:
            # 가장 마지막 JSON 부분 추출
            if isinstance(raw_output, str):
                # "assistant\n\n{...}" 구조라면 이걸 분리
                json_str = raw_output.strip().split("assistant")[-1].strip()
                parsed = json.loads(json_str)
            elif isinstance(raw_output, dict):
                parsed = raw_output
            else:
                raise ValueError("예상치 못한 RunPod 응답 포맷")

            logging.info(f"파싱된 RunPod 결과: {parsed}")
            return parsed

        except Exception as e:
            logging.error(f"JSON 파싱 실패: {e}")
            logging.warning(f"원본 RunPod 응답: {raw_output}")
            return {}

    raise Exception(f"API 요청 실패: {response.status_code}, {response.text}")

def run_evaluation():
    logging.info("평가용 데이터 불러오는 중...")
    full_data = load_instruction_dataset()
    eval_samples = random.sample(full_data, 5)
    
    image_list = []
    evaluation_records = []

    for sample in eval_samples:
        try:
            image = load_image_from_url(sample["input"]["image"])
            image_list.append(image)
            evaluation_records.append({
                "input": sample["instruction"],
                "expected_output": sample["output"]["answer"]
            })
        except Exception as e:
            logging.warning(f"이미지 로딩 실패: {sample['input']['image']} | {e}")

    evaluation_df = pd.DataFrame(evaluation_records)

    # 예측 실행
    logging.info("모델 예측 실행 중...")
    predictions = []
    full_responses = []
    
    for i, row in evaluation_df.iterrows():
        image_b64 = encode_image(image_list[i])
        
        try:
            output = get_recommendation(image_b64)
            full_responses.append(output)
            
            logging.warning(f"[예측 {i}] RunPod 응답: {output}")

            if isinstance(output, dict) and "answer" in output:
                predictions.append(output["answer"])
            else:
                logging.warning(f"[예측 {i}] 'answer' 필드 누락 또는 비정상 응답")
                predictions.append("")
        except Exception as e:
            logging.error(f"[예측 {i}] 예외 발생: {e}")
            predictions.append("")
            full_responses.append({})

    # 예측 결과를 DataFrame에 추가
    evaluation_df["prediction"] = predictions

    with mlflow.start_run(run_name="Mensclub_Vision_Eval") as run:
        logging.info("MLflow 평가 시작...")

        # 기본 MLflow 평가 (이미 계산된 예측 사용)
        eval_result = mlflow.evaluate(
            data=evaluation_df,
            targets="expected_output",
            predictions="prediction",  # 이미 계산된 예측 컬럼 사용
            model_type="question-answering",
            evaluators="default",
        )

        # 핵심 메트릭 계산
        key_metrics = evaluate_key_metrics(predictions, full_responses)

        # 모든 메트릭 로깅
        for key, value in eval_result.metrics.items():
            logging.info(f"기본 지표 - {key}: {value}")
            mlflow.log_metric(key, value)

        for key, value in key_metrics.items():
            logging.info(f"핵심 지표 - {key}: {value}")
            mlflow.log_metric(key, value)

        # 결과 저장
        result_csv_path = "evaluation_result.csv"
        evaluation_df.to_csv(result_csv_path, index=False)
        mlflow.log_artifact(result_csv_path)

        # 전체 응답도 저장
        full_responses_df = pd.DataFrame({"full_response": full_responses})
        full_responses_df.to_csv("full_responses.csv", index=False)
        mlflow.log_artifact("full_responses.csv")

        logging.info(f"평가 완료. Run ID: {run.info.run_id}")
