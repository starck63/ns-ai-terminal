import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("📈 NS AI 투자 터미널")

# ---------------------------------
# 한글 → 티커 변환
# ---------------------------------

ticker_map = {
    "코카콜라":"KO",
    "애플":"AAPL",
    "엔비디아":"NVDA",
    "테슬라":"TSLA",
    "아마존":"AMZN",
    "마이크로소프트":"MSFT",
    "삼성전자":"005930",
    "SK하이닉스":"000660"
}

# ---------------------------------
# 관심 종목
# ---------------------------------

watchlist = {
    "삼성전자":"005930",
    "SK하이닉스":"000660",
    "엔비디아":"NVDA",
    "애플":"AAPL",
    "테슬라":"TSLA",
    "아마존":"AMZN"
}

# ---------------------------------
# 차트 기간 선택
# ---------------------------------

period = st.selectbox(
    "차트 기간",
    ["3mo","6mo","1y","5y"]
)

# ---------------------------------
# 데이터 로딩
# ---------------------------------

@st.cache_data
def load_data(ticker):

    try:

        if ticker.isdigit():
            df = fdr.DataReader(ticker)

        else:
            df = yf.download(ticker,period=period)

        return df

    except:
        return None

# ---------------------------------
# 추세 계산
# ---------------------------------

def calc_trend(df):

    if df is None or len(df) < 60:
        return "중립"

    close = df["Close"]

    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1]

    return "상승" if ma20 > ma60 else "중립"

# ---------------------------------
# HeatMap
# ---------------------------------

st.subheader("📊 시장 HeatMap")

cols = st.columns(3)

i = 0

for name,ticker in watchlist.items():

    df = load_data(ticker)

    if df is None:
        continue

    trend = calc_trend(df)

    color = "🟩" if trend=="상승" else "🟥"

    cols[i].metric(label=name,value=color)

    i+=1

    if i==3:
        cols = st.columns(3)
        i=0

# ---------------------------------
# AI 추천
# ---------------------------------

st.subheader("🔥 AI 추천 종목")

recommend=[]

for name,ticker in watchlist.items():

    df = load_data(ticker)

    if df is None:
        continue

    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma60 = df["Close"].rolling(60).mean().iloc[-1]

    score = ma20-ma60

    recommend.append((name,score,ticker))

recommend.sort(key=lambda x:x[1],reverse=True)

for r in recommend[:5]:

    if st.button("⭐ "+r[0]):

        ticker=r[2]

        df=load_data(ticker)

        st.subheader(f"{r[0]} 분석")

        show_chart(df)

# ---------------------------------
# 차트 함수
# ---------------------------------

def show_chart(df):

    df["MA20"]=df["Close"].rolling(20).mean()
    df["MA60"]=df["Close"].rolling(60).mean()

    df["signal"]=0
    df.loc[df["MA20"]>df["MA60"],"signal"]=1
    df["cross"]=df["signal"].diff()

    buy=df[df["cross"]==1]
    sell=df[df["cross"]==-1]

    fig,ax=plt.subplots()

    ax.plot(df["Close"],label="Price")
    ax.plot(df["MA20"],label="MA20")
    ax.plot(df["MA60"],label="MA60")

    ax.scatter(buy.index,buy["Close"],marker="^",color="green",s=100,label="BUY")
    ax.scatter(sell.index,sell["Close"],marker="v",color="red",s=100,label="SELL")

    ax.legend()

    st.pyplot(fig)

# ---------------------------------
# 검색
# ---------------------------------

st.subheader("🔍 종목 검색")

query=st.text_input("종목 입력")

if query:

    ticker=ticker_map.get(query,query).upper()

    df=load_data(ticker)

    if df is None or len(df)==0:

        st.error("데이터 없음")

    else:

        st.subheader(f"{query} 차트")

        show_chart(df)

        trend=calc_trend(df)

        st.write("추세:",trend)

# ---------------------------------
# 패널 클릭
# ---------------------------------

st.subheader("📋 관심 종목 패널")

for name,ticker in watchlist.items():

    if st.button(name):

        df=load_data(ticker)

        if df is None:

            st.error("데이터 없음")

        else:

            st.subheader(f"{name} 분석")

            show_chart(df)
