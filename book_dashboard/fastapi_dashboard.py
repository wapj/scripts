"""
FastAPI 기반 도서 순위 모니터링 대시보드
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 로거 설정
logging.basicConfig(
    level=logging.INFO, format="%(asc time)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="도서 순위 모니터링 대시보드", version="1.0.0")

# 정적 파일 및 템플릿 설정
templates = Jinja2Templates(directory="templates")


class BookRankingAPI:
    def __init__(self, db_path=None):
        if db_path is None:
            # 환경 변수에서 DB 경로 가져오기, 없으면 기본값 사용
            import os

            self.db_path = os.getenv("DB_PATH", "data/book_rankings.db")
        else:
            self.db_path = db_path
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        # 데이터 디렉토리 생성
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            scraping_date TEXT NOT NULL,
            kyobo_domestic_rank INTEGER,
            kyobo_it_rank INTEGER,
            kyobo_error TEXT,
            yes24_sales_index INTEGER,
            yes24_it_mobile_rank INTEGER,
            yes24_error TEXT,
            aladin_computer_weekly_rank INTEGER,
            aladin_textbook_rank INTEGER,
            aladin_sales_point INTEGER,
            aladin_rank_period TEXT,
            aladin_error TEXT,
            raw_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()
        logging.info(f"FastAPI: 데이터베이스 초기화 확인 완료: {self.db_path}")

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_stats(self):
        """통계 정보"""
        conn = self.get_connection()

        try:
            # 총 레코드 수
            total_records = conn.execute(
                "SELECT COUNT(*) FROM book_rankings"
            ).fetchone()[0]

            # 최신/최오래된 데이터
            result = conn.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM book_rankings"
            ).fetchone()
            oldest, newest = result

            # 최근 24시간 데이터 수
            since_24h = datetime.now() - timedelta(hours=24)
            recent_24h = conn.execute(
                "SELECT COUNT(*) FROM book_rankings WHERE timestamp >= ?", (since_24h,)
            ).fetchone()[0]

            return {
                "total_records": total_records,
                "oldest_data": oldest,
                "newest_data": newest,
                "recent_24h": recent_24h,
            }
        finally:
            conn.close()

    def get_latest_data(self):
        """최신 데이터"""
        conn = self.get_connection()

        try:
            query = """
            SELECT 
                kyobo_domestic_rank, kyobo_it_rank,
                yes24_sales_index, yes24_it_mobile_rank,
                aladin_computer_weekly_rank, aladin_textbook_rank, aladin_sales_point,
                timestamp
            FROM book_rankings 
            ORDER BY timestamp DESC 
            LIMIT 1
            """

            result = conn.execute(query).fetchone()

            if result:
                return {
                    "kyobo_domestic_rank": result[0],
                    "kyobo_it_rank": result[1],
                    "yes24_sales_index": result[2],
                    "yes24_it_mobile_rank": result[3],
                    "aladin_computer_weekly_rank": result[4],
                    "aladin_textbook_rank": result[5],
                    "aladin_sales_point": result[6],
                    "timestamp": result[7],
                }
            return None
        finally:
            conn.close()

    def get_chart_data(self, hours=24):
        """차트 데이터"""
        conn = self.get_connection()

        try:
            since = datetime.now() - timedelta(hours=hours)

            query = """
            SELECT 
                timestamp,
                kyobo_domestic_rank, kyobo_it_rank,
                yes24_sales_index, yes24_it_mobile_rank,
                aladin_computer_weekly_rank, aladin_textbook_rank, aladin_sales_point
            FROM book_rankings 
            WHERE timestamp >= ? 
            ORDER BY timestamp
            """

            results = conn.execute(query, (since,)).fetchall()

            data = {
                "timestamps": [],
                "kyobo_domestic_rank": [],
                "kyobo_it_rank": [],
                "yes24_sales_index": [],
                "yes24_it_mobile_rank": [],
                "aladin_computer_weekly_rank": [],
                "aladin_textbook_rank": [],
                "aladin_sales_point": [],
            }

            for row in results:
                if row[0]:  # timestamp가 있는 경우만
                    timestamp_str = pd.to_datetime(row[0]).strftime("%Y-%m-%d %H:%M")
                    data["timestamps"].append(timestamp_str)
                    data["kyobo_domestic_rank"].append(
                        row[1] if row[1] is not None else None
                    )
                    data["kyobo_it_rank"].append(row[2] if row[2] is not None else None)
                    data["yes24_sales_index"].append(
                        row[3] if row[3] is not None else None
                    )
                    data["yes24_it_mobile_rank"].append(
                        row[4] if row[4] is not None else None
                    )
                    data["aladin_computer_weekly_rank"].append(
                        row[5] if row[5] is not None else None
                    )
                    data["aladin_textbook_rank"].append(
                        row[6] if row[6] is not None else None
                    )
                    data["aladin_sales_point"].append(
                        row[7] if row[7] is not None else None
                    )

            return data
        finally:
            conn.close()


# API 인스턴스
api = BookRankingAPI()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """메인 대시보드 페이지"""
    logging.info("메인 대시보드 요청")
    try:
        stats = api.get_stats()
        latest = api.get_latest_data()

        # HTML 직접 반환 (템플릿 파일 없이)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📚 도서 순위 모니터링 대시보드</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .stats-container {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }}
                .latest-data {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .bookstore-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .bookstore-title {{
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #eee;
                }}
                .bookstore-kyobo {{ border-left: 4px solid #ff6b6b; }}
                .bookstore-yes24 {{ border-left: 4px solid #4ecdc4; }}
                .bookstore-aladin {{ border-left: 4px solid #45b7d1; }}
                .chart-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .controls {{
                    background: white;
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .controls select, .controls button {{
                    padding: 8px 15px;
                    margin: 5px;
                    border-radius: 5px;
                    border: 1px solid #ddd;
                }}
                .controls button {{
                    background-color: #667eea;
                    color: white;
                    cursor: pointer;
                }}
                .controls button:hover {{
                    background-color: #5a6fd8;
                }}
                .last-update {{
                    text-align: center;
                    color: #666;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📚 도서 순위 모니터링 대시보드</h1>
                <p>실시간 도서 순위 및 판매 데이터</p>
            </div>

            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-value">{stats.get("total_records", 0)}</div>
                    <div>총 레코드</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get("recent_24h", 0)}</div>
                    <div>최근 24시간</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{"실시간" if latest else "없음"}</div>
                    <div>데이터 상태</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="current-time"></div>
                    <div>현재 시간</div>
                </div>
            </div>

            {
            f'''
            <div class="latest-data">
                <div class="bookstore-card bookstore-kyobo">
                    <div class="bookstore-title">📘 <a href="https://product.kyobobook.co.kr/detail/S000217241525">교보문고</a></div>
                    <div><strong>국내도서 순위:</strong> {latest.get("kyobo_domestic_rank", "N/A")}위</div>
                    <div><strong>컴퓨터/IT 순위:</strong> {latest.get("kyobo_it_rank", "N/A")}위</div>
                </div>
                <div class="bookstore-card bookstore-yes24">
                    <div class="bookstore-title">📗 <a href="https://www.yes24.com/product/goods/150701473">YES24</a></div>
                    <div><strong>판매지수:</strong> {latest.get("yes24_sales_index", "N/A")}</div>
                    <div><strong>IT모바일 순위:</strong> {latest.get("yes24_it_mobile_rank", "N/A")}위</div>
                </div>
                <div class="bookstore-card bookstore-aladin">
                    <div class="bookstore-title">📙 <a href="https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=369431124">알라딘</a></div>
                    <div><strong>컴퓨터/모바일 주간:</strong> {latest.get("aladin_computer_weekly_rank", "N/A")}위</div>
                    <div><strong>대학교재 순위:</strong> {latest.get("aladin_textbook_rank", "N/A")}위</div>
                    <div><strong>Sales Point:</strong> {latest.get("aladin_sales_point", "N/A")}</div>
                </div>
            </div>
            '''
            if latest
            else '<div class="latest-data"><div class="bookstore-card"><h3>데이터가 없습니다</h3><p>먼저 데이터를 수집해주세요.</p></div></div>'
        }

            <div class="controls">
                <label for="timeRange">시간 범위:</label>
                <select id="timeRange" onchange="updateCharts()">
                    <option value="6">최근 6시간</option>
                    <option value="12">최근 12시간</option>
                    <option value="24" selected>최근 24시간</option>
                    <option value="48">최근 48시간</option>
                    <option value="168">최근 7일</option>
                </select>
                <button onclick="updateCharts()">🔄 새로고침</button>
                <button onclick="toggleAutoRefresh()" id="autoRefreshBtn">⏸️ 자동새로고침 중지</button>
            </div>

            <div class="chart-container">
                <h3>📈 순위 변화 추이 (낮을수록 좋음)</h3>
                <canvas id="rankChart"></canvas>
            </div>

            <div class="chart-container">
                <h3>💰 판매지수 및 포인트 변화</h3>
                <canvas id="salesChart"></canvas>
            </div>

            <div class="last-update">
                마지막 업데이트: <span id="lastUpdate"></span>
            </div>

            <script>
                let rankChart, salesChart;
                let autoRefreshInterval;
                let isAutoRefresh = true;

                // 차트 초기화
                function initCharts() {{
                    const rankCtx = document.getElementById('rankChart').getContext('2d');
                    const salesCtx = document.getElementById('salesChart').getContext('2d');

                    rankChart = new Chart(rankCtx, {{
                        type: 'line',
                        data: {{
                            labels: [],
                            datasets: [
                                {{
                                    label: '교보문고 국내도서',
                                    data: [],
                                    borderColor: '#ff6b6b',
                                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                                    tension: 0.4
                                }},
                                {{
                                    label: '교보문고 IT',
                                    data: [],
                                    borderColor: '#ffa500',
                                    backgroundColor: 'rgba(255, 165, 0, 0.1)',
                                    tension: 0.4
                                }},
                                {{
                                    label: 'YES24 IT모바일',
                                    data: [],
                                    borderColor: '#4ecdc4',
                                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                                    tension: 0.4
                                }},
                                {{
                                    label: '알라딘 컴퓨터/모바일',
                                    data: [],
                                    borderColor: '#45b7d1',
                                    backgroundColor: 'rgba(69, 183, 209, 0.1)',
                                    tension: 0.4
                                }},
                                {{
                                    label: '알라딘 대학교재',
                                    data: [],
                                    borderColor: '#96ceb4',
                                    backgroundColor: 'rgba(150, 206, 180, 0.1)',
                                    tension: 0.4
                                }}
                            ]
                        }},
                        options: {{
                            responsive: true,
                            scales: {{
                                y: {{
                                    reverse: true,
                                    beginAtZero: false
                                }}
                            }}
                        }}
                    }});

                    salesChart = new Chart(salesCtx, {{
                        type: 'line',
                        data: {{
                            labels: [],
                            datasets: [
                                {{
                                    label: 'YES24 판매지수',
                                    data: [],
                                    borderColor: '#4ecdc4',
                                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                                    tension: 0.4,
                                    yAxisID: 'y'
                                }},
                                {{
                                    label: '알라딘 Sales Point',
                                    data: [],
                                    borderColor: '#45b7d1',
                                    backgroundColor: 'rgba(69, 183, 209, 0.1)',
                                    tension: 0.4,
                                    yAxisID: 'y1'
                                }}
                            ]
                        }},
                        options: {{
                            responsive: true,
                            interaction: {{
                                mode: 'index',
                                intersect: false,
                            }},
                            scales: {{
                                y: {{
                                    type: 'linear',
                                    display: true,
                                    position: 'left',
                                }},
                                y1: {{
                                    type: 'linear',
                                    display: true,
                                    position: 'right',
                                    grid: {{
                                        drawOnChartArea: false,
                                    }},
                                }}
                            }}
                        }}
                    }});
                }}

                // 차트 업데이트
                async function updateCharts() {{
                    const hours = document.getElementById('timeRange').value;
                    
                    try {{
                        const response = await fetch(`/api/chart-data?hours=${{hours}}`);
                        const data = await response.json();

                        // 순위 차트 업데이트
                        rankChart.data.labels = data.timestamps;
                        rankChart.data.datasets[0].data = data.kyobo_domestic_rank;
                        rankChart.data.datasets[1].data = data.kyobo_it_rank;
                        rankChart.data.datasets[2].data = data.yes24_it_mobile_rank;
                        rankChart.data.datasets[3].data = data.aladin_computer_weekly_rank;
                        rankChart.data.datasets[4].data = data.aladin_textbook_rank;
                        rankChart.update();

                        // 판매지수 차트 업데이트
                        salesChart.data.labels = data.timestamps;
                        salesChart.data.datasets[0].data = data.yes24_sales_index;
                        salesChart.data.datasets[1].data = data.aladin_sales_point;
                        salesChart.update();

                        document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
                    }} catch (error) {{
                        console.error('차트 데이터 업데이트 실패:', error);
                    }}
                }}

                // 자동 새로고침 토글
                function toggleAutoRefresh() {{
                    const btn = document.getElementById('autoRefreshBtn');
                    if (isAutoRefresh) {{
                        clearInterval(autoRefreshInterval);
                        btn.textContent = '▶️ 자동새로고침 시작';
                        isAutoRefresh = false;
                    }} else {{
                        autoRefreshInterval = setInterval(updateCharts, 30000); // 30초마다
                        btn.textContent = '⏸️ 자동새로고침 중지';
                        isAutoRefresh = true;
                    }}
                }}

                // 현재 시간 업데이트
                function updateCurrentTime() {{
                    document.getElementById('current-time').textContent = new Date().toLocaleTimeString();
                }}

                // 초기화
                document.addEventListener('DOMContentLoaded', function() {{
                    initCharts();
                    updateCharts();
                    updateCurrentTime();
                    setInterval(updateCurrentTime, 1000);
                    
                    // 자동 새로고침 시작 (30초마다)
                    autoRefreshInterval = setInterval(updateCharts, 30000);
                }});
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        logging.error(f"대시보드 로딩 오류: {e}", exc_info=True)
        error_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>오류</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .error {{ background: #ffe6e6; border: 1px solid #ff0000; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>오류가 발생했습니다</h2>
                <p>{str(e)}</p>
                <p>먼저 <code>uv run book_ranking_monitor.py --once</code> 명령으로 데이터를 수집해주세요.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@app.get("/api/stats")
async def get_stats():
    """통계 API"""
    logging.info("API 요청: /api/stats")
    try:
        stats = api.get_stats()
        return stats
    except Exception as e:
        logging.error(f"/api/stats 처리 오류: {e}", exc_info=True)
        return {"error": str(e)}


@app.get("/api/latest")
async def get_latest():
    """최신 데이터 API"""
    logging.info("API 요청: /api/latest")
    try:
        latest = api.get_latest_data()
        return latest
    except Exception as e:
        logging.error(f"/api/latest 처리 오류: {e}", exc_info=True)
        return {"error": str(e)}


@app.get("/api/chart-data")
async def get_chart_data(hours: Optional[int] = 24):
    """차트 데이터 API"""
    logging.info(f"API 요청: /api/chart-data?hours={hours}")
    try:
        data = api.get_chart_data(hours)
        return data
    except Exception as e:
        logging.error(f"/api/chart-data 처리 오류: {e}", exc_info=True)
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
