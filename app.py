import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime
import os

# [수정 포인트] 나중에 대표님께 확인 후 이 숫자들만 고치시면 됩니다.
CONFIG = {
    "주차장 태양광": {"unit": "면수(대)", "capa_per_unit": 3.5, "rent_per_kw": 25000},
    "축사/창고 태양광": {"unit": "면적(평)", "capa_per_unit": 0.5, "rent_per_kw": 20000},
    "건물 옥상 태양광": {"unit": "면적(평)", "capa_per_unit": 0.4, "rent_per_kw": 22000}
}

st.set_page_config(page_title="태양광 수익 시뮬레이터", layout="wide")
st.title("☀️ 태양광 발전 사업 수익 분석 시스템")
st.write("법인 고객님을 위한 맞춤형 임대 수익 및 설치 용량 분석 결과입니다.")

# 1. 항목 선택 및 데이터 입력
st.subheader("📍 사업 대상지 정보")
selected_items = st.multiselect("분석할 항목을 선택하세요 (중복 선택 가능)", list(CONFIG.keys()))

calc_results = {}

if selected_items:
    cols = st.columns(len(selected_items))
    for i, item in enumerate(selected_items):
        with cols[i]:
            st.markdown(f"### {item}")
            conf = CONFIG[item]
            val = st.number_input(f"{conf['unit']} 입력", min_value=0, value=20, key=f"input_{item}")
            
            # 계산 로직: 용량(kW) = 입력값 * 단위당 용량 / 수익 = 용량 * kW당 단가
            capa = val * conf['capa_per_unit']
            rent = capa * conf['rent_per_kw']
            calc_results[item] = {"용량": capa, "수익": rent, "입력값": val}
            
            st.metric("예상 용량", f"{capa:,.1f} kW")
            st.metric("연간 임대료", f"{int(rent):,} 원")

    # 2. 종합 요약
    st.divider()
    total_capa = sum(res["용량"] for res in calc_results.values())
    total_rent = sum(res["수익"] for res in calc_results.values())

    st.subheader("📊 종합 분석 결과")
    c1, c2, c3 = st.columns(3)
    c1.metric("총 설치 용량", f"{total_capa:,.1f} kW")
    c2.metric("총 연간 수익", f"{int(total_rent):,} 원")
    c3.metric("월평균 수익", f"{int(total_rent/12):,} 원")

    # 3. PDF 견적서 생성 섹션
    st.divider()
    st.subheader("📩 정식 견적서 발행")
    client_name = st.text_input("고객사명 (또는 성함)", placeholder="예: (주)에너지솔루션")

    if st.button("PDF 견적서 다운로드"):
        # PDF 생성 객체
        pdf = FPDF()
        pdf.add_page()
        
        # [중요] 한글 폰트 설정 (아래 2단계 설명 참고)
        # pdf.add_font('Nanum', '', 'NanumGothic.ttf', unicode=True)
        # pdf.set_font('Nanum', '', 16)
        
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 20, f"Solar Project Proposal", 0, 1, 'C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Client: {client_name}", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
        pdf.ln(10)
        
        for item, res in calc_results.items():
            line = f"- {item}: {res['용량']:.1f}kW (Rent: {int(res['수익']):,} KRW/year)"
            pdf.cell(0, 10, line, 0, 1)
            
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f"Total Annual Income: {int(total_rent):,} KRW", 0, 1)
        
        # PDF 다운로드 링크 생성
        pdf_output = pdf.output(dest='S').encode('latin-1', errors='ignore')
        b64 = base64.b64encode(pdf_output).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="Solar_Proposal_{client_name}.pdf" style="text-decoration:none;"><button style="padding:10px 20px; background-color:#FF4B4B; color:white; border:none; border-radius:5px; cursor:pointer;">견적서 파일 저장하기</button></a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.info("분석을 시작하려면 위에서 사업 대상을 선택해 주세요.")
