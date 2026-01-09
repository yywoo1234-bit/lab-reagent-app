import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# [설정] 핵심 컬럼 이름 (수정 X)
# ==========================================
FILE_NAME = 'database.xlsx'

# 엑셀의 제목줄에 이 단어들이 포함되어 있어야 합니다.
KEY_COLS = {
    'name': '제품명',
    'sub_name': '제품명(한글)',
    'exp_date': '유통기한',
    'danger': '유해 및 위험성' # 띄어쓰기 주의!
}
# ==========================================

st.set_page_config(page_title="시약 관리 시스템", page_icon="🧪", layout="wide")

def load_data():
    try:
        df = pd.read_excel(FILE_NAME)
        
        # [중요] 엑셀 제목의 띄어쓰기를 자동으로 없애줍니다. (에러 방지)
        # 예: " 제품명 " -> "제품명"
        df.columns = df.columns.str.strip()
        
        # 줄바꿈 문자(\n)가 있으면 제거
        df.columns = df.columns.str.replace('\n', '').str.replace('\r', '')

        # -----------------------------------------------
        # [디버깅] 엑셀에서 읽어온 실제 제목들을 화면에 보여줍니다.
        # (에러가 나면 이 부분을 확인하세요!)
        # -----------------------------------------------
        # st.caption(f"엑셀에서 인식된 제목들: {list(df.columns)}") 

        # 유통기한 날짜 변환
        if KEY_COLS['exp_date'] in df.columns:
            df[KEY_COLS['exp_date']] = pd.to_datetime(df[KEY_COLS['exp_date']], errors='coerce')
        else:
            # 유통기한 컬럼을 못 찾았을 때
            st.error(f"❌ '{KEY_COLS['exp_date']}' 컬럼을 찾을 수 없습니다!")
            st.write("현재 엑셀 파일의 제목 리스트:", list(df.columns))
            return pd.DataFrame() # 빈 데이터 반환
            
        return df
    except FileNotFoundError:
        st.error(f"❌ '{FILE_NAME}' 파일이 없습니다. 깃허브에 올리셨나요?")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
        return pd.DataFrame()

# 메인 화면
st.title("🧪 연구실 시약 종합 관리 DB")
today = datetime.now()
st.write(f"📅 **기준일:** {today.strftime('%Y-%m-%d')}")

df = load_data()

if not df.empty:
    # ----------------------------------------------------
    # 유통기한 임박 알림
    # ----------------------------------------------------
    if KEY_COLS['exp_date'] in df.columns:
        df['남은일수'] = (df[KEY_COLS['exp_date']] - today).dt.days + 1
        
        alert_days = [10, 7, 5, 3, 1]
        
        # 10일 이하 데이터 추출
        urgent_df = df[df['남은일수'] <= 10].sort_values(by='남은일수')
        
        st.divider()
        st.subheader("🚨 긴급 점검 (유통기한 임박)")
        
        if urgent_df.empty:
            st.success("✅ 현재 위험한 시약이 없습니다.")
        else:
            for i, row in urgent_df.iterrows():
                d_day = row['남은일수']
                
                # 안전하게 데이터 가져오기 (컬럼이 없으면 '-' 표시)
                # .get()을 쓰지 않고 직접 접근하되 try-except 처리
                try:
                    name = row[KEY_COLS['name']] if KEY_COLS['name'] in df.columns else "이름확인불가"
                    sub_name = row[KEY_COLS['sub_name']] if KEY_COLS['sub_name'] in df.columns else ""
                    danger = row[KEY_COLS['danger']] if KEY_COLS['danger'] in df.columns else ""
                    
                    msg_title = f"**{name}** ({sub_name})"
                    msg_desc = f"위험성: {danger}" if danger else ""
                    
                    if d_day < 0:
                        st.error(f"❌ [폐기필요] {msg_title} | {abs(d_day)}일 지남! | {msg_desc}")
                    elif d_day in alert_days:
                        st.warning(f"⚠️ [확인요망] {msg_title} | 딱 {d_day}일 남음 | {msg_desc}")
                    elif 0 <= d_day <= 10:
                        st.info(f"ℹ️ [관심] {msg_title} | {d_day}일 남음")
                except KeyError as e:
                    st.error(f"데이터 읽기 오류: {e}")

    # ----------------------------------------------------
    # 전체 리스트
    # ----------------------------------------------------
    st.divider()
    st.subheader("📋 전체 시약 상세 리스트")
    
    search_term = st.text_input("🔍 통합 검색", "")
    display_df = df.copy()
    
    # 날짜 포맷
    if KEY_COLS['exp_date'] in display_df.columns:
        display_df[KEY_COLS['exp_date']] = display_df[KEY_COLS['exp_date']].dt.strftime('%Y-%m-%d')
    if '등록일' in display_df.columns:
        display_df['등록일'] = pd.to_datetime(display_df['등록일'], errors='coerce').dt.strftime('%Y-%m-%d')

    # 검색
    if search_term:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
        
    st.dataframe(display_df, use_container_width=True, hide_index=True)
