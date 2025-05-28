# MLOps Platform

> `Men's CLUB` `머신러닝/웹` 운영을 위한 오퍼레이션 저장소 

## Architecture Overview

이 프로젝트는 Docker Compose를 기반으로 한 마이크로서비스 아키텍처의 MLOps 플랫폼입니다.

### Core Services

| Service | Description | Port | 
|---------|-------------|------|
| **Airflow** | 워크플로우 오케스트레이션 | 8080 |
| **Database** | MySQL/PostgreSQL 데이터베이스 | 3306/5432 |
| **MLflow** | ML 모델 관리 및 실험 추적 | 5000 |
| **Monitoring** | Prometheus + Grafana | 9090, 3000 |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | 9200, 5601 |

### Proxy Services

- **database.proxy**: Elasticsearch 프록시
- **model.proxy**: 모델 서빙 API 프록시  
- **monitoring.proxy**: 모니터링 서비스 프록시

## Project Structure

```bash 
project_root/
├── airflow/                     
#  워크플로우 오케스트레이션
│   ├── dags/                   
# Airflow DAG 정의
│   │   ├── evaluation.py       
# 모델 평가 파이프라인
│   │   ├── fill_data.py        
# 데이터 적재 파이프라인
│   │   ├── train.py            
# 모델 훈련 파이프라인
│   │   └── config/             
# 설정 및 유틸리티
│   └── module/                 
# 비즈니스 로직 모듈
│       ├── database_fill_chain.py
│       ├── train_piepeline.py
│       └── validating_model.py
├── database/                   
#  데이터베이스 서비스
├── database.proxy/             
#  Elasticsearch 프록시
├── logging/                    
#  로깅 스택 (ELK)
│   ├── kibana/
│   └── logstash/
├── mlflow/                     
#  ML 실험 관리
├── model.proxy/                
#  모델 서빙 프록시
├── monitoring/                 
#  모니터링 스택
│   ├── grafana/
│   └── prometheus/
└── monitoring.proxy/           
# 모니터링 프록시
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### 1. Clone Repository

```bash
git clone https://github.com/Mens-Club/Operation.git
cd Operation
```

### 2. Environment Setup

각 서비스 디렉토리의 `.env` 파일을 설정하세요:

```bash
# Copy example environment files
cp airflow/.env.example airflow/.env
cp database/.env.example database/.env
cp monitoring/.env.example monitoring/.env
# ... other services
```

### 3. Start Services

```bash
# Start all services
docker-compose -f database/mensclub.main.docker-compose.yaml up -d
docker-compose -f airflow/airflow.docker-compose.yaml up -d
docker-compose -f monitoring/monitoring.docker-compose.yaml up -d
docker-compose -f logging/logging.docker-compose.yaml up -d
docker-compose -f mlflow/validation.docker-compose.yaml up -d

# Or use the startup script
./scripts/start-all.sh
```

### 4. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow | http://localhost:8080 | admin/admin |
| MLflow | http://localhost:5000 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Kibana | http://localhost:5601 | - |

## 📋 Data Pipelines

### Airflow DAGs

1. **fill_data.py**: 데이터 수집 및 적재
   - 외부 소스에서 데이터 수집
   - 데이터 검증 및 전처리
   - 데이터베이스 적재

2. **train.py**: 모델 훈련 파이프라인
   - 훈련 데이터 준비
   - 모델 훈련 실행
   - MLflow에 모델 등록

3. **evaluation.py**: 모델 평가 파이프라인
   - 모델 성능 평가
   - A/B 테스트 결과 분석
   - 모델 승격/배포 결정

### Pipeline Schedule

- **Data Fill**: Daily at 2:00 AM
- **Model Training**: Weekly (Monday 3:00 AM)
- **Model Evaluation**: Daily at 6:00 AM

## Configuration

### Database Configuration

```python
# airflow/dags/config/connection.py
DATABASE_CONFIG = {
    'host': 'database',
    'port': 3306,
    'database': 'mlops',
    'user': 'admin',
    'password': 'password'
}
```

### Model Training Configuration

1. 모델 `Output` 값에 특정 단어 언급 비율 
    - `계절`, `카테고리` 등이 얼만큼 등장 했는지에 대해 2개의 지표로 성능 확인 

2. `both_requirements_rate`로 2가지 단어가 모두 나왔는지 여부 검증 



## Monitoring & Logging

### Prometheus Metrics

- Airflow task success/failure rates
- Model performance metrics
- System resource usage
- Database connection status

### Grafana Dashboards

- **ML Pipeline Dashboard**: DAG 실행 상태 모니터링
- **Model Performance Dashboard**: 모델 성능 추적
- **System Health Dashboard**: 인프라 상태 모니터링

### ELK Stack

- **Elasticsearch**: 로그 저장소
- **Logstash**: 로그 수집 및 처리
- **Kibana**: 로그 시각화 및 분석

## 🔍 Development

### Local Development

```bash
# Start local Airflow for development
docker-compose -f airflow/local.airflow.docker-compose.yaml up -d

# Access Airflow locally
http://localhost:8080
```

### Adding New DAGs

1. `airflow/dags/` 디렉토리에 새 DAG 파일 생성
2. 필요한 설정을 `airflow/dags/config/`에 추가
3. 비즈니스 로직을 `airflow/module/`에 구현

-------
## `MCP`를 활용한 데이터베이스, 모니터링 활용 


`MySQL-MCP`

![image](https://github.com/user-attachments/assets/3a99a6a7-3409-417a-8308-2c462553f8e7)

- `MySQL-MCP`를 활용하여 `Claude`와 연결
- 주요 인사이트로 사용자 업로드 데이터와 로그인 기록, 테이블 정보등을 조회
- 주요 트랜잭션을 자연어로 처리 가능하게끔 제공


`ELK-Stack-MCP : Elastic Search`

![image](https://github.com/user-attachments/assets/6e14e9cc-0348-41bb-acf6-5d5bf504571b)

- `ELK-Stack`이 연동된 `Elastic Search-MCP`를 `Claude`와 연결
- 기존에 서버에서 발생되었던 로그들을 모두 조회하며 사용자에게 필요한 인사이트 제공 (주요 에러로깅을 종합해줌)


## 🏷️ Tags

`mlops` `airflow` `docker` `machine-learning` `data-pipeline` `monitoring` `elasticsearch` `grafana` `prometheus` `mlflow`
