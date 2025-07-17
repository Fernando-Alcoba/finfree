import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components

# Configuración inicial
st.set_page_config(layout="wide", page_title="Análisis de Acciones")

# Estilos CSS personalizados
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .title {
        font-size: 3em;
        font-weight: 700;
        color: #c084fc;
    }
    .metric-box {
        border-radius: 12px;
        background-color: #1c1f26;
        padding: 20px;
        text-align: center;
        margin: 10px 5px;
    }
    .metric-box h2 {
        font-size: 1.5em;
        color: #f0f0f0;
    }
    .metric-box p {
        font-size: 1.1em;
        color: #a0aec0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>📊 Análisis Integral de Acciones</div>", unsafe_allow_html=True)

# Sidebar: selección de ticker
ticker = st.sidebar.selectbox("Seleccioná una acción", ["AAPL", "MSFT", "TSLA", "NVDA", "GOOGL", "AMZN"])

# Obtener datos
stock = yf.Ticker(ticker)
hist = stock.history(period="max")
current_price = hist["Close"][-1]
ath = hist["Close"].max()
upside = ((ath - current_price) / current_price) * 100

# RSI & Medias
hist_technical = stock.history(period="6mo", interval="1d")
rsi = ta.momentum.RSIIndicator(close=hist_technical["Close"]).rsi().iloc[-1]
ma50 = hist_technical["Close"].rolling(window=50).mean().iloc[-1]
ma200 = hist_technical["Close"].rolling(window=200).mean().iloc[-1]

# Bollinger Bands
bb = ta.volatility.BollingerBands(close=hist_technical["Close"])
bb_upper = bb.bollinger_hband().iloc[-1]
bb_lower = bb.bollinger_lband().iloc[-1]

# Datos fundamentales
info = stock.info
pe_ratio = info.get("trailingPE", "N/A")
market_cap = info.get("marketCap", "N/A")
eps = info.get("trailingEps", "N/A")

# Mostrar tarjetas
cols = st.columns(3)
with cols[0]:
    st.markdown("<div class='metric-box'><h2>💰 Precio Actual</h2><p>${:,.2f}</p></div>".format(current_price), unsafe_allow_html=True)
with cols[1]:
    st.markdown("<div class='metric-box'><h2>🏔 Máximo Histórico</h2><p>${:,.2f}</p></div>".format(ath), unsafe_allow_html=True)
with cols[2]:
    st.markdown("<div class='metric-box'><h2>🚀 Upside Potencial</h2><p>{:+.2f}%</p></div>".format(upside), unsafe_allow_html=True)

cols2 = st.columns(3)
with cols2[0]:
    st.markdown("<div class='metric-box'><h2>📉 RSI</h2><p>{:.2f} - {}</p></div>".format(
        rsi, "🟢 Comprar" if rsi < 30 else "🔴 Vender" if rsi > 70 else "🟡 Neutral"
    ), unsafe_allow_html=True)
with cols2[1]:
    st.markdown("<div class='metric-box'><h2>📈 MA50 / MA200</h2><p>{:.2f} / {:.2f}</p></div>".format(ma50, ma200), unsafe_allow_html=True)
with cols2[2]:
    st.markdown("<div class='metric-box'><h2>📊 Bandas Bollinger</h2><p>U: {:.2f} / L: {:.2f}</p></div>".format(bb_upper, bb_lower), unsafe_allow_html=True)

cols3 = st.columns(3)
with cols3[0]:
    st.markdown("<div class='metric-box'><h2>🏦 P/E Ratio</h2><p>{}</p></div>".format(pe_ratio), unsafe_allow_html=True)
with cols3[1]:
    st.markdown("<div class='metric-box'><h2>💸 Market Cap</h2><p>${:,}</p></div>".format(market_cap), unsafe_allow_html=True)
with cols3[2]:
    st.markdown("<div class='metric-box'><h2>📘 EPS</h2><p>{}</p></div>".format(eps), unsafe_allow_html=True)

# Mostrar gráfico de TradingView embebido
st.markdown("### 📈 Gráfico interactivo de TradingView")
tv_code = f"""
<iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_{ticker}&symbol=NASDAQ%3A{ticker}&interval=1D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=[]&theme=dark&style=1&timezone=America%2FArgentina%2FBuenos_Aires&withdateranges=1&hidevolume=0" 
width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
"""
components.html(tv_code, height=500)
