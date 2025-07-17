import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="FinAdvisor AI")

# ======== ESTILO CSS ========
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
.card { background-color: #1c1f26; border-radius: 12px; padding: 15px; text-align: center; transition: 0.3s; cursor: pointer; }
.card:hover { background-color: #2a2e38; }
.price { font-size: 1.3em; color: white; font-weight: bold; }
.change-pos { color: lime; }
.change-neg { color: red; }
.card-title { font-weight: bold; font-size: 1.1em; color: #c084fc; }
.section-title { font-size: 1.6em; margin-top: 30px; color: #c084fc; }
.metric-box { border-radius: 12px; background-color: #1c1f26; padding: 20px; margin: 10px 0; }
.metric-box h3 { font-size: 1.3em; color: #f0f0f0; }
.metric-box p { font-size: 1.05em; color: #a0aec0; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#ffffff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#cccccc;'>Descubrí oportunidades de inversión con datos en tiempo real y análisis técnico/fundamental.</p>", unsafe_allow_html=True)

# ========== LISTA DE TICKERS ==========
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]

# ========= CARGA DE DATOS =========
last_prices = {}
prev_closes = {}

for ticker in tickers:
    try:
        hist = yf.Ticker(ticker).history(period="2d", interval="1m")
        if len(hist) > 0:
            last_prices[ticker] = hist["Close"].iloc[-1]
            prev_closes[ticker] = hist["Close"].iloc[0]
        else:
            last_prices[ticker] = None
            prev_closes[ticker] = None
    except:
        last_prices[ticker] = None
        prev_closes[ticker] = None

# ========== RENDER DE TENDENCIAS ==========
st.markdown("<div class='section-title'>📊 Tendencias USA</div>", unsafe_allow_html=True)
cols = st.columns(5)
selected_ticker = None

for i, ticker in enumerate(tickers[:5]):
    last_price = last_prices.get(ticker)
    prev_close = prev_closes.get(ticker)
    if last_price and prev_close:
        change = ((last_price - prev_close) / prev_close) * 100
        last_price_str = f"${last_price:.2f}"
    else:
        change = 0
        last_price_str = "N/A"
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols[i]:
        if st.button(ticker, key=f"top_{ticker}"):
            selected_ticker = ticker
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{ticker}</div>
            <div class="price">{last_price_str}</div>
            <div class="{color_class}">{change:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

# ========== MÁS NEGOCIADAS ==========
st.markdown("<div class='section-title'>🔥 Más negociadas</div>", unsafe_allow_html=True)
cols2 = st.columns(5)

for i, ticker in enumerate(tickers[5:]):
    last_price = last_prices.get(ticker)
    prev_close = prev_closes.get(ticker)
    if last_price and prev_close:
        change = ((last_price - prev_close) / prev_close) * 100
        last_price_str = f"${last_price:.2f}"
    else:
        change = 0
        last_price_str = "N/A"
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols2[i]:
        if st.button(ticker, key=f"bottom_{ticker}"):
            selected_ticker = ticker
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{ticker}</div>
            <div class="price">{last_price_str}</div>
            <div class="{color_class}">{change:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

# ========== ANÁLISIS DETALLADO ==========
if selected_ticker:
    stock = yf.Ticker(selected_ticker)
    hist = stock.history(period="max")
    price_now = hist["Close"].iloc[-1]
    ath = hist["Close"].max()
    upside = ((ath - price_now) / price_now) * 100

    df = stock.history(period="6mo")
    rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    ma200 = df["Close"].rolling(200).mean().iloc[-1]
    bb = ta.volatility.BollingerBands(df["Close"])
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    info = stock.info
    pe = info.get("trailingPE", None)
    eps = info.get("trailingEps", None)
    mkt_cap = info.get("marketCap", None)

    st.markdown(f"<h2 style='color:#ffffff;'>📌 Análisis de {selected_ticker}</h2>", unsafe_allow_html=True)

    # RSI
    st.markdown(f"<div class='metric-box'><h3>📉 RSI: {rsi:.2f}</h3>", unsafe_allow_html=True)
    if rsi < 30:
        st.markdown("<p>📉 Sobrevendido. Probabilidad de rebote: <span style='color:lime;'>ALTA ✅</span></p>", unsafe_allow_html=True)
    elif rsi > 70:
        st.markdown("<p>📈 Sobrecomprado. Riesgo de caída: <span style='color:red;'>ELEVADO ⚠️</span></p>", unsafe_allow_html=True)
    else:
        st.markdown("<p>📊 RSI neutral. Esperar confirmación.</p></div>", unsafe_allow_html=True)

    # MA y otros análisis igual que antes...

    # Gráfico interactivo
    st.markdown("### 📈 Gráfico interactivo")
    tv_widget = f"""
    <iframe src="https://s.tradingview.com/widgetembed/?symbol=NASDAQ:{selected_ticker}&interval=1D&theme=dark&style=1&timezone=America%2FBuenos_Aires"
    width="100%" height="500" frameborder="0" scrolling="no"></iframe>
    """
    components.html(tv_widget, height=500)
