import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# [설정] 엑셀 파일 정보 (여기만 수정하면 됩니다!)
# ==========================================
FILE_NAME = 'database.xlsx'  # 파일 이름

# 엑셀의 맨 윗줄(제목)이 아래와 다르면, 따옴표 안의 글자를 엑셀과 똑같이 바꿔주세요.
COL_INFO = {
    'name': '시약이름',      # 예: 엑셀에 '제품명'이라고 적혀있으면 '제품명'으로 수정
    'type': '시약종류',      # 예: '분류'라고 적혀있으면 '분류'로 수정
    'exp_date': '유통기한',  # 유통기한 날짜가 있는 열
    'open_date': '개봉일'    # 개봉일 날짜가 있는 열 (없으면 비워도 됨)
}
# ==========================================

st.set_page_config(page_title="시약 관리 DB", page_icon="🧪", layout="centered")

def load_data():
    try:
        df = pd.read_excel(FILE_NAME)
        
        # 날짜 형식 변환 (에러 방지용 안전 장치)
        # 엑셀의 날짜가 문자로 되어있어도 날짜로 인식하게 만듦
        df[COL_INFO['exp_date']] = pd.to_datetime(df[COL_INFO['exp_date']], errors='coerce')
        if COL_INFO['open_date'] in df.columns:
            df[COL_INFO['open_date']] = pd.to_datetime(df[COL_INFO['open_date']], errors='coerce')
            
        return df
    except FileNotFoundError:
        st.error(f"❌ '{FILE_NAME}' 파일이 없습니다. 깃허브에 파일을 올렸는지 확인해주세요.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 메인 화면 시작
st.title("🧪 연구실 시약 DB 관리")
st.caption(f"연동된 파일: {FILE_NAME}")

today = datetime.now()
st.metric("오늘 날짜", today.strftime('%Y-%m-%d'))

df = load_data()

if not df.empty:
    # 남은 기간 계산
    # (유통기한 - 오늘)
    df['d_day'] = (df[COL_INFO['exp_date']] - today).dt.days + 1
    
    # ----------------------------------------------------
    # 1. 긴급 알림 섹션 (10일, 7일, 5일, 3일, 1일, 지남)
    # ----------------------------------------------------
    st.divider()
    st.subheader("🚨 긴급 점검 리스트")
    
    alert_days = [10, 7, 5, 3, 1]
    alert_count = 0
    
    # 유통기한 임박하거나 지난 것만 필터링해서 보여주기 (속도 최적화)
    # d_day가 10보다 작거나 같은 데이터만 뽑음
    urgent_df = df[df['d_day'] <= 10].sort_values(by='d_day')

    for index, row in urgent_df.iterrows():
        d_day = row['d_day']
        name = row[COL_INFO['name']]
        # 시약 종류가 데이터에 없으면 빈칸 처리
        type_ = row[COL_INFO['type']] if COL_INFO['type'] in df.columns else ""
        
        # 1. 유통기한 지남 (폐기)
        if d_day < 0:
            st.error(f"❌ [폐기] **{name}** ({type_}) | {abs(d_day)}일 지남")
            alert_count += 1
            
        # 2. 지정된 알림 날짜 (임박)
        elif d_day in alert_days:
            st.warning(f"⚠️ [임박] **{name}** ({type_}) | 딱 **{d_day}일** 남음!")
            alert_count += 1
            
        # 3. 그 외 10일 이내 (주의)
        elif 0 <= d_day <= 10:
            st.info(f"ℹ️ [관심] **{name}** ({type_}) | {d_day}일 남음")
            alert_count += 1

    if alert_count == 0:
        st.success("현재 유통기한이 임박한 시약이 없습니다. 안전합니다! 👍")

    # ----------------------------------------------------
    # 2. 전체 데이터 검색 섹션
    # ----------------------------------------------------
    st.divider()
    with st.expander("🔍 전체 시약 DB 검색하기"):
        search_term = st.text_input("찾고 싶은 시약 이름을 입력하세요")
        
        display_df = df.copy()
        
        # 날짜 보기 좋게 변경 (년-월-일)
        display_df[COL_INFO['exp_date']] = display_df[COL_INFO['exp_date']].dt.strftime('%Y-%m-%d')
        
        # 검색 기능
        if search_term:
            display_df = display_df[display_df[COL_INFO['name']].str.contains(search_term, case=False, na=False)]
            
        st.dataframe(display_df)
