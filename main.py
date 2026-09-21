import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Daily Box Office",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# 2. 화면 디자인
# ============================================================

st.markdown("""
<style>
.stApp {
    background-color: #0f1117;
}

.main-title {
    color: #ffffff;
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

.sub-title {
    color: #9ca3af;
    font-size: 15px;
    margin-bottom: 35px;
}

.section-title {
    color: #ffffff;
    font-size: 22px;
    font-weight: 700;
    margin-top: 32px;
    margin-bottom: 15px;
}

/* 숫자 카드 */
.stat-card {
    background: #181b24;
    border: 1px solid #2b303b;
    border-radius: 16px;
    padding: 20px;
    min-height: 105px;
}

.stat-label {
    color: #9ca3af;
    font-size: 14px;
    margin-bottom: 8px;
}

.stat-value {
    color: #ffffff;
    font-size: 27px;
    font-weight: 750;
}

/* 1위 영화 카드 */
.hero-card {
    background: linear-gradient(135deg, #1c202a, #151821);
    border: 1px solid #343a48;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 25px;
}

.hero-rank {
    color: #f4c95d;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 8px;
}

.hero-movie {
    color: #ffffff;
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 7px;
}

.hero-open {
    color: #9ca3af;
    font-size: 14px;
    margin-bottom: 28px;
}

.hero-info {
    display: flex;
    gap: 60px;
    flex-wrap: wrap;
}

.hero-label {
    color: #9ca3af;
    font-size: 13px;
    margin-bottom: 5px;
}

.hero-number {
    color: #ffffff;
    font-size: 24px;
    font-weight: 700;
}

/* 순위 변동 */
.rank-row {
    display: flex;
    align-items: center;
    padding: 13px 8px;
    border-bottom: 1px solid #252934;
}

.rank-number {
    width: 45px;
    color: #ffffff;
    font-weight: 700;
}

.rank-name {
    flex: 1;
    color: #e5e7eb;
    font-weight: 600;
}

.rank-change {
    width: 75px;
    text-align: right;
    font-weight: 700;
}

.up {
    color: #ff6b6b;
}

.down {
    color: #62a8ff;
}

.same {
    color: #8b93a1;
}

/* 안내 박스 */
.notice {
    background: #181b24;
    border: 1px solid #303642;
    border-radius: 14px;
    padding: 18px;
    color: #d1d5db;
}

/* 출처 */
.source {
    color: #707887;
    font-size: 12px;
    border-top: 1px solid #272c36;
    padding-top: 15px;
    margin-top: 35px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. 한국 시간 기준 '어제' 계산
# ============================================================

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()
yesterday = today_kst - timedelta(days=1)

target_date = yesterday.strftime("%Y%m%d")
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
# 5. KOBIS 인증키
# ============================================================

try:
    api_key = st.secrets["KOBIS_KEY"]

except Exception:
    st.error("🔐 KOBIS 인증키를 찾을 수 없습니다.")

    st.markdown(
        '<div class="notice">'
        '<b>확인할 것</b><br><br>'
        'Streamlit Cloud → Manage app → Settings → Secrets에서<br>'
        '<code>KOBIS_KEY = "발급받은 인증키"</code>가 등록되어 있는지 확인해 주세요.'
        '</div>',
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 6. KOBIS API 요청
# ============================================================

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

    response.raise_for_status()
    data = response.json()

except requests.exceptions.Timeout:
    st.error("⏱️ KOBIS API 응답 시간이 초과되었습니다.")
    st.info("잠시 후 다시 접속해 주세요.")
    st.stop()

except requests.exceptions.RequestException:
    st.error("🌐 KOBIS API에 연결하지 못했습니다.")
    st.info("인터넷 연결 또는 KOBIS API 서버 상태를 확인해 주세요.")
    st.stop()

except ValueError:
    st.error("📄 KOBIS에서 올바른 데이터를 받지 못했습니다.")
    st.info("잠시 후 다시 시도해 주세요.")
    st.stop()


# ============================================================
# 7. 인증키 오류 확인
# ============================================================

if "faultInfo" in data:
    fault = data["faultInfo"]

    message = fault.get(
        "message",
        "KOBIS API 인증에 문제가 발생했습니다."
    )

    st.error("🔑 KOBIS API 인증에 실패했습니다.")

    st.markdown(
        f'<div class="notice">'
        f'<b>오류 내용</b><br>{message}<br><br>'
        f'Streamlit Cloud의 Secrets에 저장한 KOBIS_KEY가 정확한지 확인해 주세요.'
        f'</div>',
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 8. 영화 목록 가져오기
# ============================================================

try:
    movie_list = data["boxOfficeResult"]["dailyBoxOfficeList"]

except (KeyError, TypeError):
    st.error("📭 박스오피스 데이터를 찾을 수 없습니다.")
    st.info("KOBIS API 응답을 확인하거나 잠시 후 다시 시도해 주세요.")
    st.stop()


# ============================================================
# 9. 영화 목록이 비어 있을 때
# ============================================================

if not movie_list:
    st.warning("📭 해당 날짜의 박스오피스 영화 목록이 없습니다.")

    st.markdown(
        f'<div class="notice">'
        f'<b>조회 날짜</b> : {display_date}<br><br>'
        f'해당 날짜의 박스오피스가 아직 집계되지 않았거나 '
        f'KOBIS에서 데이터를 제공하지 않는 경우일 수 있습니다.'
        f'</div>',
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 10. 데이터 정리
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
# 11. 기본 지표 계산
# ============================================================

total_audience = int(df["관객수"].sum())
movie_count = len(df)
first_movie = df.iloc[0]


def number(value):
    return f"{int(value):,}"


# ============================================================
# 12. 핵심 숫자
# ============================================================

st.markdown(
    '<div class="section-title">TODAY IN NUMBERS</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">👥 전체 관객</div>'
        f'<div class="stat-value">{number(total_audience)}명</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">🎞️ 집계 영화</div>'
        f'<div class="stat-value">{movie_count}편</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">🏆 1위 영화</div>'
        f'<div class="stat-value">{first_movie["영화명"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# 13. 1위 영화
# ============================================================

st.markdown(
    '<div class="section-title">🏆 YESTERDAY\'S #1</div>',
    unsafe_allow_html=True
)

change = first_movie["순위변동"]

if change > 0:
    movement = f"▲ {change}위 상승"
elif change < 0:
    movement = f"▼ {abs(change)}위 하락"
else:
    movement = "━ 순위 변동 없음"


# 중요:
# HTML 태그를 줄의 맨 앞에서 시작하도록 작성한다.
# 들여쓰기를 넣으면 Markdown이 코드 블록으로 인식할 수 있다.

hero_html = (
    '<div class="hero-card">'
    f'<div class="hero-rank">RANK 01 · {movement}</div>'
    f'<div class="hero-movie">{first_movie["영화명"]}</div>'
    f'<div class="hero-open">개봉일 · {first_movie["개봉일"]}</div>'
    '<div class="hero-info">'
    '<div>'
    '<div class="hero-label">어제 관객수</div>'
    f'<div class="hero-number">{number(first_movie["관객수"])}명</div>'
    '</div>'
    '<div>'
    '<div class="hero-label">누적 관객</div>'
    f'<div class="hero-number">{number(first_movie["누적관객"])}명</div>'
    '</div>'
    '<div>'
    '<div class="hero-label">스크린수</div>'
    f'<div class="hero-number">{number(first_movie["스크린수"])}개</div>'
    '</div>'
    '</div>'
    '</div>'
)

st.markdown(hero_html, unsafe_allow_html=True)


# ============================================================
# 14. 관객수 TOP 5
# ============================================================

st.markdown(
    '<div class="section-title">📊 AUDIENCE TOP 5</div>',
    unsafe_allow_html=True
)

top5 = df.sort_values(
    "관객수",
    ascending=False
).head(5)

chart_data = top5.set_index("영화명")[["관객수"]]

st.bar_chart(
    chart_data,
    use_container_width=True
)


# ============================================================
# 15. 순위 변동
# ============================================================

st.markdown(
    '<div class="section-title">📈 RANK MOVEMENT</div>',
    unsafe_allow_html=True
)

for _, movie in df.iterrows():

    change = movie["순위변동"]

    if change > 0:
        text = f"▲ {change}"
        css_class = "up"

    elif change < 0:
        text = f"▼ {abs(change)}"
        css_class = "down"

    else:
        text = "━"
        css_class = "same"

    row_html = (
        '<div class="rank-row">'
        f'<div class="rank-number">{movie["순위"]}</div>'
        f'<div class="rank-name">{movie["영화명"]}</div>'
        f'<div class="rank-change {css_class}">{text}</div>'
        '</div>'
    )

    st.markdown(
        row_html,
        unsafe_allow_html=True
    )


# ============================================================
# 16. 전체 박스오피스
# ============================================================

st.markdown(
    '<div class="section-title">🎞️ ALL BOX OFFICE</div>',
    unsafe_allow_html=True
)

display_df = df.copy()


def movement_text(value):

    if value > 0:
        return f"▲ {value}"

    if value < 0:
        return f"▼ {abs(value)}"

    return "━"


display_df["순위변동"] = display_df["순위변동"].apply(
    movement_text
)

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
# 17. 설명
# ============================================================

st.caption(
    "※ 스크린당 관객수 = 해당 영화의 당일 관객수 ÷ 스크린수"
)


# ============================================================
# 18. 출처
# ============================================================

st.markdown(
    f'<div class="source">'
    f'데이터 출처: 영화진흥위원회 KOBIS 일일 박스오피스 · {display_date}'
    f'</div>',
    unsafe_allow_html=True
)
