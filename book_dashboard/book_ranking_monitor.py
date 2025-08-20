"""
도서 순위 모니터링 시스템
30분마다 도서 순위 정보를 수집하고 데이터베이스에 저장
"""

import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta

import schedule

# 로거 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 현재 스크래퍼 임포트
from summary_yozm_ai_agent_info import BookRankingScraper


class BookRankingMonitor:
    def __init__(self, db_path=None):
        """모니터링 시스템 초기화"""
        if db_path is None:
            # 환경 변수에서 DB 경로 가져오기, 없으면 기본값 사용
            import os

            self.db_path = os.getenv("DB_PATH", "book_rankings.db")
        else:
            self.db_path = db_path
        self.scraper = BookRankingScraper()
        self.urls = {
            "kyobobook": "https://product.kyobobook.co.kr/detail/S000217241525",
            "yes24": "https://www.yes24.com/product/goods/150701473",
            "aladin": "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=369431124",
        }
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 메인 순위 데이터 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_rankings (
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
            raw_data TEXT,  -- JSON 형태로 원본 데이터 저장
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 인덱스 생성
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON book_rankings(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON book_rankings(created_at)"
        )

        conn.commit()
        conn.close()
        logging.info(f"데이터베이스 초기화 완료: {self.db_path}")

    def save_ranking_data(self, results):
        """순위 데이터를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 데이터 추출
            timestamp = datetime.now()
            scraping_date = results.get("scraping_date", timestamp.isoformat())

            # 교보문고 데이터
            kyobo = results.get("kyobobook", {})
            kyobo_domestic_rank = kyobo.get("domestic_rank")
            kyobo_it_rank = kyobo.get("it_rank")
            kyobo_error = kyobo.get("error")

            # YES24 데이터
            yes24 = results.get("yes24", {})
            yes24_sales_index = yes24.get("sales_index")
            if yes24_sales_index and isinstance(yes24_sales_index, str):
                try:
                    yes24_sales_index = int(yes24_sales_index.replace(",", ""))
                except:
                    yes24_sales_index = None
            yes24_it_mobile_rank = yes24.get("it_mobile_rank")
            yes24_error = yes24.get("error")

            # 알라딘 데이터
            aladin = results.get("aladin", {})
            aladin_computer_weekly_rank = aladin.get("computer_weekly_rank")
            aladin_textbook_rank = aladin.get("textbook_rank")
            aladin_sales_point = aladin.get("sales_point")
            if aladin_sales_point and isinstance(aladin_sales_point, str):
                try:
                    aladin_sales_point = int(aladin_sales_point.replace(",", ""))
                except:
                    aladin_sales_point = None
            aladin_rank_period = aladin.get("rank_period")
            aladin_error = aladin.get("error")

            # 데이터 삽입
            cursor.execute(
                """
            INSERT INTO book_rankings (
                timestamp, scraping_date,
                kyobo_domestic_rank, kyobo_it_rank, kyobo_error,
                yes24_sales_index, yes24_it_mobile_rank, yes24_error,
                aladin_computer_weekly_rank, aladin_textbook_rank, 
                aladin_sales_point, aladin_rank_period, aladin_error,
                raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    scraping_date,
                    kyobo_domestic_rank,
                    kyobo_it_rank,
                    kyobo_error,
                    yes24_sales_index,
                    yes24_it_mobile_rank,
                    yes24_error,
                    aladin_computer_weekly_rank,
                    aladin_textbook_rank,
                    aladin_sales_point,
                    aladin_rank_period,
                    aladin_error,
                    json.dumps(results, ensure_ascii=False),
                ),
            )

            conn.commit()
            logging.info(
                f"✅ 데이터 저장 완료: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except Exception as e:
            logging.error(f"❌ 데이터 저장 실패: {e}", exc_info=True)
            conn.rollback()
        finally:
            conn.close()

    def collect_data(self):
        """데이터 수집 및 저장 실행"""
        logging.info(
            f"🕐 데이터 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        try:
            # 스크래핑 실행
            results = self.scraper.scrape_all(self.urls)

            # 데이터베이스에 저장
            self.save_ranking_data(results)

            # 요약 출력
            self.scraper.print_summary(results)

        except Exception as e:
            logging.error(f"❌ 데이터 수집 실패: {e}", exc_info=True)

    def get_recent_data(self, hours=24):
        """최근 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute(
            """
        SELECT * FROM book_rankings 
        WHERE timestamp >= ? 
        ORDER BY timestamp DESC
        """,
            (since,),
        )

        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        conn.close()
        return results

    def get_stats(self):
        """통계 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 총 레코드 수
        cursor.execute("SELECT COUNT(*) FROM book_rankings")
        total_records = cursor.fetchone()[0]

        # 최신/최오래된 데이터
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM book_rankings")
        oldest, newest = cursor.fetchone()

        # 최근 24시간 데이터 수
        since_24h = datetime.now() - timedelta(hours=24)
        cursor.execute(
            "SELECT COUNT(*) FROM book_rankings WHERE timestamp >= ?", (since_24h,)
        )
        recent_24h = cursor.fetchone()[0]

        conn.close()

        return {
            "total_records": total_records,
            "oldest_data": oldest,
            "newest_data": newest,
            "recent_24h": recent_24h,
        }

    def start_scheduler(self):
        """스케줄러 시작 (30분마다 실행)"""
        logging.info("📅 스케줄러 시작 - 30분마다 데이터 수집")

        # 30분마다 실행 스케줄 등록
        schedule.every(1).minutes.do(self.collect_data)

        # 즉시 한 번 실행
        self.collect_data()

        # 스케줄러 실행
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

    def run_once(self):
        """한 번만 실행"""
        self.collect_data()

    def close(self):
        """리소스 정리"""
        self.scraper.close()


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="도서 순위 모니터링 시스템")
    parser.add_argument(
        "--once", action="store_true", help="한 번만 실행 (스케줄러 시작하지 않음)"
    )
    parser.add_argument(
        "--db", default="book_rankings.db", help="데이터베이스 파일 경로"
    )
    parser.add_argument("--stats", action="store_true", help="통계 정보 출력")

    args = parser.parse_args()

    monitor = BookRankingMonitor(db_path=args.db)

    try:
        if args.stats:
            stats = monitor.get_stats()
            logging.info("📊 데이터베이스 통계:")
            logging.info(f"  총 레코드 수: {stats['total_records']}")
            logging.info(f"  최오래된 데이터: {stats['oldest_data']}")
            logging.info(f"  최신 데이터: {stats['newest_data']}")
            logging.info(f"  최근 24시간 레코드: {stats['recent_24h']}")

        elif args.once:
            monitor.run_once()
        else:
            monitor.start_scheduler()

    except KeyboardInterrupt:
        logging.info("⏹️  모니터링 중단")
    finally:
        monitor.close()


if __name__ == "__main__":
    main()
