import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# --------------------------------------------------
# 1. 페이지 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)


# --------------------------------------------------
# 2. 한국 시간 기준으로 '어제' 날짜 계산
# --------------------------------------------------
# Streamlit Cloud 서버가 어느 나라 시간으로 돌아가는지와 관계없이
# 서울 시간(KST)을 기준으로 날짜를 계산한다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()
yesterday = today_kst - timedelta(days=1)

# KOBIS API가 요구하는 날짜 형식: YYYYMMDD
target_date = yesterday.strftime("%Y%m%d")

# 화면에 보여줄 날짜 형식
display_date = yesterday.strftime("%Y년 %m월 %d일")


# --------------------------------------------------
# 3. 화면 제목
# --------------------------------------------------

st.title("🎬 어제의 박스오피스")
st.caption(f"KOBIS 기준 · {display_date}")


# --------------------------------------------------
# 4. Secrets에서 KOBIS 인증키 가져오기
# --------------------------------------------------
# Streamlit Cloud의 Secrets에
# KOBIS_KEY = "발급받은 인증키"
# 형태로 저장해 두어야 한다.

try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    st.error("⚠️ KOBIS 인증키를 찾을 수 없습니다.")
    st.info(
        "Streamlit Cloud의 Settings → Secrets에서 "
        "KOBIS_KEY가 등록되어 있는지 확인해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 5. KOBIS API 요청
# --------------------------------------------------

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)

params = {
    "key": api_key,
    "targetDt": target_date
}

try:
    response = requests.get(
        API_URL,
        params=params,
        timeout=10
    )

    # HTTP 오류가 발생하면 예외를 발생시킨다.
    response.raise_for_status()

    data = response.json()

except requests.exceptions.RequestException:
    st.error("⚠️ KOBIS API 요청에 실패했습니다.")
    st.info(
        "인터넷 연결, KOBIS API 주소, 인증키가 올바른지 "
        "확인해 주세요."
    )
    st.stop()

except ValueError:
    st.error("⚠️ KOBIS에서 올바른 JSON 데이터를 받지 못했습니다.")
    st.info(
        "KOBIS API가 정상적으로 응답했는지 잠시 후 다시 확인해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 6. 인증키 오류 확인
# --------------------------------------------------
# KOBIS는 인증키가 잘못되어도 HTTP 상태코드가 200일 수 있다.
# 따라서 faultInfo가 있는지 반드시 따로 확인한다.

if "faultInfo" in data:
    fault_info = data["faultInfo"]

    error_message = fault_info.get(
        "message",
        "KOBIS API 인증에 문제가 발생했습니다."
    )

    st.error("⚠️ KOBIS API 인증에 실패했습니다.")
    st.info(
        f"오류 내용: {error_message}\n\n"
        "Streamlit Cloud의 Secrets에 저장한 "
        "KOBIS_KEY가 정확한지 확인해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 7. 박스오피스 데이터 꺼내기
# --------------------------------------------------

try:
    boxoffice_result = data["boxOfficeResult"]
    movie_list = boxoffice_result["dailyBoxOfficeList"]

except (KeyError, TypeError):
    st.error("⚠️ 예상한 박스오피스 데이터가 없습니다.")
    st.info(
        "KOBIS API 응답 구조가 정상인지 확인하거나 "
        "잠시 후 다시 시도해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 8. 영화 목록이 비어 있는 경우
# --------------------------------------------------

if not movie_list:
    st.warning("📭 해당 날짜의 박스오피스 영화 목록이 없습니다.")
    st.info(
        f"조회 날짜: {display_date}\n\n"
        "KOBIS에서 해당 날짜의 일일 박스오피스가 "
        "아직 집계되지 않았거나 데이터가 제공되지 않는지 확인해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 9. 필요한 데이터만 표에 사용하기
# --------------------------------------------------

rows = []

for movie in movie_list:
    rows.append({
        "순위": int(movie["rank"]),
        "영화명": movie["movieNm"],
        "개봉일": movie["openDt"],
        "관객수": int(movie["audiCnt"]),
        "누적관객": int(movie["audiAcc"]),
        "스크린수": int(movie["scrnCnt"])
    })


df = pd.DataFrame(rows)


# --------------------------------------------------
# 10. 숫자를 보기 편하게 만드는 함수
# --------------------------------------------------

def format_number(value):
    """숫자에 천 단위 쉼표를 붙인다."""
    return f"{value:,}"


# --------------------------------------------------
# 11. 1위 영화 정보
# --------------------------------------------------

first_movie = df.iloc[0]

st.subheader("🏆 1위 영화")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="영화",
        value=first_movie["영화명"]
    )

with col2:
    st.metric(
        label="어제 관객수",
        value=f"{format_number(first_movie['관객수'])}명"
    )

with col3:
    st.metric(
        label="누적 관객",
        value=f"{format_number(first_movie['누적관객'])}명"
    )


# --------------------------------------------------
# 12. 관객수 상위 5편 막대그래프
# --------------------------------------------------

st.subheader("📊 관객수 상위 5편")

top5 = df.head(5).copy()

# 영화명을 인덱스로 설정해서 막대그래프의 이름으로 사용한다.
chart_data = top5.set_index("영화명")[["관객수"]]

st.bar_chart(chart_data)


# --------------------------------------------------
# 13. 전체 박스오피스 표
# --------------------------------------------------

st.subheader("🎞️ 전체 박스오피스")

display_df = df.copy()

# 표에서는 숫자를 1,234처럼 보기 편하게 표시한다.
display_df["관객수"] = display_df["관객수"].apply(format_number)
display_df["누적관객"] = display_df["누적관객"].apply(format_number)
display_df["스크린수"] = display_df["스크린수"].apply(format_number)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 14. 데이터 출처
# --------------------------------------------------

st.caption(
    f"※ 데이터 출처: 영화진흥위원회 KOBIS · {display_date} 일일 박스오피스"
)
