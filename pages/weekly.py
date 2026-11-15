"""주간 비교 페이지: 지난주(W44) → 이번 주(W45) 장비별 가동률 증감과 비고 행."""
from pathlib import Path

import pandas as pd
import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
PREV_FILE = DATA / "readiness_W44.csv"  # 지난주
CUR_FILE = DATA / "readiness_W45.csv"   # 이번 주


@st.cache_data
def _load(path: str):
    return calc.load_readiness(path)


prev = _load(str(PREV_FILE))
cur = _load(str(CUR_FILE))
cmp = calc.compare_weeks(prev, cur)

st.title("주간 비교")
st.caption("지난주(W44) → 이번 주(W45) 장비별 가동률(%)과 증감(%p)")

up = cmp[cmp["증감"] > 0].head(3)
down = cmp[cmp["증감"] < 0].sort_values("증감").head(3)

c1, c2 = st.columns(2)
with c1:
    st.subheader("상승 상위 3")
    if up.empty:
        st.info("가동률이 오른 장비가 없습니다.")
    else:
        st.dataframe(up, hide_index=True, width="stretch")
with c2:
    st.subheader("하락 상위 3")
    if down.empty:
        st.info("가동률이 내린 장비가 없습니다.")
    else:
        st.dataframe(down, hide_index=True, width="stretch")

st.subheader("전체 장비 (증감이 큰 순서)")
st.dataframe(cmp, hide_index=True, width="stretch")

st.subheader("비고가 있는 기록")
notes = pd.concat([prev.assign(주차="W44"), cur.assign(주차="W45")], ignore_index=True)
notes = notes[notes["비고"].fillna("").str.strip() != ""]
if notes.empty:
    st.info("비고가 적힌 기록이 없습니다.")
else:
    st.dataframe(
        notes[["주차", "일자", "장비코드", "장비명", "계획시간(h)", "가동시간(h)", "비고"]],
        hide_index=True,
        width="stretch",
    )
