# Airflow 공식 이미지 사용
FROM apache/airflow:slim-2.11.0rc1-python3.10


# 기본 패키지 업데이트 및 필수 패키지 설치
USER root
WORKDIR /opt/airflow

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사
COPY requirements.txt .

# airflow 사용자로 변경 후 pip install 실행
USER airflow
RUN pip install --no-cache-dir -r requirements.txt

# 다시 root 사용자로 변경하여 entrypoint 복사 및 실행 권한 부여
USER root
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 다시 airflow 사용자로 변경 (Airflow 컨테이너는 airflow 사용자로 실행되어야 함)
USER airflow
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
