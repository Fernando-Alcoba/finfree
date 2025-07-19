import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components
import feedparser

st.set_page_config(layout="wide", page_title="FinAdvisor AI")

# =======================
# CSS personalizado
# =======================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.card {
    background-color: #1c1f26;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    transition: 0.3s;
    cursor: pointer;
}
.card:hover {
    background-color: #2a2e38;
}
.price {
    font-size: 1.3em;
    color: white;
    font-weight: bold;
}
.change-pos {
    color: lime;
}
.change-neg {
    color: red;
}
.card-title {
    font-weight: bold;
    font-size: 1.1em;
    color: #c084fc;
}
.section-title {
    font-size: 1.6em;
    margin-top: 30px;
    color: #c084fc;
}
.metric-box {
    border-radius: 12px;
    background-color: #1c1f26;
    padding: 20px;
    margin: 10px 0;
}
.metric-box h3 {
    font-size: 1.3em;
    color: #f0f0f0;
}
.metric-box p {
    font-size: 1.05em;
    color: #a0aec0;
}
</style>
""", unsafe_allow_html=True)

# =======================
# Título
# =======================
st.markdown("<h1 style='color:#ffffff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#cccccc;'>Descubrí oportunidades de inversión con datos en tiempo real, análisis técnico, fundamental y noticias.</p>", unsafe_allow_html=True)

# =======================
# Tickers populares
# =======================
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]

# Descargar datos
try:
    data = yf.download(tickers, period="1d", interval="1m", group_by='ticker', threads=True)
    prev_close_data = yf.download(tickers, period="2d", interval="1d")
except:
    st.error("Error al descargar datos de Yahoo Finance")
    data, prev_close_data = None, None

last_prices, prev_close = {}, {}

for ticker in tickers:
    try:
        last_prices[ticker] = data[ticker]['Adj Close'].iloc[-1] if ticker in data else None
    except:
        last_prices[ticker] = None
    try:
        prev_close[ticker] = prev_close_data[ticker]['Adj Close'].iloc[-2] if ticker in prev_close_data else None
    except:
        prev_close[ticker] = None

# =======================
# Mostrar tarjetas
# =======================
st.markdown("<div class='section-title'>📊 Tendencias USA</div>", unsafe_allow_html=True)
cols = st.columns(5)
for i, ticker in enumerate(tickers[:5]):
    price = last_prices[ticker]
    prev = prev_close[ticker]
    change = ((price - prev) / prev) * 100 if price and prev else 0
    price_str = f"${price:.2f}" if price else "N/A"
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols[i]:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{ticker}</div>
            <div class="price">{price_str}</div>
            <div class="{color_class}">{change:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-title'>🔥 Más negociadas</div>", unsafe_allow_html=True)
cols2 = st.columns(5)
for i, ticker in enumerate(tickers[5:]):
    price = last_prices[ticker]
    prev = prev_close[ticker]
    change = ((price - prev) / prev) * 100 if price and prev else 0
    price_str = f"${price:.2f}" if price else "N/A"
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols2[i]:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{ticker}</div>
            <div class="price">{price_str}</div>
            <div class="{color_class}">{change:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

# =======================
# Selección de ticker
# =======================
selected_ticker = st.selectbox("Elegí un ticker para analizar:", tickers)

# =======================
# Análisis técnico
# =======================
stock = yf.Ticker(selected_ticker)
df = stock.history(period="6mo")
price_now = df["Close"].iloc[-1]
rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
ma50 = df["Close"].rolling(50).mean().iloc[-1]
ma200 = df["Close"].rolling(200).mean().iloc[-1]

# =======================
# Gráfico interactivo TradingView
# =======================
st.markdown("### 📈 Gráfico interactivo")
tv_widget = f"""
<iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=1D&theme=dark&style=1&timezone=America%2FBuenos_Aires"
width="100%" height="500" frameborder="0" scrolling="no"></iframe>
"""
components.html(tv_widget, height=500)
