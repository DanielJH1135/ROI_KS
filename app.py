import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime

# 설정 부분은 동일
CONFIG = {
    "주차장 태양광": {"unit": "면수(대)", "capa_per_unit": 3.5, "rent_per_kw": 25000},
    "축사/창고 태양광": {"unit": "면적(평)", "capa_per_unit": 0.5, "rent_per_kw": 20000},
    "건물 옥상 태양광": {"unit": "면적(평)", "capa_per_unit": 0.4, "rent_per_kw": 22000}
}

st.set_page_config(page_title="태양광 수익 시뮬레이터", layout="wide")
st.title("☀️ 태양광 발전 사업 수익 분석 시스템")

# 1. 항목 선택 및 데이터 입력
selected_items = st.multiselect("분석할 항목을 선택하세요", list(CONFIG.keys()))
calc_results = {}

if selected_items:
    cols = st.columns(len(selected_items))
    for i, item in enumerate(selected_items):
        with cols[i]:
            conf = CONFIG[item]
            val = st.number_input(f"{item} ({conf['unit']})", value=20, key=f"in_{item}")
            capa = val * conf['capa_per_unit']
            rent = capa * conf['rent_per_kw']
            calc_results[item] = {"용량": capa, "수익": rent}
            st.metric("예상 용량", f"{capa:,.1f} kW")
            st.metric("연간 임대료", f"{int(rent):,} 원")

    # 2. 요약 및 PDF 발행
    st.divider()
    total_rent = sum(res["수익"] for res in calc_results.values())
    client_name = st.text_input("고객사명", placeholder="예: 제일축산")

    if st.button("PDF 견적서 다운로드"):
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # --- [핵심] 한글 폰트 추가 및 적용 ---
            # 깃허브에 올린 폰트 파일명과 일치해야 합니다.
            pdf.add_font('Nanum', '', 'NanumGothic.ttf', unicode=True)
            pdf.set_font('Nanum', '', 16)
            
            pdf.cell(0, 20, txt="태양광 발전 사업 임대 견적서", ln=True, align='C')
            pdf.set_font('Nanum', '', 12)
            pdf.cell(0, 10, txt=f"고객사: {client_name}", ln=True)
            pdf.cell(0, 10, txt=f"발행일: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
            pdf.ln(10)
            
            for item, res in calc_results.items():
                txt_line = f"• {item}: {res['용량']:.1f}kW (연 임대료: {int(res['수익']):,}원)"
                pdf.cell(0, 10, txt=txt_line, ln=True)
            
            pdf.ln(10)
            pdf.set_font('Nanum', '', 14)
            pdf.cell(0, 10, txt=f"최종 합계 임대료: 연 {int(total_rent):,}원", ln=True)
            
            # 한글 처리를 위해 output 방식을 수정
            pdf_bytes = pdf.output(dest='S').encode('utf-8') # utf-8로 인코딩
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="Solar_Proposal_{client_name}.pdf" style="text-decoration:none;"><button style="padding:10px 20px; background-color:#FF4B4B; color:white; border:none; border-radius:5px; cursor:pointer;">견적서 저장하기</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.info("NanumGothic.ttf 파일이 깃허브에 잘 올라가 있는지 확인해 주세요.")
