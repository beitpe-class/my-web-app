"""장비 가동률 대시보드 · 정비 요청 접수 (교육용 가상 데이터)."""
import streamlit as st

import db

st.set_page_config(page_title="장비 가동률 대시보드", layout="wide")


@st.cache_resource
def _init_db() -> bool:
    """앱이 켜진 뒤 처음 한 번만 정비 요청 저장소를 준비한다."""
    db.init_db()
    return True


_init_db()

pg = st.navigation([
    st.Page("pages/summary.py", title="요약", default=True),
    st.Page("pages/equipment.py", title="장비별 상세"),
    st.Page("pages/weekly.py", title="주간 비교"),
    st.Page("pages/requests.py", title="정비 요청"),
])

st.caption("※ 이 화면의 부대 · 장비 · 수치는 모두 교육용 가상 데이터입니다.")

pg.run()
