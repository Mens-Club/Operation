CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS fashion_recommendations (
    id BIGSERIAL PRIMARY KEY,
    source_url TEXT UNIQUE,
    embedding vector(512), 
    
    -- 기본 메타데이터
    season TEXT,
    category TEXT,
    sub_category TEXT,
    color TEXT,
    
    -- 추천 정보 (JSON 형식으로 저장)
    answer TEXT,
    recommend JSONB
);
