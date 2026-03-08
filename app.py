import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="NS AI TERMINAL", layout="wide")

st.title("📈 NS AI TERMINAL")

# -------------------------
# 한글 → 티커 매핑
# -------------------------

ticker_map = {
    "코카콜라":"KO",
    "애플":"AAPL",
    "엔비디아":"NVDA",
    "테슬라":"TSLA",
    "아마존":"AMZN",
    "마이크로소프트":"MSFT",
    "삼성전자":"005930",
    "SK하이닉스":"000660",
    "타이거200":"102110"
}

# -------------------------
# 관심 종목
# -------------------------

watchlist = {
    "타이거200":"102110",
    "삼성전자":"005930",
    "SK하이닉스":"000660",
    "테슬라":"TSLA",
    "엔비디아":"NVDA",
    "애플":"AAPL",
    "아마존":"AMZN"
}

# -------------------------
# 데이터 로딩 함수
# -------------------------

@st.cache_data
def load_data(ticker):

    try:

        if ticker.isdigit():
            df = fdr.DataReader(ticker)

        else:
            df = yf.download(ticker, period="1y")

        if df is None or len(df)==0:
            return None

        return df

    except:
        return None


# -------------------------
# 추세 계산
# -------------------------

def get_trend(df):

    close = df["Close"]

    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1]

    if ma20 > ma60:
        return "🔥 상승"
    else:
        return "❄ 중립"


# -------------------------
# 검색
# -------------------------

query = st.text_input("종목 검색")

if query:

    ticker = ticker_map.get(query, query).upper()

    df = load_data(ticker)

    if df is None:

        st.error("데이터를 불러올 수 없습니다. 코드 또는 종목을 확인해주세요.")

    else:

        st.subheader(f"📊 {query} 정밀 분석 차트")

        fig, ax = plt.subplots()

        ax.plot(df.index, df["Close"], label="Price")

        ma20 = df["Close"].rolling(20).mean()
        ma60 = df["Close"].rolling(60).mean()

        ax.plot(df.index, ma20, label="MA20")
        ax.plot(df.index, ma60, label="MA60")

        ax.legend()

        st.pyplot(fig)


# -------------------------
# 관심 종목 패널
# -------------------------

st.subheader("📋 관심 종목 현황")

for name,ticker in watchlist.items():

    df = load_data(ticker)

    if df is None:

        st.write(f"{name} : 데이터 없음")

    else:

        trend = get_trend(df)

        st.write(f"{name} : {trend}")
