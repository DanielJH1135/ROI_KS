import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime, timedelta, timezone
import os

# [설정] 사업 데이터 로직 (2026년 3월 런칭 예정 기준)
CONFIG = {
    "주차장 태양광": {"unit": "면수(대)", "capa_per_unit": 3.5, "rent_per_kw": 25000},
    "축사/창고 태양광": {"unit": "면적(평)", "capa_per_unit": 0.5, "rent_per_kw": 20000},
    "건물 옥상 태양광": {"unit": "면적(평)", "capa_per_unit": 0.4, "rent_per_kw": 22000}
}

st.set_page_config(page_title="KS 에너지 수익 분석기", layout="wide")

st.title("☀️ 태양광 발전 사업 수익 분석 시스템")
st.write("법인 영업을 위한 맞춤형 임대 수익 산출 도구입니다.")

# --- 1. 담당자 정보 입력 ---
st.sidebar.header("🏢 담당자 정보")
sender_info = st.sidebar.text_input("회사명 (담당자 성함 및 직함)", value="KS 에너지 (OOO 팀장)")
sender_contact = st.sidebar.text_input("담당자 연락처", value="010-XXXX-XXXX")

# --- 2. 사업지 상세 입력 ---
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
            with col2: st.metric("예상 용량", f"{capa:,.1f} kW")
            with col3: st.metric("연간 임대료", f"{int(rent):,} 원")

    st.divider()
    total_capa = sum(res["용량"] for res in calc_results.values())
    total_rent = sum(res["수익"] for res in calc_results.values())

    st.subheader("📊 전체 분석 요약")
    c1, c2, c3 = st.columns(3)
    c1.metric("총 설치 용량", f"{total_capa:,.1f} kW")
    c2.metric("총 연간 수익", f"{int(total_rent):,} 원")
    c3.metric("월 평균 수익", f"{int(total_rent/12):,} 원")

    st.divider()
    st.subheader("📩 견적서 발행")
    client_name = st.text_input("수신처 (법인명 또는 성함)", value="", placeholder="수신처를 입력해 주세요")

    # --- [수정] 미리보기 팝업 함수 (브라우저 차단 해결 및 에러 방지) ---
    @st.dialog("📋 견적서 미리보기", width="large")
    def show_pdf_preview(pdf_bytes, client_name):
        st.write("아래 견적서 내용을 확인해 주세요.")
        
        # Base64 변환
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # iframe 대신 embed 태그 사용 (Chrome/Edge 차단 확률 낮음)
        # 만약 여전히 차단된다면 브라우저의 '팝업 및 리다이렉션' 허용이 필요할 수 있습니다.
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="550" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        st.divider()
        # 에러 방지를 위해 라벨의 이모지를 제거하고 매개변수를 단순화했습니다.
        st.download_button(
            label="PDF 파일 저장하기",
            data=pdf_bytes,
            file_name=f"Solar_Proposal_{client_name}.pdf",
            mime="application/pdf"
        )
        if st.button("창 닫기"):
            st.rerun()

    # 실행 버튼
    if st.button("🔍 견적서 미리보기 및 발행"):
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
                pdf.cell(0, 20, txt="태양광 발전 사업 제안서", ln=True, align='R')
                pdf.ln(10)
                
                # KST 시간 설정 (2026년 현재 시점 기준)
                kst = timezone(timedelta(hours=9))
                current_now = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
                
                pdf.set_font('Nanum', '', 11)
                pdf.set_fill_color(245, 245, 245)
                pdf.cell(95, 10, txt=f" 수신: {client_name}", border=1, ln=0, fill=True)
                pdf.cell(95, 10, txt=f" 발신: {sender_info}", border=1, ln=1, fill=True)
                pdf.cell(95, 10, txt=f" 일자: {current_now}", border=1, ln=0)
                pdf.cell(95, 10, txt=f" 연락처: {sender_contact}", border=1, ln=1)
                pdf.ln(10)

                # 분석 내역 표
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

                pdf.cell(140, 12, "총 합계 수익 (연간)", border=1, align='C', fill=True)
                pdf.cell(50, 12, f"{int(total_rent):,} 원", border=1, align='R', fill=True)
                pdf.ln(20)

                pdf.set_font('Nanum', '', 9)
                pdf.set_text_color(120, 120, 120)
                pdf.multi_cell(0, 6, txt="* 본 제안서는 입력된 기초 데이터를 바탕으로 산출된 예상 결과입니다.\n"
                                         "* 실제 시공 가능 여부 및 최종 용량은 현장 실사 후 확정됩니다.")

                show_pdf_preview(pdf.output(), client_name)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("좌측 또는 상단에서 분석할 사업 항목을 먼저 선택해 주세요.")
