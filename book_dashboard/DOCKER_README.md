# 🐳 도서 순위 모니터링 시스템 - Docker 버전

도커를 사용해서 쉽게 배포하고 실행할 수 있는 완전한 도서 순위 모니터링 시스템입니다.

## 📁 프로젝트 구조

```
/Users/gyus/VSCode/scripts/book_dashboard/
├── Dockerfile              # 도커 이미지 정의
├── docker-compose.yml      # 서비스 구성
├── .dockerignore          # 도커 빌드 제외 파일
├── data/                  # SQLite DB 저장 (volume mount)
├── summary_yozm_ai_agent_info.py  # 원본 스크래퍼
├── book_ranking_monitor.py        # 모니터링 시스템
├── fastapi_dashboard.py           # 웹 대시보드
├── README.md                      # 상세 가이드
├── DOCKER_README.md               # Docker 상세 가이드
├── pyproject.toml         # Python 의존성
└── uv.lock               # 의존성 락 파일
```

## 🚀 빠른 시작

### 1. Docker 설치 및 실행

```bash
# Docker Desktop 설치 후 실행 확인
docker --version
docker-compose --version
```

### 2. 초기 데이터 수집

```bash
cd /Users/gyus/VSCode/scripts/book_dashboard

# 초기 데이터 수집 (한 번만 실행)
docker-compose --profile init up book-init

# 또는 별도로 실행
docker-compose run --rm book-init
```

### 3. 전체 시스템 실행

```bash
# 웹 대시보드 + 자동 모니터링 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 웹 접속

브라우저에서 `http://localhost:8000` 접속

### 5. 시스템 중지

```bash
# 모든 서비스 중지
docker-compose down

# 볼륨까지 삭제하고 싶은 경우
docker-compose down -v
```

## 🎯 Docker Compose 서비스

### book-dashboard (웹 대시보드)

- **포트**: 8000
- **기능**: FastAPI 기반 실시간 웹 대시보드
- **볼륨**: `./data:/app/data` (SQLite DB 영속성)
- **환경변수**: `DB_PATH=/app/data/book_rankings.db`

### book-monitor (데이터 수집)

- **기능**: 30분마다 자동 데이터 수집
- **볼륨**: `./data:/app/data` (SQLite DB 공유)
- **환경변수**: `DB_PATH=/app/data/book_rankings.db`
- **재시작**: `unless-stopped`

### book-init (초기 설정)

- **기능**: 최초 1회 데이터 수집
- **프로파일**: `init` (선택적 실행)
- **실행**: `docker-compose --profile init up book-init`

## 📊 SQLite 볼륨 마운트

### 데이터 영속성 보장

```yaml
volumes:
  - ./data:/app/data # 호스트의 ./data 디렉토리를 컨테이너의 /app/data로 마운트
```

### 데이터 위치

- **호스트**: `/Users/gyus/VSCode/scripts/data/book_rankings.db`
- **컨테이너**: `/app/data/book_rankings.db`

### 장점

✅ 컨테이너 재시작해도 데이터 보존  
✅ 호스트에서 직접 DB 파일 접근 가능  
✅ 백업 및 복원 용이  
✅ 다른 도구로 DB 분석 가능

## 🔧 고급 사용법

### 개별 서비스 실행

```bash
# 웹 대시보드만 실행
docker-compose up -d book-dashboard

# 모니터링만 실행
docker-compose up -d book-monitor

# 특정 서비스 로그 확인
docker-compose logs -f book-dashboard
docker-compose logs -f book-monitor
```

### 수동 데이터 수집

```bash
# 컨테이너 내에서 한 번만 실행
docker-compose exec book-monitor uv run python book_ranking_monitor.py --once

# 통계 확인
docker-compose exec book-monitor uv run python book_ranking_monitor.py --stats
```

### 데이터베이스 접근

```bash
# 호스트에서 직접 접근
sqlite3 data/book_rankings.db "SELECT COUNT(*) FROM book_rankings;"

# 컨테이너를 통해 접근
docker-compose exec book-dashboard sqlite3 /app/data/book_rankings.db
```

## 🛠️ 커스터마이징

### 1. 수집 주기 변경

`book_ranking_monitor.py` 수정 후 이미지 재빌드:

```python
# 10분마다
schedule.every(10).minutes.do(self.collect_data)

# 1시간마다
schedule.every().hour.do(self.collect_data)
```

