"""
도서 순위 모니터링 대시보드
Streamlit을 사용한 실시간 데이터 시각화
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path


class BookRankingDashboard:
    def __init__(self, db_path="book_rankings.db"):
        """대시보드 초기화"""
        self.db_path = db_path

    def get_connection(self):
        """데이터베이스 연결"""
        return sqlite3.connect(self.db_path)

    def load_data(self, hours=24):
        """데이터 로드"""
        conn = self.get_connection()

        since = datetime.now() - timedelta(hours=hours)

        query = """
        SELECT 
            timestamp,
            kyobo_domestic_rank,
            kyobo_it_rank,
            yes24_sales_index,
            yes24_it_mobile_rank,
            aladin_computer_weekly_rank,
            aladin_textbook_rank,
            aladin_sales_point,
            aladin_rank_period
        FROM book_rankings 
        WHERE timestamp >= ? 
        ORDER BY timestamp
        """

        df = pd.read_sql_query(query, conn, params=(since,))
        conn.close()

        # 타임스탬프를 datetime으로 변환
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def load_all_data(self):
        """전체 데이터 로드"""
        conn = self.get_connection()

        query = """
        SELECT 
            *
        FROM book_rankings 
        ORDER BY timestamp
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        # 타임스탬프를 datetime으로 변환
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def get_latest_data(self):
        """최신 데이터 조회"""
        conn = self.get_connection()

        query = """
        SELECT * FROM book_rankings 
        ORDER BY timestamp DESC 
        LIMIT 1
        """

        result = conn.execute(query).fetchone()
        conn.close()

        if result:
            columns = [
                "id",
                "timestamp",
                "scraping_date",
                "kyobo_domestic_rank",
                "kyobo_it_rank",
                "kyobo_error",
                "yes24_sales_index",
                "yes24_it_mobile_rank",
                "yes24_error",
                "aladin_computer_weekly_rank",
                "aladin_textbook_rank",
                "aladin_sales_point",
                "aladin_rank_period",
                "aladin_error",
                "raw_data",
                "created_at",
            ]
            return dict(zip(columns, result))
        return None

    def get_stats(self):
        """통계 정보"""
        conn = self.get_connection()

        # 총 레코드 수
        total_records = conn.execute("SELECT COUNT(*) FROM book_rankings").fetchone()[0]

        # 최신/최오래된 데이터
        oldest, newest = conn.execute(
            "SELECT MIN(timestamp), MAX(timestamp) FROM book_rankings"
        ).fetchone()

        # 최근 24시간 데이터 수
        since_24h = datetime.now() - timedelta(hours=24)
        recent_24h = conn.execute(
            "SELECT COUNT(*) FROM book_rankings WHERE timestamp >= ?", (since_24h,)
        ).fetchone()[0]

        conn.close()

        return {
            "total_records": total_records,
            "oldest_data": oldest,
            "newest_data": newest,
            "recent_24h": recent_24h,
        }


