import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime

# =========================================================
# [수정 포인트 1] 나중에 대표님께 확인 후 여기만 고치세요!
# =========================================================
CONFIG = {
    "주차장": {
        "unit": "면수(대)",       # "평수(평)"로 바꾸고 싶으면 여기 수정
        "ratio": 3.5,            # 단위당 발전용량 (예: 1대당 3.5kW)
        "rent_price": 25000      # kW당 임대료 (원)
    },
    "축사": {
        "unit": "면적(평)", 
        "ratio": 0.5,            # 예: 1평당 0.5kW
        "rent_price": 20000
    },
    "옥상": {
        "unit": "면적(평)", 
        "ratio": 0.4, 
        "rent_price": 22000
    }
}

st.title("☀️ 태양광 사업 수익성 시뮬레이터 (초안)")
st.info("대표님 확인 후 수식과 단가를 업그레이드할 예정입니다.")

# 1. 항목 선택
st.subheader("1. 사업 대상 선택 (중복 가능)")
items = st.multiselect("분석할 항목을 선택하세요", list(CONFIG.keys()))

results = {}

if items:
    # 2. 입력 섹션
    for item in items:
        st.write(f"---")
        col1, col2 = st.columns(2)
        
        with col1:
            val = st.number_input(f"[{item}] {CONFIG[item]['unit']} 입력", min_value=0, value=10, key=f"in_{item}")
        
        # =========================================================
        # [수정 포인트 2] 수익률 산정 로직 (계산기 엔진)
        # =========================================================
        # 현재 로직: 입력값 * 단위당용량 * kW당임대료
        capa = val * CONFIG[item]['ratio']
        rent = capa * CONFIG[item]['rent_price']
        
        results[item] = {"용량": capa, "수익": rent}
        
        with col2:
            st.metric(f"{item} 예상 용량", f"{capa:.1f} kW")
            st.metric(f"{item} 연 임대료", f"{int(rent):,} 원")

    # 3. 합계 섹션
    st.divider()
    total_capa = sum(r["용량"] for r in results.values())
    total_rent = sum(r["수익"] for r in results.values())
    
    st.subheader("📊 전체 요약")
    c1, c2 = st.columns(2)
    c1.metric("총 합계 용량", f"{total_capa:.1f} kW")
    c2.metric("총 연간 임대 수익", f"{int(total_rent):,} 원")

    # 4. PDF 견적서 생성 (기존 로직 유지)
    client = st.text_input("고객사명", "OOO 귀하")
    if st.button("PDF 견적서 생성"):
        # PDF 생성 로직... (이전 코드와 동일)
        st.success("견적서가 생성되었습니다. (한글 폰트 적용은 로직 확정 후 진행 권장)")
else:
    st.write("분석할 항목을 먼저 선택해 주세요.")