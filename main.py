import streamlit as st
import pandas as pd
import requests

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. 기본 설정
# ============================================================

st.set_page_config(
    page_title="Daily Box Office",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# 2. 화면 디자인
# ============================================================
# Streamlit 기본 화면에 조금 더 영화관 대시보드 같은 느낌을 주기 위한 CSS이다.

st.markdown("""
<style>

    /* 전체 배경 */
    .stApp {
        background-color: #0f1117;
    }

    /* 전체 글씨 */
    html, body, [class*="css"] {
        font-family: Arial, sans-serif;
    }

    /* 제목 */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }

    .sub-title {
        color: #9ca3af;
        font-size: 16px;
        margin-top: 4px;
        margin-bottom: 30px;
    }

    /* 작은 섹션 제목 */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 35px;
        margin-bottom: 15px;
    }

    /* 1위 영화 카드 */
    .hero-card {
        background: linear-gradient(135deg, #1d2029, #151821);
        border: 1px solid #303542;
        border-radius: 20px;
        padding: 30px;
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .hero-rank {
        color: #f5c451;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .hero-movie {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-open {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 25px;
    }

    .hero-number {
        font-size: 25px;
        font-weight: 700;
    }

    .hero-label {
        color: #9ca3af;
        font-size: 13px;
        margin-bottom: 3px;
    }

    /* 순위 변동 */
    .rank-up {
        color: #ff6b6b;
        font-weight: 700;
    }

    .rank-down {
        color: #5da9ff;
        font-weight: 700;
    }

    .rank-same {
        color: #9ca3af;
        font-weight: 700;
    }

    .rank-new {
        color: #f5c451;
        font-weight: 700;
    }

    /* 안내 박스 */
    .info-box {
        background-color: #191c24;
        border: 1px solid #303542;
        border-radius: 14px;
        padding: 18px;
        color: #d1d5db;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    /* 하단 출처 */
    .source {
        color: #6b7280;
        font-size: 12px;
        margin-top: 35px;
        padding-top: 15px;
        border-top: 1px solid #292d37;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. 한국 시간 기준으로 '어제' 계산
# ============================================================
# Streamlit Cloud 서버의 시간이 한국 시간이 아닐 수 있기 때문에
# 반드시 Asia/Seoul을 지정해서 날짜를 계산한다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()
yesterday = today_kst - timedelta(days=1)

# KOBIS API에서 사용하는 날짜 형식
target_date = yesterday.strftime("%Y%m%d")

# 화면에서 보여줄 날짜
display_date = yesterday.strftime("%Y.%m.%d")


# ============================================================
# 4. 제목
# ============================================================

st.markdown(
    '<div class="main-title">🎬 DAILY BOX OFFICE</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="sub-title">KOBIS 일일 박스오피스 · {display_date} 기준</div>',
    unsafe_allow_html=True
)


# ============================================================
# 5. KOBIS 인증키 가져오기
# ============================================================
# 인증키는 코드에 직접 적지 않는다.
# Streamlit Cloud의 Secrets에 KOBIS_KEY를 등록해야 한다.

try:
    api_key = st.secrets["KOBIS_KEY"]

except Exception:
    st.error("🔐 KOBIS 인증키를 찾을 수 없습니다.")

    st.markdown("""
    <div class="info-box">
    <b>확인할 것</b><br><br>
    1. Streamlit Cloud에서 Manage app → Settings → Secrets로 이동<br>
    2. 아래와 같은 형식으로 KOBIS_KEY가 등록되어 있는지 확인<br><br>
    <code>KOBIS_KEY = "발급받은 인증키"</code>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ============================================================
# 6. KOBIS API 주소
# ============================================================

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)


# ============================================================
# 7. API 요청
# ============================================================

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

    # 인터넷 연결 등의 HTTP 오류 확인
    response.raise_for_status()

    data = response.json()

except requests.exceptions.Timeout:
    st.error("⏱️ KOBIS API 응답 시간이 초과되었습니다.")

    st.info(
        "인터넷 연결 상태를 확인한 뒤 잠시 후 다시 접속해 주세요."
    )

    st.stop()

except requests.exceptions.RequestException:
    st.error("🌐 KOBIS API에 연결하지 못했습니다.")

    st.info(
        "인터넷 연결 상태나 KOBIS API 서버 상태를 확인해 주세요."
    )

    st.stop()

except ValueError:
    st.error("📄 KOBIS에서 올바른 데이터를 받지 못했습니다.")

    st.info(
        "KOBIS API가 정상적으로 응답했는지 잠시 후 다시 확인해 주세요."
    )

    st.stop()


# ============================================================
# 8. KOBIS 인증 오류 확인
# ============================================================
# 중요:
# KOBIS는 인증키가 틀려도 HTTP 상태코드가 200으로 올 수 있다.
# 그래서 faultInfo를 따로 확인한다.

fault_info = data.get("faultInfo")

if fault_info:

    error_message = fault_info.get(
        "message",
        "KOBIS API 인증에 문제가 발생했습니다."
    )

    st.error("🔑 KOBIS API 인증에 실패했습니다.")

    st.markdown(
        f"""
        <div class="info-box">
        <b>오류 내용</b><br>
        {error_message}<br><br>
        Streamlit Cloud의 Secrets에 저장한
        <b>KOBIS_KEY</b>가 정확한지 확인해 주세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 9. 박스오피스 데이터 가져오기
# ============================================================

try:

    boxoffice_result = data["boxOfficeResult"]

    movie_list = boxoffice_result["dailyBoxOfficeList"]

except (KeyError, TypeError):

    st.error("📭 박스오피스 데이터를 찾을 수 없습니다.")

    st.info(
        f"{display_date}의 KOBIS 일일 박스오피스 데이터가 "
        "정상적으로 제공되는지 확인해 주세요."
    )

    st.stop()


# ============================================================
# 10. 영화 목록이 비어 있는 경우
# ============================================================

if not movie_list:

    st.warning("📭 해당 날짜의 영화 목록이 없습니다.")

    st.markdown(
        f"""
        <div class="info-box">
        <b>조회 날짜</b> : {display_date}<br><br>
        KOBIS에서 해당 날짜의 일일 박스오피스가 아직 집계되지 않았거나
        데이터를 제공하지 않는 경우일 수 있습니다.<br><br>
        잠시 후 다시 확인해 주세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 11. API 데이터를 표에 사용하기 좋은 형태로 변환
# ============================================================

rows = []

for movie in movie_list:

    try:
        rank = int(movie.get("rank", 0))
    except (ValueError, TypeError):
        rank = 0

    try:
        rank_inten = int(movie.get("rankInten", 0))
    except (ValueError, TypeError):
        rank_inten = 0

    try:
        audi_cnt = int(movie.get("audiCnt", 0))
    except (ValueError, TypeError):
        audi_cnt = 0

    try:
        audi_acc = int(movie.get("audiAcc", 0))
    except (ValueError, TypeError):
        audi_acc = 0

    try:
        scrn_cnt = int(movie.get("scrnCnt", 0))
    except (ValueError, TypeError):
        scrn_cnt = 0

    # 스크린당 관객수를 직접 계산한다.
    if scrn_cnt > 0:
        audience_per_screen = audi_cnt / scrn_cnt
    else:
        audience_per_screen = 0

    rows.append({
        "순위": rank,
        "순위변동": rank_inten,
        "영화명": movie.get("movieNm", "영화명 없음"),
        "개봉일": movie.get("openDt", "-"),
        "관객수": audi_cnt,
        "누적관객": audi_acc,
        "스크린수": scrn_cnt,
        "스크린당 관객": audience_per_screen
    })


df = pd.DataFrame(rows)


# ============================================================
# 12. 숫자를 보기 좋게 만드는 함수
# ============================================================

def number(value):
    """숫자에 천 단위 쉼표를 붙인다."""
    return f"{int(value):,}"


# ============================================================
# 13. 전체 관객수 계산
# ============================================================
# 각 영화의 당일 관객수를 모두 더한다.

total_audience = int(df["관객수"].sum())
movie_count = len(df)

first_movie = df.iloc[0]


# ============================================================
# 14. 핵심 지표
# ============================================================

st.markdown(
    '<div class="section-title">TODAY IN NUMBERS</div>',
    unsafe_allow_html=True
)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric(
        label="👥 전체 관객",
        value=f"{number(total_audience)}명"
    )

with metric2:
    st.metric(
        label="🎞️ 집계 영화",
        value=f"{movie_count}편"
    )

with metric3:
    st.metric(
        label="🏆 1위",
        value=first_movie["영화명"]
    )


# ============================================================
# 15. 1위 영화 히어로 카드
# ============================================================

st.markdown(
    '<div class="section-title">🏆 YESTERDAY\'S #1</div>',
    unsafe_allow_html=True
)

rank_change = first_movie["순위변동"]

if rank_change > 0:
    rank_text = f"▲ {rank_change}위 상승"
elif rank_change < 0:
    rank_text = f"▼ {abs(rank_change)}위 하락"
else:
    rank_text = "━ 순위 변동 없음"


st.markdown(
    f"""
    <div class="hero-card">

        <div class="hero-rank">
            RANK 01 &nbsp; · &nbsp; {rank_text}
        </div>

        <div class="hero-movie">
            {first_movie["영화명"]}
        </div>

        <div class="hero-open">
            개봉일 · {first_movie["개봉일"]}
        </div>

        <div style="display: flex; gap: 70px; flex-wrap: wrap;">

            <div>
                <div class="hero-label">어제 관객수</div>
                <div class="hero-number">
                    {number(first_movie["관객수"])}명
                </div>
            </div>

            <div>
                <div class="hero-label">누적 관객</div>
                <div class="hero-number">
                    {number(first_movie["누적관객"])}명
                </div>
            </div>

            <div>
                <div class="hero-label">스크린수</div>
                <div class="hero-number">
                    {number(first_movie["스크린수"])}개
                </div>
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 16. 관객수 TOP 5
# ============================================================

st.markdown(
    '<div class="section-title">📊 AUDIENCE TOP 5</div>',
    unsafe_allow_html=True
)

top5 = (
    df.sort_values("관객수", ascending=False)
    .head(5)
    .copy()
)

# 그래프에서는 영화명을 인덱스로 사용한다.
chart_data = top5.set_index("영화명")[["관객수"]]

st.bar_chart(
    chart_data,
    use_container_width=True
)


# ============================================================
# 17. 순위 변동
# ============================================================

st.markdown(
    '<div class="section-title">📈 RANK MOVEMENT</div>',
    unsafe_allow_html=True
)

for _, movie in df.iterrows():

    change = movie["순위변동"]

    if change > 0:
        movement = f"▲ {change}"
        movement_class = "rank-up"

    elif change < 0:
        movement = f"▼ {abs(change)}"
        movement_class = "rank-down"

    else:
        movement = "━"
        movement_class = "rank-same"

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            padding:10px 5px;
            border-bottom:1px solid #242832;
        ">

            <div style="
                width:50px;
                font-weight:700;
            ">
                {movie["순위"]}
            </div>

            <div style="
                flex:1;
                font-weight:600;
            ">
                {movie["영화명"]}
            </div>

            <div class="{movement_class}" style="
                width:80px;
                text-align:right;
            ">
                {movement}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 18. 전체 박스오피스 표
# ============================================================

st.markdown(
    '<div class="section-title">🎞️ ALL BOX OFFICE</div>',
    unsafe_allow_html=True
)

display_df = df.copy()

# 화면에서 사용할 표를 보기 좋게 만든다.

display_df["관객수"] = display_df["관객수"].apply(
    lambda x: f"{x:,}명"
)

display_df["누적관객"] = display_df["누적관객"].apply(
    lambda x: f"{x:,}명"
)

display_df["스크린수"] = display_df["스크린수"].apply(
    lambda x: f"{x:,}개"
)

display_df["스크린당 관객"] = display_df["스크린당 관객"].apply(
    lambda x: f"{x:,.1f}명"
)


# 순위변동은 표에서 조금 더 직관적으로 표시한다.

def movement_text(value):

    if value > 0:
        return f"▲ {value}"

    if value < 0:
        return f"▼ {abs(value)}"

    return "━"


display_df["순위변동"] = df["순위변동"].apply(movement_text)


# 최종적으로 보여줄 열만 선택한다.

display_df = display_df[
    [
        "순위",
        "순위변동",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수",
        "스크린당 관객"
    ]
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 19. 스크린당 관객수 설명
# ============================================================

st.caption(
    "※ 스크린당 관객수 = 해당 영화의 당일 관객수 ÷ 스크린수로 계산한 값입니다."
)


# ============================================================
# 20. 데이터 출처
# ============================================================

st.markdown(
    f"""
    <div class="source">
    데이터 출처: 영화진흥위원회 KOBIS 일일 박스오피스<br>
    조회 기준일: {display_date}
    </div>
    """,
    unsafe_allow_html=True
)
