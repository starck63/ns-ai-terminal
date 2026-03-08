import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("NS AI TERMINAL")

# -----------------------------
# WATCHLIST
# -----------------------------

korea_watchlist = {
"삼성전자":"005930","SK하이닉스":"000660","LG에너지솔루션":"373220","NAVER":"035420",
"카카오":"035720","현대차":"005380","기아":"000270","POSCO홀딩스":"005490",
"삼성SDI":"006400","셀트리온":"068270","두산에너빌리티":"034020","한화에어로스페이스":"012450",
"LIG넥스원":"079550","현대로템":"064350","삼성바이오로직스":"207940","LG전자":"066570",
"LG이노텍":"011070","대한항공":"003490","포스코퓨처엠":"003670","HD현대중공업":"329180",
"한국전력":"015760","KT":"030200","CJ제일제당":"097950","삼성물산":"028260",
"롯데케미칼":"011170","GS":"078930","S-Oil":"010950","DB하이텍":"000990",
"한화솔루션":"009830","LG생활건강":"051900","에코프로":"086520","에코프로비엠":"247540",
"엘앤에프":"066970","펄어비스":"263750","크래프톤":"259960","위메이드":"112040",
"카카오게임즈":"293490","넷마블":"251270","한미반도체":"042700","ISC":"095340"
}

usa_watchlist = {
"NVDA":"NVDA","AMD":"AMD","AAPL":"AAPL","MSFT":"MSFT","AMZN":"AMZN",
"GOOGL":"GOOGL","META":"META","TSLA":"TSLA","AVGO":"AVGO","NFLX":"NFLX",
"SMCI":"SMCI","INTC":"INTC","ARM":"ARM","PLTR":"PLTR","TSM":"TSM"
}

etf_watchlist = {
"QQQ":"QQQ","SPY":"SPY","SOXX":"SOXX","SMH":"SMH","XLK":"XLK","TIGER200":"102110","KODEX200":"069500"
}

# -----------------------------
# DATA LOADER
# -----------------------------

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

# -----------------------------
# TREND
# -----------------------------

def calc_trend(df):

    close=df["Close"].squeeze()

    ma20=close.rolling(20).mean().iloc[-1]
    ma60=close.rolling(60).mean().iloc[-1]

    if pd.isna(ma20) or pd.isna(ma60):
        return "중립"

    return "상승" if ma20>ma60 else "중립"

# -----------------------------
# CHART
# -----------------------------

def show_chart(df):

    df=df.tail(126)

    close=df["Close"].squeeze()

    df["MA20"]=close.rolling(20).mean()
    df["MA60"]=close.rolling(60).mean()

    df["signal"]=0
    df.loc[df["MA20"]>df["MA60"],"signal"]=1
    df["cross"]=df["signal"].diff()

    buy=df[df["cross"]==1]
    sell=df[df["cross"]==-1]

    fig,ax=plt.subplots()

    ax.plot(close,label="Price")
    ax.plot(df["MA20"],label="MA20")
    ax.plot(df["MA60"],label="MA60")

    ax.scatter(buy.index,buy["Close"],marker="^",color="green",s=120,label="BUY")
    ax.scatter(sell.index,sell["Close"],marker="v",color="red",s=120,label="SELL")

    ax.legend()

    st.pyplot(fig)

# -----------------------------
# AI ANALYSIS
# -----------------------------

def ai_analysis(df):

    df=df.tail(126)

    close=df["Close"].squeeze()

    last=close.iloc[-1]

    change=((last-close.iloc[0])/close.iloc[0])*100

    ma20=close.rolling(20).mean().iloc[-1]
    ma60=close.rolling(60).mean().iloc[-1]

    trend="상승 추세" if ma20>ma60 else "조정 구간"

    return f"""
현재 가격 : {round(last,2)}

6개월 수익률 : {round(change,2)} %

기술적 추세 : {trend}

MA20 / MA60 기준 분석입니다.
"""

# -----------------------------
# SEARCH (ONE INPUT)
# -----------------------------

query=st.text_input("종목 검색 (한국 이름 또는 미국 티커)")

if query:

    ticker=None
    name=None

    krx=fdr.StockListing("KRX")

    res=krx[krx["Name"].str.contains(query)]

    if len(res)>0:

        ticker=res.iloc[0]["Code"]
        name=res.iloc[0]["Name"]

    else:

        ticker=query.upper()
        name=ticker

    df=load_data(ticker)

    if df is None:

        st.error("종목 데이터 없음")

    else:

        st.subheader(name)

        show_chart(df)

        st.subheader("AI 분석")

        st.write(ai_analysis(df))

# -----------------------------
# PANEL
# -----------------------------

def draw_panel(title,watchlist):

    st.subheader(title)

    cols=st.columns(5)

    i=0

    for name,ticker in watchlist.items():

        df=load_data(ticker)

        trend=calc_trend(df) if df is not None else "중립"

        icon="🔥" if trend=="상승" else "❄"

        label=f"{name} {icon}"

        if cols[i].button(label):

            if df is not None:

                st.subheader(name)

                show_chart(df)

                st.subheader("AI 분석")

                st.write(ai_analysis(df))

        i+=1

        if i==5:

            cols=st.columns(5)

            i=0

# -----------------------------
# PANELS
# -----------------------------

draw_panel("한국 종목",korea_watchlist)
draw_panel("미국 종목",usa_watchlist)
draw_panel("ETF",etf_watchlist)