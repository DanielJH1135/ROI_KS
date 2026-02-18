import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime
import os

# [설정] 사업 데이터 로직
CONFIG = {
    "주차장 태양광": {"unit": "면수(대)", "capa_per_unit": 3.5, "rent_per_kw": 25000},
    "축사/창고 태양광": {"unit": "면적(평)", "capa_per_unit": 0.5, "rent_per_kw": 20000},
    "건물 옥상 태양광": {"unit": "면적(평)", "capa_per_unit": 0.4, "rent_per_kw": 22000}
}

st.set_page_config(page_title="태양광 수익 시뮬레이터", layout="wide")
st.title("☀️ 태양광 발전 사업 수익 분석 시스템")

# 1. 정보 입력
st.sidebar.header("🏢 회사 및 고객 정보")
company_name = st.sidebar.text_input("우리 회사명", "KS 에너지")
company_contact = st.sidebar.text_input("회사 연락처", "010-XXXX-XXXX")

st.subheader("📍 사업지 상세 입력")
selected_items = st.multiselect("분석 항목 선택", list(CONFIG.keys()))
calc_results = {}

if selected_items:
    cols = st.columns(len(selected_items))
    for i, item in enumerate(selected_items):
        with cols[i]:
            conf = CONFIG[item]
            val = st.number_input(f"{item} ({conf['unit']})", min_value=0, value=50, key=f"in_{item}")
            capa = val * conf['capa_per_unit']
            rent = capa * conf['rent_per_kw']
            calc_results[item] = {"용량": capa, "수익": rent, "입력값": val, "단위": conf['unit']}
            st.metric(f"{item} 예상용량", f"{capa:,.1f} kW")

    total_capa = sum(res["용량"] for res in calc_results.values())
    total_rent = sum(res["수익"] for res in calc_results.values())

    st.divider()
    st.subheader("📩 견적서 발행 상세")
    client_name = st.text_input("수신처 (법인/성함)", "제일축산 귀하")

    if st.button("전문 PDF 견적서 생성"):
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # 폰트 등록
            pdf.add_font('Nanum', '', 'NanumGothic.ttf')
            
            # --- 상단: 로고 및 타이틀 ---
            if os.path.exists("logo.png"):
                pdf.image("logo.png", x=10, y=8, w=30) # 로고 위치와 크기 조절
            
            pdf.set_font('Nanum', '', 25)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(0, 20, txt="태양광 발전 사업 제안서", ln=True, align='R')
            pdf.ln(10)
            
            # --- 중단: 기본 정보 테이블 ---
            pdf.set_font('Nanum', '', 11)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(95, 10, txt=f" 수신: {client_name}", border=1, ln=0, fill=True)
            pdf.cell(95, 10, txt=f" 발신: {company_name}", border=1, ln=1, fill=True)
            pdf.cell(95, 10, txt=f" 일자: {datetime.now().strftime('%Y-%m-%d')}", border=1, ln=0)
            pdf.cell(95, 10, txt=f" 담당: {company_contact}", border=1, ln=1)
            pdf.ln(10)

            # --- 하단: 상세 분석 내역 ---
            pdf.set_font('Nanum', '', 14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, txt="[ 사업 규모 및 예상 수익 ]", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Nanum', '', 11)
            
            # 표 헤더
            pdf.cell(60, 10, "구분", border=1, align='C', fill=True)
            pdf.cell(40, 10, "규모", border=1, align='C', fill=True)
            pdf.cell(40, 10, "예상용량", border=1, align='C', fill=True)
            pdf.cell(50, 10, "연간 임대료", border=1, align='C', fill=True)
            pdf.ln()

            for item, res in calc_results.items():
                pdf.cell(60, 10, item, border=1)
                pdf.cell(40, 10, f"{res['입력값']}{res['단위']}", border=1, align='C')
                pdf.cell(40, 10, f"{res['용량']:.1f} kW", border=1, align='C')
                pdf.cell(50, 10, f"{int(res['수익']):,} 원", border=1, align='R')
                pdf.ln()

            # 합계 행
            pdf.set_font('Nanum', '', 12)
            pdf.cell(140, 12, "총 합계", border=1, align='C', fill=True)
            pdf.cell(50, 12, f"{int(total_rent):,} 원", border=1, align='R', fill=True)
            pdf.ln(15)

            # --- 안내 사항 ---
            pdf.set_font('Nanum', '', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 7, txt="* 본 견적은 입력된 면적을 기반으로 산출된 예상 수치이며, 실제 현장 실사 후 변동될 수 있습니다.\n"
                                     "* 임대료 지급 방식 및 계약 기간은 법인별 세부 협의에 따릅니다.\n"
                                     "* 태양광 설치로 인한 축사 및 건물의 구조적 안전성 검토가 선행될 예정입니다.")

            # PDF 데이터 전송
            pdf_bytes = pdf.output()
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="Solar_Proposal_{client_name}.pdf" style="text-decoration:none;"><button style="width:100%; padding:15px; background-color:#2E7D32; color:white; border:none; border-radius:10px; font-size:18px; cursor:pointer;">📥 전문 견적서 다운로드 (PDF)</button></a>'
            st.markdown(href, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"오류 발생: {e}")
