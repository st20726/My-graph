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

movie_list = sorted(
    df["영화명"].dropna().unique().tolist()
)

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()

movie_daily = (
    movie_df
    .groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

fig1 = px.line(
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

fig1.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,}명"
    "<extra></extra>"
)

fig1.update_layout(
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
    fig1,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="",
    height=100,
    key="graph1_explanation"
)


# ==========================================
# 그래프 구역 2
# ==========================================

st.divider()

st.header("📈 그래프 2. 일관객 합계 상위 5편의 날짜별 변화")

st.write(
    "이 기간 동안 일관객 합계가 가장 큰 5편의 날짜별 일관객 변화를 비교합니다."
)

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)
)

top5_movie_names = top5_movies["영화명"].tolist()

top5_daily = (
    df[df["영화명"].isin(top5_movie_names)]
    .groupby(["날짜", "영화명"], as_index=False)["일관객"]
    .sum()
    .sort_values(["날짜", "영화명"])
)

fig2 = px.line(
    top5_daily,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=
    "영화: %{fullData.name}<br>"
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,}명"
    "<extra></extra>"
)

fig2.update_layout(
    height=600,
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    ),
    legend=dict(
        title="영화",
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="",
    height=100,
    key="graph2_explanation"
)


# ==========================================
# 그래프 구역 3
# ==========================================

st.divider()

st.header("📊 그래프 3. 날짜별 10위권 일관객 합계")

st.write(
    "각 날짜에 박스오피스 10위권 영화들이 기록한 일관객을 모두 합산하여 보여줍니다."
)


# 날짜별 10위권 일관객 합계
daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)


# 일관객 합계가 가장 큰 날 3일
top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("일관객", ascending=False)
)


# 영역 그래프
fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)


# 상위 3일 표시
for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=(
            f"{row['날짜'].strftime('%Y-%m-%d')}"
            f"<br>{row['일관객']:,}명"
        ),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-60
    )


fig3.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "10위권 일관객 합계: %{y:,}명"
    "<extra></extra>"
)

fig3.update_layout(
    height=600,
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        tickformat=","
    )
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="",
    height=100,
    key="graph3_explanation"
)


# ==========================================
# 그래프 구역 4
# ==========================================

st.divider()

st.header("📊 그래프 4. 일관객 합계 TOP 10 영화")

st.write(
    "이 기간 동안 일관객의 합계가 가장 큰 영화 10편을 비교합니다."
)


# ------------------------------------------
# 영화별 일관객 합계와 10위권 등장 일수 계산
# ------------------------------------------

movie_summary = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        등장일수=("날짜", "nunique")
    )
    .reset_index()
)


# 일관객 합계가 큰 순서로 정렬 후 TOP 10
top10_movies = (
    movie_summary
    .sort_values("일관객합계", ascending=False)
    .head(10)
    .sort_values("일관객합계", ascending=True)
)


# ------------------------------------------
# 가로 막대그래프
# ------------------------------------------

fig4 = px.bar(
    top10_movies,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="일관객 합계 TOP 10",
    labels={
        "일관객합계": "기간 내 일관객 합계",
        "영화명": "영화"
    },
    custom_data=["등장일수"]
)


# 마우스를 올렸을 때 표시되는 내용
fig4.update_traces(
    hovertemplate=
    "영화: %{y}<br>"
    "기간 내 일관객 합계: %{x:,}명<br>"
    "10위권에 든 날수: %{customdata[0]}일"
    "<extra></extra>"
)


fig4.update_layout(
    height=600,
    yaxis=dict(
        categoryorder="total ascending"
    ),
    xaxis=dict(
        tickformat=","
    )
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# ------------------------------------------
# 그래프 4 설명 입력칸
# ------------------------------------------

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="",
    height=100,
    key="graph4_explanation"
)


# ==========================================
# 그래프 구역 5
# 앞으로 새로운 그래프를 추가할 공간
# ==========================================

st.divider()

st.header("📊 그래프 5. 앞으로 추가할 그래프")

st.write(
    "새로운 시간 관련 그래프를 추가할 수 있는 공간입니다."
)
