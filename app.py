import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="연구실 시약 유통기한 관리", page_icon="🧪")

st.title("🧪 연구실 시약 유통기한 알리미")
st.subheader("오늘 날짜: " + datetime.now().strftime('%Y-%m-%d'))

# 2. 데이터 불러오기 함수
def load_data():
    try:
        # 엑셀 파일 읽기 (파일명이 다르면 수정하세요)
        df = pd.read_excel("reagents.xlsx")
        # 날짜 형식 변환 (에러 방지)
        df['유통기한'] = pd.to_datetime(df['유통기한'])
        return df
    except FileNotFoundError:
        st.error("❌ 'reagents.xlsx' 파일이 없습니다. 같은 폴더에 엑셀 파일을 넣어주세요.")
        return pd.DataFrame()

df = load_data()

# 3. 유통기한 계산 및 알림 로직
if not df.empty:
    today = datetime.now()
    
    # 남은 기간(D-Day) 계산
    # (유통기한 - 오늘)의 일수(days)만 추출
    df['남은일수'] = (df['유통기한'] - today).dt.days + 1 
    # +1을 하는 이유: 오늘 마감이면 0일이 아니라 '오늘까지'라고 표현하거나 D-Day 계산을 맞추기 위함

    # 알림을 띄울 조건 (10, 7, 5, 3, 1일 전)
    alert_days = [10, 7, 5, 3, 1]
    
    st.divider()
    st.markdown("### 🚨 긴급 점검 필요 (알림)")

    alert_count = 0
    
    for index, row in df.iterrows():
        d_day = row['남은일수']
        name = row['시약이름']
        loc = row['시약종류']
        
        # 1. 유통기한이 지났을 때
        if d_day < 0:
            st.error(f"❌ [폐기필요] '{name}' ({loc}) - 유통기한이 {abs(d_day)}일 지났습니다!")
            alert_count += 1
            
        # 2. 지정된 알림 날짜에 해당할 때 (1, 3, 5, 7, 10일 전)
        elif d_day in alert_days:
            st.warning(f"⚠️ [임박] '{name}' ({loc}) - 유통기한까지 딱 {d_day}일 남았습니다!")
            alert_count += 1
            
        # 3. 10일 이내로 남았지만 위 날짜가 아닐 때 (참고용)
        elif 0 <= d_day < 10:
            st.info(f"ℹ️ [관심] '{name}' ({loc}) - {d_day}일 남음")

    if alert_count == 0:
        st.success("현재 긴급하게 처리해야 할 시약이 없습니다.")

    st.divider()

    # 4. 전체 데이터 조회 (옵션)
    with st.expander("📋 전체 시약 목록 보기"):
        # 보기 좋게 날짜 포맷 변경해서 보여주기
        display_df = df.copy()
        display_df['유통기한'] = display_df['유통기한'].dt.strftime('%Y-%m-%d')
        # 남은일수 기준으로 정렬 (급한게 위로)
        display_df = display_df.sort_values(by='남은일수')
        st.dataframe(display_df)
