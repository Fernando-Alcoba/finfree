import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components
import feedparser

st.set_page_config(layout="wide", page_title="FinAdvisor AI")

# =======================
# CSS
# =======================
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
.card {
    background-color: #1c1f26;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
}
.price { font-size: 1.3em; font-weight: bold; }
.change-pos { color: lime; }
.change-neg { color: red; }
.card-title { font-weight: bold; font-size: 1.1em; color: #c084fc; }
.section-title { font-size: 1.6em; margin-top: 30px; color: #c084fc; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#fff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)

# =======================
# Inicializar estado
# =======================
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "AAPL"

# =======================
# Tickers populares
# =======================
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]

# =======================
# Obtener datos de precios
# =======================
last_prices = {}
changes = {}

for ticker in tickers:
    stock = yf.Ticker(ticker)
    try:
        price = stock.fast_info.last_price
        prev_close = stock.fast_info.previous_close
        change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
        last_prices[ticker] = price
        changes[ticker] = change
    except:
        last_prices[ticker] = None
        changes[ticker] = 0

# =======================
# Mostrar tarjetas
# =======================
st.markdown("<div class='section-title'>📊 Tendencias USA</div>", unsafe_allow_html=True)
cols = st.columns(5)
for i, ticker in enumerate(tickers[:5]):
    price = last_prices[ticker]
    change = changes[ticker]
    price_str = f"${price:.2f}" if price else "N/A"
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols[i]:
        if st.button(ticker, key=f"btn_{ticker}"):
            st.session_state.selected_ticker = ticker
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
    change = changes[ticker]
    price_str = f"${price:.2f}" if price else "N/A"
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols2[i]:
        if st.button(ticker, key=f"btn_{ticker}_2"):
            st.session_state.selected_ticker = ticker
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{ticker}</div>
            <div class="price">{price_str}</div>
            <div class="{color_class}">{change:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

# =======================
# Análisis del ticker seleccionado
# =======================
selected_ticker = st.session_state.selected_ticker
st.markdown(f"### ✅ Analizando: {selected_ticker}")

stock = yf.Ticker(selected_ticker)
df = stock.history(period="6mo")
if df.empty:
    st.warning("No hay datos históricos para análisis.")
else:
    price_now = df["Close"].iloc[-1]
    rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    ma200 = df["Close"].rolling(200).mean().iloc[-1]

    st.write(f"📌 Precio actual: ${price_now:.2f}")
    st.write(f"📊 RSI: {rsi:.2f}")
    st.write(f"📈 MA50: {ma50:.2f} | MA200: {ma200:.2f}")

# =======================
# Gráfico TradingView
# =======================
st.markdown("### 📈 Gráfico interactivo")
tv_widget = f"""
<iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=1D&theme=dark&style=1"
width="100%" height="500" frameborder="0" scrolling="no"></iframe>
"""
components.html(tv_widget, height=500)
