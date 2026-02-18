import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime, timedelta, timezone
import os

# [설정] 사업 데이터 로직 (추후 대표님 확인 후 수정하세요)
CONFIG = {
    "주차장 태양광": {"unit": "면수(대)", "capa_per_unit": 3.5, "rent_per_kw": 25000},
    "축사/창고 태양광": {"unit": "면적(평)", "capa_per_unit": 0.5, "rent_per_kw": 20000},
    "건물 옥상 태양광": {"unit": "면적(평)", "capa_per_unit": 0.4, "rent_per_kw": 22000}
}

st.set_page_config(page_title="KS 에너지 수익 분석기", layout="wide")

# 상단 제목
st.title("☀️ 태양광 발전 사업 수익 분석 시스템")
st.write("법인 영업을 위한 맞춤형 임대 수익 산출 도구입니다.")

# --- 1. 담당자 정보 입력 (사이드바) ---
st.sidebar.header("🏢 담당자 정보")
sender_info = st.sidebar.text_input(
    "회사명 (담당자 성함 및 직함)", 
    value="KS 에너지 (OOO 팀장)",
    help="PDF 견적서 '발신'란에 표시될 정보입니다."
)
sender_contact = st.sidebar.text_input(
    "담당자 연락처", 
    value="010-XXXX-XXXX",
    help="고객이 문의할 연락처를 입력하세요."
)

# --- 2. 사업지 상세 입력 (메인 화면) ---
st.subheader("📍 사업지 상세 정보 입력")
selected_items = st.multiselect("분석할 항목을 모두 선택하세요", list(CONFIG.keys()))

calc_results = {}

if selected_items:
    for item in selected_items:
        with st.expander(f"🔍 {item} 상세 설정", expanded=True):
            conf = CONFIG[item]
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                val = st.number_input(f"{item} {conf['unit']}를 입력하세요", min_value=0, value=100, key=f"in_{item}")
            
            capa = val * conf['capa_per_unit']
            rent = capa * conf['rent_per_kw']
            calc_results[item] = {"용량": capa, "수익": rent, "입력값": val, "단위": conf['unit']}
            
            with col2:
                st.metric("예상 용량", f"{capa:,.1f} kW")
            with col3:
                st.metric("연간 임대료", f"{int(rent):,} 원")

    # --- 3. 종합 요약 ---
    st.divider()
    total_capa = sum(res["용량"] for res in calc_results.values())
    total_rent = sum(res["수익"] for res in calc_results.values())

    st.subheader("📊 전체 분석 요약")
    c1, c2, c3 = st.columns(3)
    c1.metric("총 설치 용량", f"{total_capa:,.1f} kW")
    c2.metric("총 연간 수익", f"{int(total_rent):,} 원")
    c3.metric("월 평균 수익", f"{int(total_rent/12):,} 원")

    # --- 4. PDF 견적서 발행 ---
    st.divider()
    st.subheader("📩 정식 견적서 발행")
    # 수신처 예시 법인명을 삭제하고 빈 칸으로 설정
    client_name = st.text_input("수신처 (법인명 또는 성함)", value="", placeholder="수신처를 입력해 주세요")

    if st.button("전문 PDF 견적서 생성 및 다운로드"):
        if not client_name:
            st.error("수신처를 입력해야 견적서 생성이 가능합니다.")
        else:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.add_font('Nanum', '', 'NanumGothic.ttf')
                
                if os.path.exists("logo.png"):
                    pdf.image("logo.png", x=10, y=8, w=30)
                
                pdf.set_font('Nanum', '', 25)
                pdf.set_text_color(40, 40, 40)
                pdf.cell(0, 20, txt="태양광 발전 사업 제안서", ln=True, align='R')
                pdf.ln(10)
                
                # --- [수정] 한국 시간대(KST) 설정 ---
                kst = timezone(timedelta(hours=9)) # UTC+9 설정
                current_now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
                
                pdf.set_font('Nanum', '', 11)
                pdf.set_fill_color(245, 245, 245)
                pdf.cell(95, 10, txt=f" 수신: {client_name}", border=1, ln=0, fill=True)
                pdf.cell(95, 10, txt=f" 발신: {sender_info}", border=1, ln=1, fill=True)
                pdf.cell(95, 10, txt=f" 일자: {current_now}", border=1, ln=0)
                pdf.cell(95, 10, txt=f" 연락처: {sender_contact}", border=1, ln=1)
                pdf.ln(10)

                # 상세 내역 표
                pdf.set_font('Nanum', '', 14)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 10, txt="[ 사업 규모 및 예상 수익 분석 ]", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Nanum', '', 10)
                
                pdf.set_fill_color(230, 230, 230)
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

                pdf.set_font('Nanum', '', 12)
                pdf.cell(140, 12, "총 합계 수익 (연간)", border=1, align='C', fill=True)
                pdf.cell(50, 12, f"{int(total_rent):,} 원", border=1, align='R', fill=True)
                pdf.ln(20)

                # 유의사항
                pdf.set_font('Nanum', '', 9)
                pdf.set_text_color(120, 120, 120)
                pdf.multi_cell(0, 6, txt="* 본 제안서는 입력된 기초 데이터를 바탕으로 산출된 예상 결과입니다.\n"
                                         "* 실제 시공 가능 여부 및 최종 용량은 현장 실사(구조 진단 등) 후 확정됩니다.\n"
                                         "* 임대 조건 및 계약 관련 세부 사항은 별도 협의에 따릅니다.")

                pdf_bytes = pdf.output()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="Solar_Proposal_{client_name}.pdf" style="text-decoration:none;"><button style="width:100%; padding:15px; background-color:#1E88E5; color:white; border:none; border-radius:10px; font-size:18px; cursor:pointer; font-weight:bold;">📥 전문 견적서 PDF 다운로드</button></a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success(f"{current_now} 기준 견적서가 생성되었습니다.")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("좌측 또는 상단에서 분석할 사업 항목을 먼저 선택해 주세요.")
