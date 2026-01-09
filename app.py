import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# [설정] 파일 및 핵심 컬럼 설정
# ==========================================
FILE_NAME = 'database.xlsx'  # 엑셀 파일 이름

# 엑셀의 제목줄(Header)과 토씨 하나 안 틀리고 똑같아야 하는 설정값입니다.
# 보내주신 항목명을 기준으로 작성했습니다.
KEY_COLS = {
    'name': '제품명',         # 알림창에 띄울 이름 1
    'sub_name': '제품명(한글)', # 알림창에 띄울 이름 2 (보조)
    'exp_date': '유통기한',    # 날짜 계산용 필수 항목
    'danger': '유해 및 위험성'  # 알림창에 같이 보여줄 정보
}
# ==========================================

st.set_page_config(page_title="시약 관리 시스템", page_icon="🧪", layout="wide")

def load_data():
    try:
        # 엑셀의 모든 컬럼, 모든 데이터를 그대로 가져옵니다.
        df = pd.read_excel(FILE_NAME)
        
        # 유통기한 계산을 위해 '유통기한' 열만 날짜 형식으로 바꿉니다.
        if KEY_COLS['exp_date'] in df.columns:
            df[KEY_COLS['exp_date']] = pd.to_datetime(df[KEY_COLS['exp_date']], errors='coerce')
        
        # '등록일'이 있다면 날짜 보기 좋게 변환 (계산에는 안 씀)
        if '등록일' in df.columns:
             df['등록일'] = pd.to_datetime(df['등록일'], errors='coerce')
             
        return df
    except FileNotFoundError:
        st.error(f"❌ '{FILE_NAME}' 파일이 없습니다. 깃허브에 올리셨나요?")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
        return pd.DataFrame()

# 1. 헤더 섹션
st.title("🧪 연구실 시약 종합 관리 DB")
today = datetime.now()
st.write(f"📅 **기준일:** {today.strftime('%Y-%m-%d')}")

df = load_data()

if not df.empty:
    # ----------------------------------------------------
    # 2. 유통기한 임박 알림 (핵심 기능)
    # ----------------------------------------------------
    if KEY_COLS['exp_date'] in df.columns:
        # D-Day 계산
        df['남은일수'] = (df[KEY_COLS['exp_date']] - today).dt.days + 1
        
        # 알림 조건
        alert_days = [10, 7, 5, 3, 1]
        
        # 10일 이하로 남은 것들 추출
        urgent_df = df[df['남은일수'] <= 10].sort_values(by='남은일수')
        
        st.divider()
        st.subheader("🚨 긴급 점검 (유통기한 임박)")
        
        if urgent_df.empty:
            st.success("✅ 현재 위험한 시약이 없습니다.")
        else:
            for i, row in urgent_df.iterrows():
                d_day = row['남은일수']
                
                # 데이터 가져오기 (없으면 빈칸)
                name = row.get(KEY_COLS['name'], "-")
                sub_name = row.get(KEY_COLS['sub_name'], "")
                danger = row.get(KEY_COLS['danger'], "")
                
                # 화면 표시 메시지
                msg_title = f"**{name}** ({sub_name})"
                msg_desc = f"위험성: {danger}" if danger else ""
                
                if d_day < 0:
                    st.error(f"❌ [폐기필요] {msg_title} | {abs(d_day)}일 지남! | {msg_desc}")
                elif d_day in alert_days:
                    st.warning(f"⚠️ [확인요망] {msg_title} | 딱 {d_day}일 남음 | {msg_desc}")
                elif 0 <= d_day <= 10:
                    st.info(f"ℹ️ [관심] {msg_title} | {d_day}일 남음")

    # ----------------------------------------------------
    # 3. 전체 데이터베이스 (요청하신 모든 정보 표시)
    # ----------------------------------------------------
    st.divider()
    st.subheader("📋 전체 시약 상세 리스트")
    
    # 검색 기능 (제품명, 한글명, CAS No, 제조사 등 통합 검색)
    search_term = st.text_input("🔍 통합 검색 (이름, CAS No., 제조사 등 입력)", "")
    
    # 보여줄 데이터 복사
    display_df = df.copy()
    
    # 보기 좋게 날짜 포맷 변경
    if KEY_COLS['exp_date'] in display_df.columns:
        display_df[KEY_COLS['exp_date']] = display_df[KEY_COLS['exp_date']].dt.strftime('%Y-%m-%d')
    if '등록일' in display_df.columns:
        display_df['등록일'] = display_df['등록일'].dt.strftime('%Y-%m-%d')

    # 검색 필터
    if search_term:
        # 데이터프레임 전체에서 검색어가 포함된 행 찾기
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
        
    st.caption(f"총 {len(display_df)}개의 시약이 있습니다.")
    
    # ⭐️ 여기가 핵심: 14개 컬럼을 포함해 엑셀에 있는 모든걸 다 보여줍니다.
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("데이터를 불러오지 못했습니다.")
