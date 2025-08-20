# 📚 도서 순위 모니터링 시스템

30분마다 자동으로 도서 순위 정보를 수집하고 웹에서 시각화할 수 있는 완전한 모니터링 시스템입니다.

## ✨ 주요 기능

- **실시간 데이터 수집**: 교보문고, YES24, 알라딘에서 도서 순위 및 판매 데이터 자동 수집
- **자동 스케줄링**: 30분마다 자동으로 데이터 수집 실행
- **SQLite 데이터베이스**: 모든 데이터를 체계적으로 저장
- **웹 대시보드**: FastAPI 기반의 현대적인 실시간 대시보드
- **인터랙티브 차트**: Chart.js를 활용한 동적 시각화
- **자동 새로고침**: 30초마다 최신 데이터로 자동 업데이트

## 📊 수집 데이터

### 교보문고

- 국내도서 순위
- 컴퓨터/IT 순위

### YES24

- 판매지수
- IT모바일 순위

### 알라딘

- 컴퓨터/모바일 주간 순위
- 대학교재/전문서적 top100 순위
- Sales Point
- 순위 기간 정보

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd /Users/gyus/VSCode/scripts/book_dashboard
uv add httpx beautifulsoup4 schedule fastapi uvicorn pandas
```

### 2. 데이터 수집 (한 번)

```bash
# 데이터를 한 번만 수집
uv run python book_ranking_monitor.py --once
```

### 3. 웹 대시보드 실행

```bash
# FastAPI 대시보드 실행
uv run python fastapi_dashboard.py
```

웹 브라우저에서 `http://localhost:8000` 접속

### 4. 자동 모니터링 시작

```bash
# 30분마다 자동 데이터 수집 (백그라운드 실행)
nohup uv run python book_ranking_monitor.py &
```

## 📋 명령어 참고

### book_ranking_monitor.py

```bash
# 한 번만 데이터 수집
uv run python book_ranking_monitor.py --once

# 30분마다 자동 수집 (무한 실행)
uv run python book_ranking_monitor.py

# 데이터베이스 통계 확인
uv run python book_ranking_monitor.py --stats

# 사용자 지정 데이터베이스 경로
uv run python book_ranking_monitor.py --db custom_rankings.db --once
```

### fastapi_dashboard.py

```bash
# 웹 대시보드 실행 (기본 포트 8000)
uv run python fastapi_dashboard.py

# 다른 포트로 실행하려면 코드 수정 필요
```

## 🖥️ 웹 대시보드 기능

### 메인 화면

- 총 레코드 수
- 최근 24시간 데이터 수
- 실시간 데이터 상태
- 현재 시간 (실시간 업데이트)

### 최신 순위 현황

- 각 서점별 최신 순위 및 판매 데이터
- 색상별로 구분된 서점 카드

### 차트 기능

1. **순위 변화 추이**

   - 모든 순위 데이터의 시간별 변화
   - y축 반전 (낮은 순위가 위쪽)
   - 다중 라인 차트

2. **판매지수 및 포인트 변화**
   - YES24 판매지수 (왼쪽 y축)
   - 알라딘 Sales Point (오른쪽 y축)
   - 이중 y축 차트

### 컨트롤

- **시간 범위**: 최근 6시간 ~ 7일 선택 가능
- **수동 새로고침**: 🔄 버튼으로 즉시 업데이트
- **자동 새로고침**: 30초마다 자동 업데이트 (토글 가능)

## 📁 파일 구조

```
book_dashboard/
├── summary_yozm_ai_agent_info.py  # 원본 스크래퍼
├── book_ranking_monitor.py        # 모니터링 시스템 (스케줄러 + DB)
├── fastapi_dashboard.py           # FastAPI 웹 대시보드
├── README.md                      # 사용법 가이드 (이 파일)
├── DOCKER_README.md               # Docker 상세 가이드
├── Dockerfile                     # Docker 이미지 정의
├── docker-compose.yml             # Docker 서비스 구성
├── .dockerignore                  # Docker 빌드 제외 파일
├── pyproject.toml                 # Python 의존성
└── uv.lock                        # 의존성 락 파일

data/
└── book_rankings.db               # SQLite 데이터베이스 파일
```

## 🗄️ 데이터베이스 스키마

```sql
CREATE TABLE book_rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    scraping_date TEXT NOT NULL,

    -- 교보문고 데이터
    kyobo_domestic_rank INTEGER,
    kyobo_it_rank INTEGER,
    kyobo_error TEXT,

    -- YES24 데이터
    yes24_sales_index INTEGER,
    yes24_it_mobile_rank INTEGER,
    yes24_error TEXT,

    -- 알라딘 데이터
    aladin_computer_weekly_rank INTEGER,
    aladin_textbook_rank INTEGER,
    aladin_sales_point INTEGER,
    aladin_rank_period TEXT,
    aladin_error TEXT,

    -- 메타데이터
    raw_data TEXT,  -- JSON 형태 원본 데이터
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 설정 및 커스터마이징

### URL 변경

`book_ranking_monitor.py`에서 모니터링할 도서의 URL을 변경할 수 있습니다:

```python
self.urls = {
    "kyobobook": "https://product.kyobobook.co.kr/detail/S000217241525",
    "yes24": "https://www.yes24.com/product/goods/150701473",
    "aladin": "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=369431124",
}
```

### 수집 주기 변경

30분 대신 다른 주기로 변경하려면:

```python
# 10분마다
schedule.every(10).minutes.do(self.collect_data)

