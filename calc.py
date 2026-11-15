"""가동률 계산 함수 (교육용 가상 데이터).

가동률 = 가동시간 합계 ÷ 계획시간 합계 × 100
- 일별 가동률의 평균을 쓰지 않는다.
- 가동시간이 음수인 정정 행도 지우지 않고 합계에 포함한다.
"""
from __future__ import annotations

import pandas as pd

PLAN_COL = "계획시간(h)"
RUN_COL = "가동시간(h)"


def _rate(run_sum: float, plan_sum: float) -> float:
    """합계 ÷ 합계 × 100, 소수 첫째 자리. 계획시간 합계가 0이면 0.0."""
    if plan_sum == 0:
        return 0.0
    return round(float(run_sum) / float(plan_sum) * 100, 1)


def load_readiness(path) -> pd.DataFrame:
    """가동 현황 CSV를 읽는다. 행은 지우지 않는다 (음수 정정 행 포함)."""
    return pd.read_csv(path, encoding="utf-8-sig")


def total_rate(df: pd.DataFrame) -> float:
    """전체 가동률(%), 소수 첫째 자리."""
    return _rate(df[RUN_COL].sum(), df[PLAN_COL].sum())


def rate_by_equipment(df: pd.DataFrame) -> pd.DataFrame:
    """장비별 가동률. 열: 장비코드 · 장비명 · 계획시간 · 가동시간 · 가동률."""
    out = (
        df.groupby(["장비코드", "장비명"], as_index=False)[[PLAN_COL, RUN_COL]]
        .sum()
        .rename(columns={PLAN_COL: "계획시간", RUN_COL: "가동시간"})
    )
    out["가동률"] = [_rate(r, p) for r, p in zip(out["가동시간"], out["계획시간"])]
    return out[["장비코드", "장비명", "계획시간", "가동시간", "가동률"]]


def compare_weeks(prev: pd.DataFrame, cur: pd.DataFrame) -> pd.DataFrame:
    """두 주의 장비별 가동률 비교. 열: 장비코드 · 장비명 · 가동률_이전 · 가동률_이번 · 증감 (증감이 큰 순서)."""
    p = rate_by_equipment(prev)[["장비코드", "장비명", "가동률"]].rename(columns={"가동률": "가동률_이전"})
    c = rate_by_equipment(cur)[["장비코드", "가동률"]].rename(columns={"가동률": "가동률_이번"})
    out = p.merge(c, on="장비코드", how="outer")
    if out["장비명"].isna().any():
        names = rate_by_equipment(cur).set_index("장비코드")["장비명"]
        out["장비명"] = out["장비명"].fillna(out["장비코드"].map(names))
    out["증감"] = (out["가동률_이번"] - out["가동률_이전"]).round(1)
    out = out.sort_values("증감", ascending=False, na_position="last").reset_index(drop=True)
    return out[["장비코드", "장비명", "가동률_이전", "가동률_이번", "증감"]]
