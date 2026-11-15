"""정비 요청 페이지: 등록 · 목록(상태별) · 상태 변경. 저장 · 조회는 db.py 함수로만 한다."""
from pathlib import Path

import pandas as pd
import streamlit as st

import calc
import db

DATA = Path(__file__).resolve().parents[1] / "data"
WEEK_FILES = [DATA / "readiness_W44.csv", DATA / "readiness_W45.csv"]
COLUMNS = {
    "id": "번호", "created_at": "접수 시각", "equipment_code": "장비코드", "장비명": "장비명",
    "title": "요청 내용", "priority": "우선순위", "requester_role": "요청자 역할", "status": "상태",
}


@st.cache_data
def _equipment() -> pd.DataFrame:
    """CSV에 나오는 장비코드 · 장비명 목록."""
    frames = [calc.load_readiness(str(f))[["장비코드", "장비명"]] for f in WEEK_FILES]
    return pd.concat(frames).drop_duplicates("장비코드").sort_values("장비코드").reset_index(drop=True)


def _flash(kind: str, msg: str) -> None:
    """다시 그린 뒤에도 보이도록 안내 문구를 남긴다."""
    st.session_state["requests_flash"] = (kind, msg)


st.title("정비 요청")
st.caption(f"지금 저장소: **{db.backend_name()}**")

if "requests_flash" in st.session_state:
    kind, msg = st.session_state.pop("requests_flash")
    getattr(st, kind)(msg)

equipment = _equipment()
names = dict(zip(equipment["장비코드"], equipment["장비명"]))

# ── 등록 ──
st.subheader("요청 등록")
with st.form("new_request", clear_on_submit=True):
    code = st.selectbox("장비", list(names), format_func=lambda c: f"{c} · {names[c]}")
    title = st.text_area("요청 내용", placeholder="예: 냉각 팬 소음 점검 요청")
    c1, c2 = st.columns(2)
    priority = c1.selectbox("우선순위", db.PRIORITIES, index=db.PRIORITIES.index("보통"))
    role = c2.text_input("요청자 역할명", placeholder="예: 정비 담당 (실명은 쓰지 않습니다)")
    if st.form_submit_button("등록", type="primary"):
        try:
            rid = db.add_request(code, title, priority, role)
            _flash("success", f"{rid}번 요청을 '접수' 상태로 등록했습니다.")
            st.rerun()
        except ValueError as e:
            st.error(str(e))

# ── 목록 ──
st.subheader("요청 목록")
status = st.selectbox("상태", ["전체", *db.STATUSES])
rows = db.list_requests(None if status == "전체" else status)
if rows.empty:
    st.info("해당하는 정비 요청이 없습니다.")
else:
    view = rows.assign(장비명=rows["equipment_code"].map(names))
    st.dataframe(view[list(COLUMNS)].rename(columns=COLUMNS), hide_index=True, width="stretch")

# ── 상태 변경 ──
st.subheader("상태 변경")
all_rows = db.list_requests()
if all_rows.empty:
    st.info("상태를 바꿀 요청이 아직 없습니다.")
else:
    labels = {int(r.id): f"{r.id}번 · {r.equipment_code} · {r.title} (지금: {r.status})"
              for r in all_rows.itertuples()}
    with st.form("change_status"):
        rid = st.selectbox("번호", list(labels), format_func=labels.get)
        new_status = st.selectbox("바꿀 상태", db.STATUSES)
        if st.form_submit_button("상태 변경"):
            try:
                db.update_status(rid, new_status)
                _flash("success", f"{rid}번 요청을 '{new_status}' 상태로 바꿨습니다.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
