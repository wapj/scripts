"""
온라인 서점 도서 랭킹 정보 스크래퍼
교보문고, YES24, 알라딘에서 도서 순위 정보를 추출합니다.
"""

import json
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from bs4 import BeautifulSoup

# 로거 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BookRankingScraper:
    def __init__(self, debug=False):
        """
        스크래퍼 초기화

        Args:
            debug (bool): 디버깅 모드 활성화 여부
        """
        self.debug = debug
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.client = httpx.Client(
            headers=self.headers, follow_redirects=True, timeout=30.0
        )
        self.results = {}

    def fetch_page(self, url: str) -> Optional[str]:
        """페이지 HTML 가져오기"""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            # httpx는 자동으로 인코딩을 감지하지만, 필요시 명시적 설정
            if response.encoding is None:
                response.encoding = "utf-8"
            return response.text
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP 오류 ({url}): {e.response.status_code}")
            return None
        except Exception as e:
            logging.error(f"페이지 가져오기 실패 ({url}): {e}")
            return None

    def scrape_kyobobook(self, url: str) -> Dict[str, Any]:
        """
        교보문고에서 주간베스트 순위 추출
        - 국내 도서 순위
        - 컴퓨터/IT 순위
        """
        logging.info("교보문고 스크래핑 시작...")
        kyobo_data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "domestic_rank": None,
            "it_rank": None,
            "error": None,
        }

        try:
            html = self.fetch_page(url)
            if not html:
                kyobo_data["error"] = "페이지를 가져올 수 없습니다"
                return kyobo_data

            soup = BeautifulSoup(html, "html.parser")
            page_text = soup.get_text()

            # 주간베스트 정보 추출 - 다양한 패턴 시도
            # 국내도서 순위 찾기
            domestic_patterns = [
                r"국내도서\s*(\d+)위",
                r"국내도서\s*주간베스트\s*(\d+)위",
                r"국내\s*도서\s*(\d+)위",
                r"종합\s*(\d+)위",
                r"종합베스트\s*(\d+)위",
                r"주간베스트\s*국내도서\s*(\d+)위",
            ]

            for pattern in domestic_patterns:
                match = re.search(pattern, page_text)
                if match:
                    kyobo_data["domestic_rank"] = int(match.group(1))
                    break

            # 컴퓨터/IT 순위 찾기
            it_patterns = [
                r"컴퓨터/IT\s*(\d+)위",
                r"컴퓨터\s*/\s*IT\s*(\d+)위",
                r"IT/컴퓨터\s*(\d+)위",
                r"IT\s*(\d+)위",
                r"컴퓨터/모바일\s*(\d+)위",
                r"컴퓨터\s*(\d+)위",
            ]

            for pattern in it_patterns:
                match = re.search(pattern, page_text)
                if match:
                    kyobo_data["it_rank"] = int(match.group(1))
                    break

            # prod_rank_area 또는 유사한 클래스에서 찾기
            if not kyobo_data["domestic_rank"] or not kyobo_data["it_rank"]:
                rank_areas = [
                    "prod_rank_area",
                    "prod_rank_wrap",
                    "rankArea",
                    "bestRank",
                ]
                for area_class in rank_areas:
                    rank_section = soup.find("div", class_=area_class)
                    if rank_section:
                        section_text = rank_section.get_text()

                        if not kyobo_data["domestic_rank"]:
                            for pattern in domestic_patterns:
                                match = re.search(pattern, section_text)
                                if match:
                                    kyobo_data["domestic_rank"] = int(match.group(1))
                                    break

                        if not kyobo_data["it_rank"]:
                            for pattern in it_patterns:
                                match = re.search(pattern, section_text)
                                if match:
                                    kyobo_data["it_rank"] = int(match.group(1))
                                    break

            # 메타 데이터나 JSON-LD에서 찾기
            if not kyobo_data["domestic_rank"] or not kyobo_data["it_rank"]:
                script_tags = soup.find_all("script", type="application/ld+json")
                for script in script_tags:
                    try:
                        data = json.loads(script.string)
                        # JSON-LD 데이터에서 랭킹 정보 추출 시도
                        if isinstance(data, dict):
                            str_data = str(data)
                            if not kyobo_data["domestic_rank"]:
                                for pattern in domestic_patterns:
                                    match = re.search(pattern, str_data)
                                    if match:
                                        kyobo_data["domestic_rank"] = int(
                                            match.group(1)
                                        )
                                        break

                            if not kyobo_data["it_rank"]:
                                for pattern in it_patterns:
                                    match = re.search(pattern, str_data)
                                    if match:
                                        kyobo_data["it_rank"] = int(match.group(1))
                                        break
                    except:
                        continue

            # dl, dt, dd 태그에서 찾기
            if not kyobo_data["domestic_rank"] or not kyobo_data["it_rank"]:
                dl_elements = soup.find_all("dl")
                for dl in dl_elements:
                    dl_text = dl.get_text()
                    if not kyobo_data["domestic_rank"]:
                        for pattern in domestic_patterns:
                            match = re.search(pattern, dl_text)
                            if match:
                                kyobo_data["domestic_rank"] = int(match.group(1))
                                break

                    if not kyobo_data["it_rank"]:
                        for pattern in it_patterns:
                            match = re.search(pattern, dl_text)
                            if match:
                                kyobo_data["it_rank"] = int(match.group(1))
                                break

            logging.info(
                f"교보문고 데이터: 국내도서 {kyobo_data['domestic_rank']}위, IT {kyobo_data['it_rank']}위"
            )

        except Exception as e:
            kyobo_data["error"] = str(e)
            logging.error(f"교보문고 스크래핑 오류: {e}")

        return kyobo_data

    def scrape_yes24(self, url: str) -> Dict[str, Any]:
        """
        YES24에서 판매지수와 IT 모바일 순위 추출
        메인 상품 페이지와 베스트셀러 모듈 페이지를 모두 확인
        """
        logging.info("YES24 스크래핑 시작...")
        yes24_data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "sales_index": None,
            "it_mobile_rank": None,
            "error": None,
        }

        try:
            # 메인 상품 페이지에서 판매지수 추출
            html = self.fetch_page(url)
            if not html:
                yes24_data["error"] = "메인 페이지를 가져올 수 없습니다"
                return yes24_data

            soup = BeautifulSoup(html, "html.parser")

            # 판매지수 찾기
            sales_patterns = [
                r"판매지수\s*[:\s]*(\d+(?:,\d+)*)",
                r"Sales\s*Point\s*[:\s]*(\d+(?:,\d+)*)",
                r"판매\s*지수\s*(\d+(?:,\d+)*)",
            ]

            # 전체 페이지에서 판매지수 검색
            page_text = soup.get_text()
            for pattern in sales_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    yes24_data["sales_index"] = match.group(1).replace(",", "")
                    break

            # 판매지수가 특정 요소에 있는 경우
            if not yes24_data["sales_index"]:
                # gd_infoBot 클래스 내부 검색
                info_section = soup.find("div", class_="gd_infoBot")
                if info_section:
                    text = info_section.get_text()
                    match = re.search(r"판매지수\s*(\d+(?:,\d+)*)", text)
                    if match:
                        yes24_data["sales_index"] = match.group(1).replace(",", "")

            # URL에서 상품 ID 추출하여 베스트셀러 모듈 URL 생성
            product_id_match = re.search(r"/goods/(\d+)", url)
            if product_id_match:
                product_id = product_id_match.group(1)
                module_url = f"https://www.yes24.com/Product/addModules/BestSellerRank_Book/{product_id}/?categoryNumber=001001003025009&FreePrice=N"

                logging.info(f"베스트셀러 모듈 URL 확인 중: {module_url}")

                # 베스트셀러 모듈 페이지에서 IT 모바일 순위 추출
                module_html = self.fetch_page(module_url)
                if module_html:
                    module_soup = BeautifulSoup(module_html, "html.parser")
                    module_text = module_soup.get_text()

                    # IT 모바일 순위 패턴 - 모듈 페이지에 특화된 패턴
                    it_patterns = [
                        r"IT\s*모바일\s*(\d+)위",
                        r"IT\s*모바일\s*top\d+\s*(\d+)주",  # "IT 모바일 top20 1주" 형식도 고려
                        r"IT/모바일\s*(\d+)위",
                        r"IT\s*/\s*모바일\s*(\d+)",
                    ]

                    for pattern in it_patterns:
                        match = re.search(pattern, module_text)
                        if match:
                            rank_num = match.group(1)
                            # 순위가 숫자인지 확인 (주차는 제외)
                            if (
                                rank_num.isdigit() and int(rank_num) <= 100
                            ):  # 100위 이하는 유효한 순위로 간주
                                yes24_data["it_mobile_rank"] = int(rank_num)
                                break

                    if self.debug and module_text:
                        logging.debug(f"모듈 페이지 내용 일부: {module_text[:200]}")
                else:
                    logging.warning("베스트셀러 모듈 페이지를 가져올 수 없습니다.")

            # 메인 페이지에서도 IT 모바일 순위 시도 (보조 수단)
            if not yes24_data["it_mobile_rank"]:
                it_patterns = [
                    r"IT\s*모바일\s*(\d+)위",
                    r"IT/모바일\s*(\d+)위",
                    r"IT\s*/\s*모바일\s*(\d+)",
                    r"컴퓨터/IT\s*(\d+)위",
                    r"컴퓨터\s*/\s*모바일\s*(\d+)위",
                    r"컴퓨터\s*모바일\s*(\d+)위",
                    r"IT\s*(\d+)위",
                    r"IT/컴퓨터\s*(\d+)위",
                ]

                for pattern in it_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        yes24_data["it_mobile_rank"] = int(match.group(1))
                        break

                # 베스트셀러 랭킹 섹션에서 찾기
                if not yes24_data["it_mobile_rank"]:
                    # 여러 가능한 클래스명으로 시도
                    rank_classes = [
                        "gd_best",
                        "rank_row",
                        "cate_best",
                        "rankRow",
                        "gd_nameH",
                    ]
                    for class_name in rank_classes:
                        rank_elem = soup.find("div", class_=class_name)
                        if rank_elem:
                            rank_text = rank_elem.get_text()
                            for pattern in it_patterns:
                                match = re.search(pattern, rank_text)
                                if match:
                                    yes24_data["it_mobile_rank"] = int(match.group(1))
                                    break
                            if yes24_data["it_mobile_rank"]:
                                break

                # 베스트셀러 정보가 있는 dl, dt, dd 태그 검색
                if not yes24_data["it_mobile_rank"]:
                    dl_elements = soup.find_all("dl")
                    for dl in dl_elements:
                        text = dl.get_text()
                        for pattern in it_patterns:
                            match = re.search(pattern, text)
                            if match:
                                yes24_data["it_mobile_rank"] = int(match.group(1))
                                break
                        if yes24_data["it_mobile_rank"]:
                            break

            # 디버깅: 카테고리 정보가 포함된 영역 출력
            if not yes24_data["it_mobile_rank"] and self.debug:
                logging.debug(
                    "IT 모바일 순위를 찾을 수 없음. 카테고리 관련 텍스트 검색 중..."
                )
                # 'IT', '모바일', '컴퓨터' 키워드가 포함된 요소 찾기
                keywords = ["IT", "모바일", "컴퓨터"]
                for keyword in keywords:
                    elements = soup.find_all(text=re.compile(keyword))
                    for elem in elements[:3]:  # 처음 3개만 확인
                        if elem and "위" in elem:
                            logging.debug(f"  찾은 텍스트: {elem.strip()[:100]}")

            logging.info(
                f"YES24 데이터: 판매지수 {yes24_data['sales_index']}, IT모바일 {yes24_data['it_mobile_rank']}위"
            )

        except Exception as e:
            yes24_data["error"] = str(e)
            logging.error(f"YES24 스크래핑 오류: {e}")

        return yes24_data

    def scrape_aladin(self, url: str) -> Dict[str, Any]:
        """
        알라딘에서 순위 정보 추출
        - 컴퓨터/모바일 주간 순위
        - 대학교재/전문서적 top100 순위
        - Sales Point
        """
        logging.info("알라딘 스크래핑 시작...")
        aladin_data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "computer_weekly_rank": None,
            "textbook_rank": None,
            "sales_point": None,
            "rank_period": None,
            "error": None,
        }

        try:
            html = self.fetch_page(url)
            if not html:
                aladin_data["error"] = "페이지를 가져올 수 없습니다"
                return aladin_data

            soup = BeautifulSoup(html, "html.parser")
            page_text = soup.get_text()

            # 컴퓨터/모바일 주간 순위
            computer_patterns = [
                r"컴퓨터/모바일\s*주간\s*(\d+)위",
                r"컴퓨터\s*/\s*모바일\s*.*?(\d+)위",
                r"IT/컴퓨터.*?주간\s*(\d+)",
            ]

            for pattern in computer_patterns:
                match = re.search(pattern, page_text)
                if match:
                    aladin_data["computer_weekly_rank"] = int(match.group(1))
                    break

            # 대학교재/전문서적 순위
            textbook_patterns = [
                r"대학교재/전문서적\s*top\s*100\s*(\d+)",
                r"대학교재\s*/\s*전문서적.*?(\d+)위",
                r"전문서적.*?top.*?(\d+)",
            ]

            for pattern in textbook_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    aladin_data["textbook_rank"] = int(match.group(1))
                    break

            # 순위 기간 (예: 2주)
            period_match = re.search(r"(\d+)주\s*\|", page_text)
            if period_match:
                aladin_data["rank_period"] = f"{period_match.group(1)}주"

            # Sales Point
            sales_patterns = [
                r"Sales\s*Point\s*:\s*(\d+(?:,\d+)*)",
                r"판매지수\s*:\s*(\d+(?:,\d+)*)",
                r"Sales\s*Point\s*(\d+(?:,\d+)*)",
            ]

            for pattern in sales_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    aladin_data["sales_point"] = match.group(1).replace(",", "")
                    break

            # 베스트셀러 정보 섹션에서 추가 검색
            bestseller_section = soup.find("div", class_=re.compile("best|rank"))
            if bestseller_section and not all(
                [
                    aladin_data["computer_weekly_rank"],
                    aladin_data["textbook_rank"],
                    aladin_data["sales_point"],
                ]
            ):
                section_text = bestseller_section.get_text()

                # 추가 패턴 매칭 시도
                if not aladin_data["computer_weekly_rank"]:
                    match = re.search(r"컴퓨터.*?(\d+)위", section_text)
                    if match:
                        aladin_data["computer_weekly_rank"] = int(match.group(1))

                if not aladin_data["sales_point"]:
                    match = re.search(
                        r"(\d+(?:,\d+)*)\s*point", section_text, re.IGNORECASE
                    )
                    if match:
                        aladin_data["sales_point"] = match.group(1).replace(",", "")

            logging.info(
                f"알라딘 데이터: 컴퓨터/모바일 {aladin_data['computer_weekly_rank']}위, "
                f"대학교재 {aladin_data['textbook_rank']}위, "
                f"Sales Point {aladin_data['sales_point']}"
            )

        except Exception as e:
            aladin_data["error"] = str(e)
            logging.error(f"알라딘 스크래핑 오류: {e}")

        return aladin_data

    def scrape_all(self, urls: Dict[str, str]) -> Dict[str, Any]:
        """
        모든 사이트 스크래핑 실행

        Args:
            urls: {'kyobobook': url, 'yes24': url, 'aladin': url}

        Returns:
            모든 스크래핑 결과
        """
        logging.info(
            f"모든 사이트 스크래핑 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        results = {
            "scraping_date": datetime.now().isoformat(),
            "kyobobook": None,
            "yes24": None,
            "aladin": None,
        }

        # 교보문고 스크래핑
        if "kyobobook" in urls:
            results["kyobobook"] = self.scrape_kyobobook(urls["kyobobook"])
            time.sleep(1)  # 요청 간격 두기

        # YES24 스크래핑
        if "yes24" in urls:
            results["yes24"] = self.scrape_yes24(urls["yes24"])
            time.sleep(1)

        # 알라딘 스크래핑
        if "aladin" in urls:
            results["aladin"] = self.scrape_aladin(urls["aladin"])

        logging.info(
            f"모든 사이트 스크래핑 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return results

    def save_results(self, results: Dict[str, Any], filename: str = None):
        """결과를 JSON 파일로 저장"""
        if filename is None:
            filename = f"book_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logging.info(f"결과가 {filename}에 저장되었습니다.")
        return filename

    def print_summary(self, results: Dict[str, Any]):
        """결과 요약 출력"""
        logging.info("========== 📚 도서 순위 정보 요약 ==========")

        if results.get("kyobobook"):
            data = results["kyobobook"]
            if not data.get("error"):
                logging.info(
                    f"📘 교보문고: 국내도서 {data.get('domestic_rank', 'N/A')}위, IT {data.get('it_rank', 'N/A')}위"
                )
            else:
                logging.error(f"📘 교보문고: ❌ 오류: {data['error']}")

        if results.get("yes24"):
            data = results["yes24"]
            if not data.get("error"):
                logging.info(
                    f"📗 YES24: 판매지수 {data.get('sales_index', 'N/A')}, IT모바일 {data.get('it_mobile_rank', 'N/A')}위"
                )
            else:
                logging.error(f"📗 YES24: ❌ 오류: {data['error']}")

        if results.get("aladin"):
            data = results["aladin"]
            if not data.get("error"):
                logging.info(
                    f"📙 알라딘: 컴퓨터/모바일 {data.get('computer_weekly_rank', 'N/A')}위, "
                    f"대학교재 {data.get('textbook_rank', 'N/A')}위, "
                    f"Sales Point {data.get('sales_point', 'N/A')}"
                )
            else:
                logging.error(f"📙 알라딘: ❌ 오류: {data['error']}")
        logging.info("========================================")

    def close(self):
        """리소스 정리"""
        if hasattr(self, "client"):
            self.client.close()


# 사용 예시
def main():
    """메인 실행 함수"""
    # URL 설정
    urls = {
        "kyobobook": "https://product.kyobobook.co.kr/detail/S000217241525",
        "yes24": "https://www.yes24.com/product/goods/150701473",
        "aladin": "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=369431124",
    }

    # 스크래퍼 생성 (디버깅 모드는 선택사항)
    scraper = BookRankingScraper(debug=False)

    try:
        # 모든 사이트 스크래핑
        results = scraper.scrape_all(urls)

        # 결과 요약 출력
        scraper.print_summary(results)

        # 결과 저장
        filename = scraper.save_results(results)

        # 상세 결과 출력 (선택사항)
        logging.debug(f"상세 결과: {json.dumps(results, ensure_ascii=False, indent=2)}")

    except Exception as e:
        logging.critical(f"스크래핑 중 심각한 오류 발생: {e}", exc_info=True)
    finally:
        scraper.close()


# 설치 명령어
# pip install httpx beautifulsoup4

if __name__ == "__main__":
    main()
