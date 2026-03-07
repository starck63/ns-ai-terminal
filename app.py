import streamlit as st
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("NS AI TERMINAL")

# 종목 리스트
stocks = {
    "삼성전자":"005930",
    "SK하이닉스":"000660",
    "NAVER":"035420",
    "카카오":"035720",
    "NVDA":"NVDA",
    "AMD":"AMD",
    "AAPL":"AAPL",
    "MSFT":"MSFT",
    "TSLA":"TSLA"
}

# 데이터 캐시 (속도 개선)
@st.cache_data
def load_data(ticker):

    try:

        if ticker.isdigit():
            df = fdr.DataReader(ticker)

        else:
            df = yf.download(ticker,period="1y")

        return df

    except:
        return None


# 패널 + 검색 레이아웃
col1,col2 = st.columns([1,2])

# ---------------------------------
# 패널
# ---------------------------------

panel_data = []

for name,ticker in stocks.items():

    df = load_data(ticker)

    if df is None or len(df)==0:
        continue

    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma60 = df["Close"].rolling(60).mean().iloc[-1]

    trend = "상승" if ma20 > ma60 else "중립"

    panel_data.append({"종목":name,"추세":trend})

st.dataframe(panel_data)

# ---------------------------------
# 검색 + 차트
# ---------------------------------

with col2:

    st.subheader("종목 검색")

    ticker_input = st.text_input("종목 코드 입력 (예: NVDA)")

    if ticker_input:

        ticker = ticker_input.upper()

        df = load_data(ticker)

        if df is None or len(df)==0:

            st.write("데이터 없음")

        else:

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA60"] = df["Close"].rolling(60).mean()

            fig,ax = plt.subplots()

            ax.plot(df["Close"],label="Price")
            ax.plot(df["MA20"],label="MA20")
            ax.plot(df["MA60"],label="MA60")

            ax.legend()

            st.pyplot(fig)

            ma20 = df["MA20"].iloc[-1]
            ma60 = df["MA60"].iloc[-1]

            trend = "상승" if ma20 > ma60 else "중립"

            st.write(f"추세 : {trend}")
