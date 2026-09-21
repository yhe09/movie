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
# 2. 전체 화면 디자인
# ============================================================

st.markdown(
    """
<style>

/* 전체 배경 */
.stApp {
    background-color: #0f1117;
}

/* 메인 제목 */
.main-title {
    color: #ffffff;
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

/* 제목 아래 날짜 */
.sub-title {
    color: #9ca3af;
    font-size: 15px;
    margin-bottom: 35px;
}

/* 섹션 제목 */
.section-title {
    color: #ffffff;
    font-size: 22px;
    font-weight: 700;
    margin-top: 32px;
    margin-bottom: 15px;
}

/* ==========================================================
   상단 숫자 카드
========================================================== */

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


/* ==========================================================
   1위 영화 카드
========================================================== */

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


/* ==========================================================
   TOP 5
========================================================== */

.top5-item {
    margin-bottom: 23px;
}

.top5-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.top5-rank {
    width: 40px;
    color: #8f96a3;
    font-size: 13px;
    font-weight: 700;
}

.top5-name {
    flex: 1;
    color: #f3f4f6;
    font-size: 15px;
    font-weight: 600;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.top5-number {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
}

.bar-background {
    height: 10px;
    background: #252a34;
    border-radius: 999px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    background: #f4c95d;
    border-radius: 999px;
}


/* ==========================================================
   순위 변동
========================================================== */

.rank-row {
    display: flex;
    align-items: center;
    padding: 14px 8px;
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
    width: 85px;
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

.new {
    color: #f4c95d;
}


/* ==========================================================
   오류 / 안내 박스
========================================================== */

.notice {
    background: #181b24;
    border: 1px solid #303642;
    border-radius: 14px;
    padding: 18px;
    color: #d1d5db;
}


/* ==========================================================
   표 아래 설명
========================================================== */

.table-note {
    color: #9ca3af !important;
    font-size: 13px;
    margin-top: 10px;
}


/* ==========================================================
   출처
========================================================== */

.source {
    color: #707887;
    font-size: 12px;
    border-top: 1px solid #272c36;
    padding-top: 15px;
    margin-top: 35px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# 3. 한국 시간 기준으로 '어제' 계산
# ============================================================
# Streamlit Cloud 서버의 시간이 한국 시간이 아닐 수 있으므로
# 반드시 Asia/Seoul 기준으로 날짜를 계산한다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()
yesterday = today_kst - timedelta(days=1)

# KOBIS API용 날짜: YYYYMMDD
target_date = yesterday.strftime("%Y%m%d")

# 화면 표시용 날짜
display_date = yesterday.strftime("%Y.%m.%d")


# ============================================================
# 4. 제목
# ============================================================

st.markdown(
    '<div class="main-title">🎬 DAILY BOX OFFICE</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="sub-title">'
    f'KOBIS 일일 박스오피스 · {display_date} 기준'
    f'</div>',
    unsafe_allow_html=True
)


# ============================================================
# 5. Secrets에서 KOBIS 인증키 가져오기
# ============================================================
# 인증키는 코드에 직접 넣지 않는다.
# Streamlit Cloud의 Secrets에 KOBIS_KEY를 등록해야 한다.

try:
    api_key = st.secrets["KOBIS_KEY"]

except Exception:

    st.error("🔐 KOBIS 인증키를 찾을 수 없습니다.")

    st.markdown(
        '<div class="notice">'
        '<b>확인할 것</b><br><br>'
        'Streamlit Cloud → Manage app → Settings → Secrets에서<br>'
        '<code>KOBIS_KEY = "발급받은 인증키"</code>가 '
        '등록되어 있는지 확인해 주세요.'
        '</div>',
        unsafe_allow_html=True
    )

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
# 7. KOBIS API 요청
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

    response.raise_for_status()

    data = response.json()

except requests.exceptions.Timeout:

    st.error("⏱️ KOBIS API 응답 시간이 초과되었습니다.")
    st.info("잠시 후 다시 접속해 주세요.")
    st.stop()

except requests.exceptions.RequestException:

    st.error("🌐 KOBIS API에 연결하지 못했습니다.")
    st.info(
        "인터넷 연결 또는 KOBIS API 서버 상태를 확인해 주세요."
    )
    st.stop()

except ValueError:

    st.error("📄 KOBIS에서 올바른 데이터를 받지 못했습니다.")
    st.info("잠시 후 다시 시도해 주세요.")
    st.stop()


# ============================================================
# 8. KOBIS 인증키 오류 확인
# ============================================================
# KOBIS는 인증키가 잘못되어도 HTTP 상태코드 200을
# 보낼 수 있기 때문에 faultInfo를 따로 확인한다.

if "faultInfo" in data:

    fault = data["faultInfo"]

    message = fault.get(
        "message",
        "KOBIS API 인증에 문제가 발생했습니다."
    )

    st.error("🔑 KOBIS API 인증에 실패했습니다.")

    st.markdown(
        f'<div class="notice">'
        f'<b>오류 내용</b><br>'
        f'{message}<br><br>'
        f'Streamlit Cloud의 Secrets에 저장한 '
        f'<b>KOBIS_KEY</b>가 정확한지 확인해 주세요.'
        f'</div>',
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# 9. 영화 목록 가져오기
# ============================================================

try:

    movie_list = data[
        "boxOfficeResult"
    ][
        "dailyBoxOfficeList"
    ]

except (KeyError, TypeError):

    st.error("📭 박스오피스 데이터를 찾을 수 없습니다.")

    st.info(
        "KOBIS API 응답을 확인하거나 잠시 후 다시 시도해 주세요."
    )

    st.stop()


# ============================================================
# 10. 영화 목록이 비어 있을 때
# ============================================================

if not movie_list:

    st.warning(
        "📭 해당 날짜의 박스오피스 영화 목록이 없습니다."
    )

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
# 11. API 데이터 정리
# ============================================================

rows = []

for movie in movie_list:

    # --------------------------------------------------------
    # 순위
    # --------------------------------------------------------

    try:
        rank = int(movie.get("rank", 0))
    except (ValueError, TypeError):
        rank = 0


    # --------------------------------------------------------
    # 전날 대비 순위 변동
    # --------------------------------------------------------

    try:
        rank_inten = int(movie.get("rankInten", 0))
    except (ValueError, TypeError):
        rank_inten = 0


    # --------------------------------------------------------
    # 관객수
    # --------------------------------------------------------

    try:
        audi_cnt = int(movie.get("audiCnt", 0))
    except (ValueError, TypeError):
        audi_cnt = 0


    # --------------------------------------------------------
    # 누적 관객수
    # --------------------------------------------------------

    try:
        audi_acc = int(movie.get("audiAcc", 0))
    except (ValueError, TypeError):
        audi_acc = 0


    # --------------------------------------------------------
    # 스크린수
    # --------------------------------------------------------

    try:
        scrn_cnt = int(movie.get("scrnCnt", 0))
    except (ValueError, TypeError):
        scrn_cnt = 0


    # --------------------------------------------------------
    # 신규 진입 여부
    # --------------------------------------------------------

    rank_old_and_new = movie.get(
        "rankOldAndNew",
        ""
    )


    # --------------------------------------------------------
    # 스크린당 관객수
    # --------------------------------------------------------

    if scrn_cnt > 0:

        audience_per_screen = (
            audi_cnt / scrn_cnt
        )

    else:

        audience_per_screen = 0


    # --------------------------------------------------------
    # 하나의 영화 데이터를 한 줄로 저장
    # --------------------------------------------------------

    rows.append(
        {
            "순위": rank,
            "순위변동": rank_inten,
            "신규여부": rank_old_and_new,
            "영화명": movie.get(
                "movieNm",
                "영화명 없음"
            ),
            "개봉일": movie.get(
                "openDt",
                "-"
            ),
            "관객수": audi_cnt,
            "누적관객": audi_acc,
            "스크린수": scrn_cnt,
            "스크린당 관객": audience_per_screen
        }
    )


# 데이터프레임으로 변환
df = pd.DataFrame(rows)


# ============================================================
# 12. 기본 지표 계산
# ============================================================

total_audience = int(
    df["관객수"].sum()
)

movie_count = len(df)

first_movie = df.iloc[0]


def number(value):
    """숫자에 천 단위 쉼표를 붙인다."""
    return f"{int(value):,}"


# ============================================================
# 13. 어제의 전체 숫자
# ============================================================

st.markdown(
    '<div class="section-title">YESTERDAY IN NUMBERS</div>',
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">👥 전체 관객</div>'
        f'<div class="stat-value">'
        f'{number(total_audience)}명'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">🎞️ 집계 영화</div>'
        f'<div class="stat-value">'
        f'{movie_count}편'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">🏆 1위 영화</div>'
        f'<div class="stat-value">'
        f'{first_movie["영화명"]}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# 14. 어제의 1위 영화
# ============================================================

st.markdown(
    '<div class="section-title">🏆 YESTERDAY\'S #1</div>',
    unsafe_allow_html=True
)


change = first_movie["순위변동"]


# 순위 변동 표시
if first_movie["신규여부"] == "NEW":

    movement = "NEW"

elif change > 0:

    movement = f"▲ {change}위 상승"

elif change < 0:

    movement = f"▼ {abs(change)}위 하락"

else:

    movement = "━ 순위 변동 없음"


# 1위 카드
hero_html = (
    '<div class="hero-card">'

    f'<div class="hero-rank">'
    f'RANK 01 · {movement}'
    f'</div>'

    f'<div class="hero-movie">'
    f'{first_movie["영화명"]}'
    f'</div>'

    f'<div class="hero-open">'
    f'개봉일 · {first_movie["개봉일"]}'
    f'</div>'

    '<div class="hero-info">'

    '<div>'
    '<div class="hero-label">어제 관객수</div>'
    f'<div class="hero-number">'
    f'{number(first_movie["관객수"])}명'
    f'</div>'
    '</div>'

    '<div>'
    '<div class="hero-label">누적 관객</div>'
    f'<div class="hero-number">'
    f'{number(first_movie["누적관객"])}명'
    f'</div>'
    '</div>'

    '<div>'
    '<div class="hero-label">스크린수</div>'
    f'<div class="hero-number">'
    f'{number(first_movie["스크린수"])}개'
    f'</div>'
    '</div>'

    '</div>'
    '</div>'
)


st.markdown(
    hero_html,
    unsafe_allow_html=True
)


# ============================================================
# 15. 관객수 TOP 5
# ============================================================
# Streamlit 기본 그래프 대신 직접 만든 가로 막대 그래프를 사용한다.
# 영화명이 세로로 돌아가지 않아서 보기 편하다.

st.markdown(
    '<div class="section-title">📊 AUDIENCE TOP 5</div>',
    unsafe_allow_html=True
)


top5 = (
    df
    .sort_values(
        "관객수",
        ascending=False
    )
    .head(5)
)


# 가장 관객수가 많은 영화를 100%로 설정
max_audience = top5["관객수"].max()


for i, (_, movie) in enumerate(
    top5.iterrows(),
    start=1
):

    if max_audience > 0:

        percentage = (
            movie["관객수"]
            / max_audience
            * 100
        )

    else:

        percentage = 0


    audience_text = (
        f'{int(movie["관객수"]):,}명'
    )


    top5_html = (
        '<div class="top5-item">'

        '<div class="top5-header">'

        f'<div class="top5-rank">'
        f'{i:02d}'
        f'</div>'

        f'<div class="top5-name">'
        f'{movie["영화명"]}'
        f'</div>'

        f'<div class="top5-number">'
        f'{audience_text}'
        f'</div>'

        '</div>'

        '<div class="bar-background">'

        f'<div class="bar-fill" '
        f'style="width:{percentage:.1f}%;">'
        '</div>'

        '</div>'

        '</div>'
    )


    st.markdown(
        top5_html,
        unsafe_allow_html=True
    )


# ============================================================
# 16. 순위 변동
# ============================================================

st.markdown(
    '<div class="section-title">📈 RANK MOVEMENT</div>',
    unsafe_allow_html=True
)


for _, movie in df.iterrows():

    change = movie["순위변동"]


    if movie["신규여부"] == "NEW":

        text = "NEW"
        css_class = "new"

    elif change > 0:

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

        f'<div class="rank-number">'
        f'{movie["순위"]}'
        f'</div>'

        f'<div class="rank-name">'
        f'{movie["영화명"]}'
        f'</div>'

        f'<div class="rank-change {css_class}">'
        f'{text}'
        f'</div>'

        '</div>'
    )


    st.markdown(
        row_html,
        unsafe_allow_html=True
    )


# ============================================================
# 17. 전체 박스오피스
# ============================================================

st.markdown(
    '<div class="section-title">🎞️ ALL BOX OFFICE</div>',
    unsafe_allow_html=True
)


display_df = df.copy()


# ------------------------------------------------------------
# 순위 변동을 사람이 읽기 좋은 형태로 변경
# ------------------------------------------------------------

def movement_text(row):

    if row["신규여부"] == "NEW":

        return "NEW"

    if row["순위변동"] > 0:

        return f'▲ {row["순위변동"]}'

    if row["순위변동"] < 0:

        return f'▼ {abs(row["순위변동"])}'

    return "━"


display_df["순위변동"] = display_df.apply(
    movement_text,
    axis=1
)


# ------------------------------------------------------------
# 숫자에 쉼표와 단위 붙이기
# ------------------------------------------------------------

display_df["관객수"] = (
    display_df["관객수"]
    .apply(
        lambda x: f"{x:,}명"
    )
)


display_df["누적관객"] = (
    display_df["누적관객"]
    .apply(
        lambda x: f"{x:,}명"
    )
)


display_df["스크린수"] = (
    display_df["스크린수"]
    .apply(
        lambda x: f"{x:,}개"
    )
)


display_df["스크린당 관객"] = (
    display_df["스크린당 관객"]
    .apply(
        lambda x: f"{x:,.1f}명"
    )
)


# ------------------------------------------------------------
# 표에 보여줄 열
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# 표 출력
# ------------------------------------------------------------

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 18. 표 설명
# ============================================================
# st.caption() 대신 직접 스타일을 지정해서
# 다크 테마에서 글씨가 검게 묻히는 문제를 방지한다.

st.markdown(
    '<div class="table-note">'
    '※ 스크린당 관객수 = 해당 영화의 당일 관객수 ÷ 스크린수'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 19. 데이터 출처
# ============================================================

st.markdown(
    f'<div class="source">'
    f'데이터 출처: 영화진흥위원회 KOBIS 일일 박스오피스 · '
    f'{display_date}'
    f'</div>',
    unsafe_allow_html=True
)
