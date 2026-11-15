"""장비별 상세 페이지: 주차 · 장비를 고르면 가동률 · 합계 · 일별 추이 · 원본 표."""
from pathlib import Path

import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
WEEKS = {"W45 (이번 주)": DATA / "readiness_W45.csv", "W44 (지난주)": DATA / "readiness_W44.csv"}


@st.cache_data
def _load(path: str):
    return calc.load_readiness(path)


st.title("장비별 상세")

c1, c2 = st.columns(2)
week = c1.selectbox("주차", list(WEEKS))
df = _load(str(WEEKS[week]))

by_eq = calc.rate_by_equipment(df)
labels = {f"{r.장비코드} · {r.장비명}": r.장비코드 for r in by_eq.itertuples()}
code = labels[c2.selectbox("장비", list(labels))]

row = by_eq[by_eq["장비코드"] == code].iloc[0]
m1, m2, m3 = st.columns(3)
m1.metric("가동률", f"{row['가동률']:.1f}%")
m2.metric("가동시간 합계", f"{row['가동시간']:g}h")
m3.metric("계획시간 합계", f"{row['계획시간']:g}h")

rows = df[df["장비코드"] == code]

st.subheader("일별 계획 · 가동시간")
daily = (
    rows.groupby("일자", as_index=True)[["계획시간(h)", "가동시간(h)"]]
    .sum()
    .rename(columns={"계획시간(h)": "계획시간", "가동시간(h)": "가동시간"})
)
st.line_chart(daily, x_label="일자", y_label="시간(h)")
if (rows["가동시간(h)"] < 0).any():
    st.caption("가동시간이 음수인 정정 행은 그 날짜의 합계에 포함해 그렸습니다.")

st.subheader("일별 기록")
st.dataframe(
    rows[["일자", "계획시간(h)", "가동시간(h)", "비고"]].fillna({"비고": ""}),
    hide_index=True,
    width="stretch",
)
