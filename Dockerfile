# Python 3.11 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# uv 설치 및 의존성 설치
RUN pip install uv
RUN uv sync --frozen

# 애플리케이션 코드 복사
COPY py/ ./py/

# 데이터 디렉토리 생성
RUN mkdir -p /app/data

# 환경변수 설정
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/book_rankings.db

# 포트 노출
EXPOSE 8000

# 기본 명령어 (웹 대시보드 실행)
CMD ["uv", "run", "python", "py/fastapi_dashboard.py"]
