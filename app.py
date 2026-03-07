import streamlit as st
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# --- [환경 설정 및 폰트] ---
st.set_page_config(page_title="NS AI TERMINAL", layout="wide")

@st.cache_resource
def load_font():
    # 리눅스 서버(Streamlit Cloud) 한글 폰트 강제 설정
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False

load_font()

st.title("🏢 NS 글로벌 통합 관제탑 (WEB)")

# --- [1. 지능형 엔진: 국내/미국 자동 판별] ---
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    try:
        # 국내 주식 여부 판별 (숫자 6자리)
        if ticker.isdigit():
            df = fdr.DataReader(ticker).tail(250)
        else:
            # 미국 주식 및 지수
            df = yf.download(ticker, period="1y", progress=False)
            # 최근 yfinance 멀티인덱스 이슈 대응
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# --- [2. 종목 리스트 (대표님 핵심 관심주)] ---
stocks = {
    "타이거200": "102110",
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "테슬라": "TSLA",
    "엔비디아": "NVDA",
    "애플": "AAPL",
    "아마존": "AMZN"
}

# --- [3. 메인 화면 구성] ---
ticker_input = st.text_input("🔍 종목명 또는 코드 입력 (예: 102110, TSLA)", "")

col1, col2 = st.columns([1, 2.5])

# 왼쪽 패널: 주요 종목 상태 (캐시 적용으로 속도 향상)
with col1:
    st.subheader("📋 관심 종목 현황")
    for name, code in stocks.items():
        df_mini = get_stock_data(code)
        if not df_mini.empty:
            m20 = df_mini["Close"].rolling(20).mean().iloc[-1]
            m60 = df_mini["Close"].rolling(60).mean().iloc[-1]
            trend = "🔥 상승" if m20 > m60 else "❄️ 중립"
            color = "red" if trend == "🔥 상승" else "blue"
            st.markdown(f"**{name}**: :{color}[{trend}]")

# 오른쪽 패널: 상세 차트 분석
with col2:
    target = ticker_input.strip() if ticker_input else "102110" # 기본값 타이거200
    st.subheader(f"📈 {target} 정밀 분석 차트")
    
    df = get_stock_data(target)
    
    if not df.empty:
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA60"] = df["Close"].rolling(60).mean()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index[-120:], df["Close"].tail(120), label="현재가", color='dodgerblue', linewidth=2)
        ax.plot(df.index[-120:], df["MA20"].tail(120), label="20일선", color='orange', linestyle='--')
        ax.plot(df.index[-120:], df["MA60"].tail(120), label="60일선(기준)", color='red', linewidth=2.5)
        
        # 골든크로스 구간 강조
        ax.fill_between(df.index[-120:], df["MA20"].tail(120), df["MA60"].tail(120), 
                         where=(df["MA20"].tail(120) >= df["MA60"].tail(120)), color='red', alpha=0.1)
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        
        # AI 상태 보고
        curr_m20 = df["MA20"].iloc[-1]
        curr_m60 = df["MA60"].iloc[-1]
        if curr_m20 > curr_m60:
            st.success(f"✅ 현재 **상승 추세**입니다. (20일선이 60일선 위에 위치)")
        else:
            st.warning(f"⚠️ 현재 **관망 구간**입니다. (60일선 지지 확인 필요)")
    else:
        st.error("데이터를 불러올 수 없습니다. 코드를 확인해주세요.")
