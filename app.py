import streamlit as st
import pandas as pd
from datetime import datetime, timedelta # timedelta 추가됨

# ==========================================
# [설정] 핵심 컬럼 이름
# ==========================================
FILE_NAME = 'database.xlsx'

KEY_COLS = {
    'name': '제품명',
    'sub_name': '제품명(한글)',
    'exp_date': '유통기한',
    'danger': '유해 및 위험성'
}
# ==========================================

st.set_page_config(page_title="시약 관리 시스템", page_icon="🧪", layout="wide")

def load_data():
    try:
        df = pd.read_excel(FILE_NAME)
        df.columns = df.columns.str.strip() # 공백 제거
        df.columns = df.columns.str.replace('\n', '').str.replace('\r', '') # 줄바꿈 제거

        if KEY_COLS['exp_date'] in df.columns:
            df[KEY_COLS['exp_date']] = pd.to_datetime(df[KEY_COLS['exp_date']], errors='coerce')
        return df
    except Exception as e:
        st.error(f"데이터 오류: {e}")
        return pd.DataFrame()

# 메인 화면
st.title("🧪 연구실 시약 종합 관리 DB")

# [중요] 한국 시간 설정 (UTC + 9시간)
today = datetime.now() + timedelta(hours=9)
st.write(f"📅 **기준일(한국):** {today.strftime('%Y-%m-%d')}")

df = load_data()

if not df.empty:
    if KEY_COLS['exp_date'] in df.columns:
        # 남은 일수 계산
        df['남은일수'] = (df[KEY_COLS['exp_date']] - today).dt.days + 1
        
        alert_days = [10, 7, 5, 3, 1]
        urgent_df = df[df['남은일수'] <= 10].sort_values(by='남은일수')
        
        st.divider()
        st.subheader("🚨 긴급 점검 (유통기한 임박)")
        
        if urgent_df.empty:
            st.success("✅ 현재 위험한 시약이 없습니다.")
        else:
            for i, row in urgent_df.iterrows():
                d_day = row['남은일수']
                try:
                    name = row[KEY_COLS['name']] if KEY_COLS['name'] in df.columns else "-"
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
                except:
                    pass

    # 전체 리스트
    st.divider()
    st.subheader("📋 전체 시약 상세 리스트")
    search_term = st.text_input("🔍 통합 검색", "")
    
    display_df = df.copy()
    if KEY_COLS['exp_date'] in display_df.columns:
        display_df[KEY_COLS['exp_date']] = display_df[KEY_COLS['exp_date']].dt.strftime('%Y-%m-%d')
    if '등록일' in display_df.columns:
         # 등록일이 있으면 날짜 변환 (없으면 통과)
         display_df['등록일'] = pd.to_datetime(display_df['등록일'], errors='coerce').dt.strftime('%Y-%m-%d')

    if search_term:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
        
    st.dataframe(display_df, use_container_width=True, hide_index=True)
