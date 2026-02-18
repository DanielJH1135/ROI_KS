import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime

# =========================================================
# [설정] 회사 기준 단가 및 용량 산정 로직
# =========================================================
CONFIG = {
    "주차장 태양광": {
        "unit": "면수(대)", 
        "capa_per_unit": 3.5,   # 1대당 3.5kW
        "rent_per_kw": 25000    # 1kW당 연 임대료 2.5만원
    },
    "축사/창고 태양광": {
        "unit": "면적(평)", 
        "capa_per_unit": 0.5,   # 1평당 0.5kW
        "rent_per_kw": 20000    # 1kW당 연 임대료 2만원
    },
    "건물 옥상 태양광": {
        "unit": "면적(평)", 
        "capa_per_unit": 0.4,   # 1평당 0.4kW
        "rent_per_kw": 22000    # 1kW당 연 임대료 2.2만원
    }
}

# 페이지 설정
st.set_page_config(page_title="태양광 수익 시뮬레이터", layout="wide")
st.title("☀️ 태양광 발전 사업 수익 분석 시스템")
st.write("법인 고객님의 부지 정보를 바탕으로 산출된 예상 임대 수익 보고서입니다.")

# 1. 항목 선택 및 데이터 입력
st.subheader("📍 사업 대상지 정보 입력")
selected_items = st.multiselect("분석할 항목을 선택하세요 (중복 선택 가능)", list(CONFIG.keys()))

calc_results = {}

if selected_items:
    cols = st.columns(len(selected_items))
    for i, item in enumerate(selected_items):
        with cols[i]:
            st.markdown(f"### {item}")
            conf = CONFIG[item]
            val = st.number_input(f"{conf['unit']} 입력", min_value=0, value=20, key=f"input_{item}")
            
            # 계산 로직
            capa = val * conf['capa_per_unit']
            rent = capa * conf['rent_per_kw']
            calc_results[item] = {"용량": capa, "수익": rent, "입력값": val, "단위": conf['unit']}
            
            st.metric("예상 설치 용량", f"{capa:,.1f} kW")
            st.metric("연간 확정 임대료", f"{int(rent):3,} 원")

    # 2. 종합 분석 결과
    st.divider()
    total_capa = sum(res["용량"] for res in calc_results.values())
    total_rent = sum(res["수익"] for res in calc_results.values())

    st.subheader("📊 종합 분석 요약")
    c1, c2, c3 = st.columns(3)
    c1.metric("총 합계 용량", f"{total_capa:,.1f} kW")
    c2.metric("총 연간 수익", f"{int(total_rent):3,} 원")
    c3.metric("월 평균 수익", f"{int(total_rent/12):3,} 원")

    # 3. PDF 견적서 발행 섹션
    st.divider()
    st.subheader("📩 정식 견적서 발행")
    client_name = st.text_input("고객사명 (또는 성함)", placeholder="예: (주)대한산업")

    if st.button("PDF 견적서 생성 및 다운로드"):
        try:
            # PDF 객체 생성 (fpdf2 기준)
            pdf = FPDF()
            pdf.add_page()
            
            # 한글 폰트 추가 (NanumGothic.ttf 파일이 깃허브에 있어야 함)
            pdf.add_font('Nanum', '', 'NanumGothic.ttf')
            pdf.set_font('Nanum', '', 20)
            
            # 타이틀
            pdf.cell(0, 20, txt="태양광 발전 사업 임대 견적서", ln=True, align='C')
            pdf.ln(10)
            
            # 기본 정보
            pdf.set_font('Nanum', '', 12)
            pdf.cell(0, 10, txt=f"고객사: {client_name}", ln=True)
            pdf.cell(0, 10, txt=f"발행일: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
            pdf.ln(5)
            pdf.cell(0, 0, txt="", border="T", ln=True) # 구분선
            pdf.ln(5)
            
            # 상세 내역
            for item, res in calc_results.items():
                line = f"• {item}: {res['입력값']}{res['단위']} -> 예상용량 {res['용량']:.1f}kW"
                pdf.cell(0, 10, txt=line, ln=True)
                rent_line = f"  (연간 임대료: {int(res['수익']):,} 원)"
                pdf.cell(0, 10, txt=rent_line, ln=True)
            
            pdf.ln(5)
            pdf.cell(0, 0, txt="", border="T", ln=True) # 구분선
            pdf.ln(5)
            
            # 합계
            pdf.set_font('Nanum', '', 15)
            pdf.cell(0, 10, txt=f"최종 합계 임대료: 연 {int(total_rent):,} 원", ln=True)
            
            # PDF 다운로드 링크 생성
            pdf_bytes = pdf.output() # fpdf2는 여기서 바로 바이트를 반환할 수 있음
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="Solar_Proposal_{client_name}.pdf" style="text-decoration:none;"><button style="padding:10px 20px; background-color:#FF4B4B; color:white; border:none; border-radius:5px; cursor:pointer;">견적서 파일 저장하기</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("견적서 생성이 완료되었습니다. 위 버튼을 눌러 저장하세요.")
            
        except Exception as e:
            st.error(f"PDF 생성 중 오류가 발생했습니다: {e}")
            st.info("NanumGothic.ttf 파일이 깃허브 저장소에 있는지 다시 확인해 주세요.")

else:
    st.info("분석을 시작하려면 위에서 사업 대상지를 선택해 주세요.")
