"""요약 페이지: 이번 주 · 지난주 전체 가동률, 목표 대비, 장비별 가동률."""
from pathlib import Path

import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
CUR_FILE = DATA / "readiness_W45.csv"   # 이번 주
PREV_FILE = DATA / "readiness_W44.csv"  # 지난주
TARGET = 90.0


@st.cache_data
def _load(path: str):
    return calc.load_readiness(path)


cur = _load(str(CUR_FILE))
prev = _load(str(PREV_FILE))

cur_rate = calc.total_rate(cur)
prev_rate = calc.total_rate(prev)

st.title("요약")

c1, c2, c3 = st.columns(3)
c1.metric("이번 주 전체 가동률", f"{cur_rate:.1f}%", f"{cur_rate - prev_rate:+.1f}%p (지난주 대비)")
c2.metric("지난주 전체 가동률", f"{prev_rate:.1f}%")
c3.metric(f"목표 {TARGET:.0f}% 대비", f"{cur_rate - TARGET:+.1f}%p")

st.subheader("장비별 이번 주 가동률")
by_eq = calc.rate_by_equipment(cur)
st.bar_chart(by_eq, x="장비명", y="가동률", x_label="장비", y_label="가동률(%)")