```bash
docker-compose build
docker-compose up -d
```

### 2. 포트 변경

`docker-compose.yml` 수정:

```yaml
book-dashboard:
  ports:
    - "8080:8000" # 호스트 포트 8080으로 변경
```

### 3. 다른 도서 모니터링

`book_ranking_monitor.py`의 URL 변경 후 재빌드:

```python
self.urls = {
    "kyobobook": "https://product.kyobobook.co.kr/detail/YOUR_BOOK_ID",
    "yes24": "https://www.yes24.com/product/goods/YOUR_BOOK_ID",
    "aladin": "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=YOUR_BOOK_ID",
}
```

## 📝 환경 변수

### 사용 가능한 환경 변수

```bash
# 데이터베이스 경로
DB_PATH=/app/data/book_rankings.db

# Python 경로
PYTHONPATH=/app
```

### docker-compose.yml에서 환경 변수 추가

```yaml
environment:
  - DB_PATH=/app/data/book_rankings.db
  - CUSTOM_SETTING=value
```

## 🚨 문제 해결

### Docker 데몬 실행 확인

```bash
# Docker Desktop 실행 여부 확인
docker info

# Docker 서비스 시작 (Linux)
sudo systemctl start docker
```

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000

# 다른 포트 사용
docker-compose up -d --env PORT=8080
```

### 권한 문제

```bash
# data 디렉토리 권한 확인
ls -la data/

# 권한 수정 (필요시)
chmod 755 data/
```

### 빌드 실패

```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 이미지 삭제 후 재빌드
docker-compose down --rmi all
docker-compose build
```

### 볼륨 문제

```bash
# 볼륨 상태 확인
docker volume ls

# 볼륨 삭제 및 재생성
docker-compose down -v
docker-compose up -d
```

## 📈 모니터링 및 로그

### 실시간 로그 모니터링

```bash
# 전체 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f book-monitor
docker-compose logs -f book-dashboard

# 최근 100줄만
docker-compose logs --tail=100 -f
```

### 시스템 리소스 모니터링

```bash
# 컨테이너 상태 확인
docker-compose ps

# 리소스 사용량 확인
docker stats

# 컨테이너 내부 접근
docker-compose exec book-dashboard bash
```

## 🔄 운영 환경 배포

### 프로덕션 설정

```yaml
# docker-compose.prod.yml
version: "3.8"
services:
  book-dashboard:
    build: .
    ports:
      - "80:8000"
    volumes:
      - /var/lib/book-rankings:/app/data
    environment:
      - DB_PATH=/app/data/book_rankings.db
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

```bash
# 프로덕션 실행
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 백업 및 복원

```bash
# 백업
tar -czf book_rankings_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/

# 복원
tar -xzf book_rankings_backup_20250820_223000.tar.gz
```

### 업데이트

```bash
# 코드 업데이트 후
git pull
docker-compose build
docker-compose up -d
```

## 🔐 보안 고려사항

### 네트워크 보안

```yaml
# 외부 접근 제한
book-monitor:
  networks:
    - internal

networks:
  internal:
    driver: bridge
    internal: true
```

### 데이터 보안

```bash
# 데이터 디렉토리 권한 제한
chmod 700 data/
chown $(id -u):$(id -g) data/
```

## 📊 성능 최적화

### 리소스 제한

```yaml
deploy:
  resources:
    limits:
      cpus: "0.5"
      memory: 256M
    reservations:
      cpus: "0.1"
      memory: 128M
```

### 로그 관리

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🎉 완성된 기능

✅ **자동 데이터 수집**: 30분마다 3개 서점에서 순위 정보 수집  
✅ **실시간 대시보드**: 인터랙티브 차트와 통계  
✅ **데이터 영속성**: SQLite 볼륨 마운트로 데이터 보존  
✅ **컨테이너화**: Docker로 간편한 배포 및 관리  
✅ **환경 변수 지원**: 설정 커스터마이징 가능  
✅ **자동 재시작**: 서비스 안정성 보장  
✅ **로그 관리**: 체계적인 모니터링

---

**🎯 사용법 요약**:

1. `docker-compose --profile init up book-init` (초기 데이터 수집)
2. `docker-compose up -d` (전체 시스템 실행)
3. `http://localhost:8000` 접속
4. 30분마다 자동으로 새로운 데이터 수집 및 대시보드 업데이트!