# 1시간마다
schedule.every().hour.do(self.collect_data)

# 매일 특정 시간
schedule.every().day.at("09:00").do(self.collect_data)
```

### 대시보드 포트 변경

`fastapi_dashboard.py` 마지막 줄:

```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # 8000 → 8080
```

## 🚨 문제 해결

### 데이터가 수집되지 않는 경우

1. 인터넷 연결 확인
2. 웹사이트 접근 가능성 확인
3. URL이 여전히 유효한지 확인

### 대시보드가 로드되지 않는 경우

1. FastAPI 서버가 실행 중인지 확인
2. 포트 충돌 확인 (다른 포트 사용)
3. 방화벽 설정 확인

### 데이터베이스 오류

```bash
# 데이터베이스 파일 권한 확인
ls -la book_rankings.db

# 새 데이터베이스로 다시 시작
rm book_rankings.db
uv run book_ranking_monitor.py --once
```

## 📈 API 엔드포인트

FastAPI는 자동 API 문서를 제공합니다:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 주요 API

- `GET /`: 메인 대시보드
- `GET /api/stats`: 통계 정보
- `GET /api/latest`: 최신 데이터
- `GET /api/chart-data?hours=24`: 차트 데이터

## 🐳 Docker 배포 (권장)

### 빠른 시작

```bash
# 1. 초기 데이터 수집
docker-compose --profile init up book-init

# 2. 전체 시스템 실행
docker-compose up -d

# 3. 웹 접속
open http://localhost:8000
```

### Docker 서비스 구성

- **book-dashboard**: FastAPI 웹 대시보드 (포트 8000)
- **book-monitor**: 30분마다 자동 데이터 수집
- **book-init**: 최초 1회 데이터 수집

### SQLite 볼륨 마운트

```yaml
volumes:
  - ./data:/app/data # 데이터 영속성 보장
```

데이터베이스 파일이 호스트의 `data/book_rankings.db`에 저장되어 컨테이너 재시작 후에도 보존됩니다.

### Docker 명령어

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f book-monitor
docker-compose logs -f book-dashboard

# 서비스 중지
docker-compose down

# 수동 데이터 수집
docker-compose exec book-monitor uv run python py/book_ranking_monitor.py --once

# 통계 확인
docker-compose exec book-monitor uv run python py/book_ranking_monitor.py --stats
```

자세한 Docker 사용법은 `DOCKER_README.md`를 참고하세요.

## 🔄 기존 방식 배포

### PM2 사용

```bash
# PM2 설치
npm install -g pm2

# 자동 모니터링 시작
pm2 start "uv run py/book_ranking_monitor.py" --name "book-monitor"

# 웹 대시보드 시작
pm2 start "uv run python py/fastapi_dashboard.py" --name "book-dashboard"

# 상태 확인
pm2 status

# 로그 확인
pm2 logs book-monitor
pm2 logs book-dashboard
```

### systemd 서비스 (Linux)

```bash
# /etc/systemd/system/book-monitor.service 파일 생성
[Unit]
Description=Book Ranking Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/Users/gyus/VSCode/scripts
ExecStart=uv run py/book_ranking_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target

# 서비스 시작
sudo systemctl enable book-monitor
sudo systemctl start book-monitor
```

## 📊 모니터링 예제

### 데이터 수집 상황 확인

```bash
# 실시간 로그 모니터링
tail -f nohup.out

# 데이터베이스 통계
uv run book_ranking_monitor.py --stats
```

### 백업

```bash
# 데이터베이스 백업
cp book_rankings.db backups/book_rankings_$(date +%Y%m%d_%H%M%S).db

# 정기 백업 스크립트
echo "0 0 * * * cp /path/to/book_rankings.db /path/to/backups/book_rankings_\$(date +\%Y\%m\%d).db" | crontab -
```

## 🤝 기여 및 개발

### 새로운 서점 추가

1. `summary_yozm_ai_agent_info.py`에 스크래핑 메서드 추가
2. `book_ranking_monitor.py`에 데이터베이스 컬럼 추가
3. `fastapi_dashboard.py`에 시각화 코드 추가

### 알림 기능 추가

- 순위 변화 시 슬랙/디스코드 알림
- 이메일 리포트 기능
- 모바일 푸시 알림

## 📝 라이센스

MIT License - 자유롭게 사용 및 수정 가능합니다.

---

**🎯 목표**: 도서 순위 변화를 지속적으로 모니터링하여 마케팅 전략 수립에 도움을 주는 것

**⚡ 성능**: 30분마다 데이터 수집, 실시간 웹 대시보드 제공

**🔧 유지보수**: 로그 모니터링, 정기 백업, 오류 처리 포함