def main():
    """메인 대시보드"""
    st.set_page_config(
        page_title="도서 순위 모니터링 대시보드",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📚 도서 순위 모니터링 대시보드")
    st.markdown("---")

    # 대시보드 인스턴스 생성
    dashboard = BookRankingDashboard()

    # 사이드바 설정
    st.sidebar.header("⚙️ 설정")

    # 시간 범위 선택
    time_options = {
        "최근 6시간": 6,
        "최근 12시간": 12,
        "최근 24시간": 24,
        "최근 48시간": 48,
        "최근 7일": 168,
        "전체 데이터": 0,
    }

    selected_time = st.sidebar.selectbox(
        "시간 범위", list(time_options.keys()), index=2
    )
    hours = time_options[selected_time]

    # 자동 새로고침
    auto_refresh = st.sidebar.checkbox("자동 새로고침 (30초)", value=True)

    if auto_refresh:
        st.rerun()

    # 데이터 로드
    try:
        if hours == 0:
            df = dashboard.load_all_data()
        else:
            df = dashboard.load_data(hours)

        latest_data = dashboard.get_latest_data()
        stats = dashboard.get_stats()

    except Exception as e:
        st.error(f"데이터를 로드할 수 없습니다: {e}")
        st.info(
            "먼저 `uv run book_ranking_monitor.py --once` 명령으로 데이터를 수집해주세요."
        )
        return

    # 통계 정보 표시
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총 레코드", stats["total_records"])

    with col2:
        st.metric("최근 24시간", stats["recent_24h"])

    with col3:
        if latest_data:
            latest_time = pd.to_datetime(latest_data["timestamp"]).strftime("%H:%M")
            st.metric("마지막 업데이트", latest_time)
        else:
            st.metric("마지막 업데이트", "없음")

    with col4:
        if len(df) > 0:
            data_points = len(df)
            st.metric("표시 데이터", f"{data_points}개")
        else:
            st.metric("표시 데이터", "0개")

    if len(df) == 0:
        st.warning("선택한 시간 범위에 데이터가 없습니다.")
        return

    # 최신 데이터 요약
    st.header("📊 최신 순위 현황")

    if latest_data:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📘 교보문고")
            st.write(
                f"**국내도서 순위:** {latest_data['kyobo_domestic_rank'] or 'N/A'}위"
            )
            st.write(f"**컴퓨터/IT 순위:** {latest_data['kyobo_it_rank'] or 'N/A'}위")

        with col2:
            st.subheader("📗 YES24")
            st.write(f"**판매지수:** {latest_data['yes24_sales_index'] or 'N/A'}")
            st.write(
                f"**IT모바일 순위:** {latest_data['yes24_it_mobile_rank'] or 'N/A'}위"
            )

        with col3:
            st.subheader("📙 알라딘")
            st.write(
                f"**컴퓨터/모바일 주간:** {latest_data['aladin_computer_weekly_rank'] or 'N/A'}위"
            )
            st.write(
                f"**대학교재 순위:** {latest_data['aladin_textbook_rank'] or 'N/A'}위"
            )
            st.write(f"**Sales Point:** {latest_data['aladin_sales_point'] or 'N/A'}")

    st.markdown("---")

    # 순위 변화 그래프
    st.header("📈 순위 변화 추이")

    # 순위 데이터 정리 (값이 낮을수록 좋은 순위이므로 y축 반전)
    rank_cols = [
        "kyobo_domestic_rank",
        "kyobo_it_rank",
        "yes24_it_mobile_rank",
        "aladin_computer_weekly_rank",
        "aladin_textbook_rank",
    ]

    rank_names = {
        "kyobo_domestic_rank": "교보문고 국내도서",
        "kyobo_it_rank": "교보문고 IT",
        "yes24_it_mobile_rank": "YES24 IT모바일",
        "aladin_computer_weekly_rank": "알라딘 컴퓨터/모바일",
        "aladin_textbook_rank": "알라딘 대학교재",
    }

    fig_rank = go.Figure()

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for i, col in enumerate(rank_cols):
        if col in df.columns and df[col].notna().any():
            fig_rank.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df[col],
                    mode="lines+markers",
                    name=rank_names[col],
                    line=dict(color=colors[i], width=2),
                    marker=dict(size=6),
                )
            )

    fig_rank.update_layout(
        title="순위 변화 (낮을수록 좋음)",
        xaxis_title="시간",
        yaxis_title="순위",
        yaxis=dict(autorange="reversed"),  # y축 반전
        height=500,
        hovermode="x unified",
    )

    st.plotly_chart(fig_rank, use_container_width=True)

    # 판매지수/포인트 변화 그래프
    st.header("💰 판매지수/포인트 변화")

    fig_sales = go.Figure()

    # YES24 판매지수
    if "yes24_sales_index" in df.columns and df["yes24_sales_index"].notna().any():
        fig_sales.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["yes24_sales_index"],
                mode="lines+markers",
                name="YES24 판매지수",
                yaxis="y",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=6),
            )
        )

    # 알라딘 Sales Point (다른 y축 사용)
    if "aladin_sales_point" in df.columns and df["aladin_sales_point"].notna().any():
        fig_sales.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["aladin_sales_point"],
                mode="lines+markers",
                name="알라딘 Sales Point",
                yaxis="y2",
                line=dict(color="#ff7f0e", width=2),
                marker=dict(size=6),
            )
        )

    fig_sales.update_layout(
        title="판매지수 및 포인트 변화",
        xaxis_title="시간",
        yaxis=dict(title="YES24 판매지수", side="left"),
        yaxis2=dict(title="알라딘 Sales Point", side="right", overlaying="y"),
        height=500,
        hovermode="x unified",
    )

    st.plotly_chart(fig_sales, use_container_width=True)

    # 데이터 테이블
    st.header("📋 상세 데이터")

    # 컬럼 선택
    display_columns = st.multiselect(
        "표시할 컬럼 선택:",
        options=df.columns.tolist(),
        default=[
            "timestamp",
            "kyobo_it_rank",
            "yes24_sales_index",
            "yes24_it_mobile_rank",
            "aladin_computer_weekly_rank",
            "aladin_textbook_rank",
            "aladin_sales_point",
        ],
    )

    if display_columns:
        display_df = df[display_columns].copy()

        # 타임스탬프 포맷팅
        if "timestamp" in display_df.columns:
            display_df["timestamp"] = display_df["timestamp"].dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        st.dataframe(display_df, use_container_width=True)

    # 원시 데이터 다운로드
    if st.button("📥 CSV 다운로드"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name=f"book_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    # 푸터
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "📚 도서 순위 모니터링 시스템 | "
        f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
