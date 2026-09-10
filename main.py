import streamlit as st
import pandas as pd
import plotly.express as px


# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("1년치 일별 박스오피스 데이터를 이용해 영화 관객수의 변화를 살펴봅니다.")


# ==========================================
# 데이터 불러오기
# ==========================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 실제 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형 열 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.write(e)
    st.stop()


# ==========================================
# 데이터 기본 정보
# ==========================================

st.subheader("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("데이터 행 수", f"{len(df):,}개")

with col2:
    st.metric(
        "데이터 기간",
        f"{df['날짜'].min().strftime('%Y-%m-%d')} ~ "
        f"{df['날짜'].max().strftime('%Y-%m-%d')}"
    )

with col3:
    st.metric(
        "영화 종류",
        f"{df['영화명'].nunique():,}편"
    )


# ==========================================
# 그래프 구역 1
# ==========================================

st.divider()

st.header("📈 그래프 1. 영화별 일관객 변화")

st.write(
    "영화를 하나 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다."
)


# 영화 선택
movie_list = sorted(
    df["영화명"].dropna().unique().tolist()
)

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)


# 선택한 영화 데이터
movie_df = df[df["영화명"] == selected_movie].copy()

# 같은 날짜에 여러 기록이 있을 가능성을 고려하여 날짜별 일관객 합계 계산
movie_daily = (
    movie_df
    .groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)


# 그래프 생성
fig = px.line(
    movie_daily,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,}명"
    "<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    height=500,
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 그래프로 알 수 있는 것
# ==========================================

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "선택한 영화가 날짜에 따라 하루 동안 얼마나 많은 관객을 모았는지와 "
    "관객수가 증가하거나 감소하는 시점을 알 수 있습니다."
)


# ==========================================
# 그래프 구역 2
# 앞으로 새로운 그래프를 추가할 공간
# ==========================================

st.divider()

st.header("📊 그래프 2. 앞으로 추가할 그래프")

st.write(
    "여기에 새로운 시간 관련 그래프를 추가할 수 있습니다."
)

# 새로운 그래프를 추가할 때 이 부분 아래에 작성하면 됩니다.


# ==========================================
# 그래프 구역 3
# 앞으로 새로운 그래프를 추가할 공간
# ==========================================

st.divider()

st.header("📊 그래프 3. 앞으로 추가할 그래프")

st.write(
    "새로운 분석 그래프를 추가할 수 있는 공간입니다."
)
