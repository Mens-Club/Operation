import os 
import requests
import time


def runpod_run(input_data=None, endpoint_id=None, api_key=None, timeout=300):
    """
    RunPod API를 통해 서버리스 함수 실행
    
    Args:
        input_data: 입력 데이터 (dict 또는 None)
        endpoint_id: RunPod 엔드포인트 ID (기본값: 환경변수 TRAIN_ENDPOINT_ID)
        api_key: RunPod API 키 (기본값: 환경변수 RUNPOD_API_KEY)
        timeout: 최대 대기 시간(초) (기본값: 300초)
    
    Returns:
        실행 결과
    """
    # 환경변수에서 설정 가져오기
    api_key = api_key or os.getenv('RUNPOD_API_KEY')
    endpoint_id = endpoint_id or os.getenv('TRAIN_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        raise ValueError("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # 입력 데이터 준비
    if input_data is None:
        payload = {}
    else:
        payload = {'input': input_data}
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        
        # 동기 요청 (즉시 결과 반환)
        if "output" in result:
            return result["output"]
        
        # 비동기 요청 (작업 ID로 상태 확인)
        elif "id" in result:
            task_id = result["id"]
            status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{task_id}"
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                status_response = requests.get(status_url, headers=headers)
                
                if status_response.status_code != 200:
                    raise Exception(f"상태 확인 실패: {status_response.status_code}")
                
                status_data = status_response.json()
                
                if status_data["status"] == "COMPLETED":
                    return status_data["output"]
                elif status_data["status"] in ["FAILED", "CANCELLED"]:
                    error_msg = status_data.get("error", "알 수 없는 오류")
                    raise Exception(f"작업 {status_data['status']}: {error_msg}")
                
                time.sleep(2)
            
            raise Exception(f"타임아웃: {timeout}초 내에 작업이 완료되지 않았습니다")
        else:
            # 예상치 못한 응답 형식
            return result
    else:
        raise Exception(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")