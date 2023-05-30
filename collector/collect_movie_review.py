import time
import math
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from db.movie_crud import add_review

# anaconda prompt
# > conda activate cnu_python
# > pip install beautifulsoup
# > pip install selenium
# > pip install webdriver_manager

########################################
# 1. Install ChromeDriver for selenium #
########################################
# Selenium -> 개인 웹 브라우저 사용!(우리는 웹 브라우저 중 Chrome 사용)
driver = webdriver.Chrome()

########################
# 2. Open ChromeDriver #
########################
options = Options()
options.add_experimental_option("detach", True)  # ChromeDriver 자동 종료 X
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

###############################
# 2. Open URL in chromeDriver #
###############################
# Selenium: 동적 페이지에서 웹 크롤링 가능
#            -> 원래 용도: 웹 브라우저 테스트 용

movie_id = 160244
url = f"https://movie.daum.net/moviedb/grade?movieId={movie_id}"

# Selenium의 ChromeDriver를 통해서 해당 URL 접속
driver.get(url)
time.sleep(1)  # 1초 딜레이(웹 페이지 랜더링 완료까지 기다리기)
doc_html = driver.page_source  # 해당 URL 소스코드

doc = BeautifulSoup(doc_html, "html.parser")
title = doc.select("span.txt_tit")[1].text.strip  # 영화 제목 수집

total_review_txt = doc.select("span.txt_netizen")[0].text
# 정규화 -> 숫자만 추출
total_review = int(re.sub(r"[^~0-9]", "", total_review_txt))
click_cnt = math.ceil((total_review - 10) / 30)  # "평점 더보기" 버튼 클릭 횟수(모든 리뷰 출력을 위한)

for i in range(click_cnt):
    # "평점 더보기" 클릭(리뷰 30개씩 증가)
    driver.find_element(By.CLASS_NAME, "link_fold").click()
    time.sleep(1)
time.sleep(5)

# >> 해당 페이지에 모든 리뷰 출력 완료
review_html = driver.page_source
doc = BeautifulSoup(review_html, "html.parser")
review_list = doc.select("ul.list_comment div.cmt_info")

empty_cnt = 0
empty_list = []
for i, review_box in enumerate(review_list):
    if len(review_box.select("p.desc_txt")) == 0:
        empty_cnt += 1  # empty review cnt+1
        empty_list.append(i+1)  # empty review number
    else:
        review = review_box.select("p.desc_txt")[0].text.strip()
    review = review_box.select("p.desc_txt")[0].text
    score = review_box.select("div.ratings")[0].text
    writer = review_box.select("a.link_nick > span")[1].text
    review_date = review_box.select("span.txt_date")[0].text
    print(f"={i+1}================================================")
    print(f" - 리뷰: {review}")
    print(f" - 평점: {score}")
    print(f" - 작성자: {writer}")
    print(f" - 일자: {review_date}")

    # MongoDB 저장
    # - JSON type(dict) 전달
    data = {
        "title": str(title),
        "review": str(review),
        "score": str(score),
        "writer": str(writer),
        "regdate": str(review_date)
    }
    add_review(data)

# Report
print("=" * 30)
print(f"# MOVIE TITLE: {title}")
print("=" * 30)
print(f"  - Total Review: {total_review}")
print(f"  - Empty Review: {empty_cnt}")
if len(empty_list) > 0:
    print(f"   + {empty_list}")
print(f"  - Reviews collected: {total_review - empty_cnt}")
print("=" * 30)