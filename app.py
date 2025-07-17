import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Asesor de Acciones AI")

# 💄 Estilos
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
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

# Título principal
st.markdown("<h1 style='color:#c084fc;'>📊 Análisis de Acción Inteligente</h1>", unsafe_allow_html=True)

# ▶️ Selección de acción
ticker = st.sidebar.selectbox("Elegí una acción", ["AAPL", "MSFT", "TSLA", "GOOGL", "NVDA", "AMZN"])

# ▶️ Cargar datos
stock = yf.Ticker(ticker)
hist = stock.history(period="max")
price_now = hist["Close"].iloc[-1]
ath = hist["Close"].max()
upside = ((ath - price_now) / price_now) * 100

# ▶️ Técnicos
df = stock.history(period="6mo")
rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
ma50 = df["Close"].rolling(50).mean().iloc[-1]
ma200 = df["Close"].rolling(200).mean().iloc[-1]
bb = ta.volatility.BollingerBands(df["Close"])
bb_upper = bb.bollinger_hband().iloc[-1]
bb_lower = bb.bollinger_lband().iloc[-1]

# ▶️ Fundamentales
info = stock.info
pe = info.get("trailingPE", None)
eps = info.get("trailingEps", None)
mkt_cap = info.get("marketCap", None)

# ▶️ SECCIONES EXPLICATIVAS

# 1. RSI
st.markdown("### 📉 RSI (Índice de Fuerza Relativa)")
st.markdown(f"<div class='metric-box'><h3>RSI actual: {rsi:.2f}</h3>", unsafe_allow_html=True)
if rsi < 30:
    st.markdown("<p>📉 Está en sobreventa. Probabilidad de rebote: <span style='color:lime;'>ALTA ✅</span></p>", unsafe_allow_html=True)
elif rsi > 70:
    st.markdown("<p>📈 Está en sobrecompra. Riesgo de corrección: <span style='color:red;'>ELEVADO ⚠️</span></p>", unsafe_allow_html=True)
else:
    st.markdown("<p>📊 RSI neutral. Esperar confirmación del mercado.</p></div>", unsafe_allow_html=True)

# 2. Medias móviles
st.markdown("### 📈 Medias Móviles")
st.markdown(f"<div class='metric-box'><h3>MA50: {ma50:.2f} | MA200: {ma200:.2f} | Precio actual: {price_now:.2f}</h3>", unsafe_allow_html=True)
if price_now > ma50 > ma200:
    st.markdown("<p>🟢 Tendencia alcista consolidada. Momentum positivo.</p></div>", unsafe_allow_html=True)
elif price_now < ma50 < ma200:
    st.markdown("<p>🔴 Tendencia bajista. Cautela recomendada.</p></div>", unsafe_allow_html=True)
else:
    st.markdown("<p>🟡 Señal mixta. Esperar confirmación de tendencia.</p></div>", unsafe_allow_html=True)

# 3. Bollinger Bands
st.markdown("### 📊 Bandas de Bollinger")
st.markdown(f"<div class='metric-box'><h3>Banda superior: {bb_upper:.2f} | inferior: {bb_lower:.2f}</h3>", unsafe_allow_html=True)
if price_now >= bb_upper:
    st.markdown("<p>🚨 Precio rozando la banda superior. Posible corrección a la baja.</p></div>", unsafe_allow_html=True)
elif price_now <= bb_lower:
    st.markdown("<p>🟢 Precio tocando banda inferior. Potencial rebote técnico.</p></div>", unsafe_allow_html=True)
else:
    st.markdown("<p>📎 Precio dentro del canal. Volatilidad moderada.</p></div>", unsafe_allow_html=True)

# 4. Máximo histórico
st.markdown("### 🏔 Máximo Histórico")
st.markdown(f"<div class='metric-box'><h3>ATH: {ath:.2f} | Upside: {upside:.2f}%</h3>", unsafe_allow_html=True)
if upside > 30:
    st.markdown("<p>🚀 Upside significativo. Potencial de suba a mediano plazo.</p></div>", unsafe_allow_html=True)
elif upside < 10:
    st.markdown("<p>📉 Upside limitado. La acción ya está cerca de su pico histórico.</p></div>", unsafe_allow_html=True)
else:
    st.markdown("<p>📊 Potencial intermedio. Evaluar junto a otros factores.</p></div>", unsafe_allow_html=True)

# 5. Análisis Fundamental
st.markdown("### 📘 Análisis Fundamental")
st.markdown(f"<div class='metric-box'><h3>PE: {pe} | EPS: {eps} | Market Cap: ${mkt_cap:,}</h3>", unsafe_allow_html=True)
if pe and pe < 15:
    st.markdown("<p>💲 PE bajo. Posible infravaloración.</p>", unsafe_allow_html=True)
elif pe and pe > 30:
    st.markdown("<p>⚠️ PE alto. Podría estar sobrevalorada.</p>", unsafe_allow_html=True)
else:
    st.markdown("<p>📊 Valuación media.</p>", unsafe_allow_html=True)

if eps and eps > 0:
    st.markdown("<p>🟢 EPS positivo. La empresa está generando ganancias.</p></div>", unsafe_allow_html=True)
else:
    st.markdown("<p>🔴 EPS negativo. Riesgo de rentabilidad.</p></div>", unsafe_allow_html=True)

# ▶️ GRÁFICO DE TRADINGVIEW
st.markdown("### 📈 Gráfico en vivo (TradingView)")
tv_widget = f"""
<iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_{ticker}&symbol=NASDAQ%3A{ticker}&interval=1D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=[]&theme=dark&style=1&timezone=America%2FArgentina%2FBuenos_Aires&withdateranges=1&hidevolume=0" 
width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
"""
components.html(tv_widget, height=500)

# ▶️ 🔍 RESUMEN FINAL / ASISTENTE
st.markdown("## 🧠 Informe del Asistente Financiero AI")

# Evaluación general (semáforo)
if rsi < 30 and upside > 25 and eps > 0:
    estado = "🟢 **Condiciones favorables** para una oportunidad de entrada técnica."
elif rsi > 70 or price_now > bb_upper:
    estado = "🔴 **Posible corrección en curso.** Cautela recomendada."
else:
    estado = "🟡 **Escenario mixto.** Esperar confirmación o entrada en zona más clara."

# Recomendación estilo estrategia
st.markdown(f"""
<div class='metric-box'>
<h3>🎯 Estado Actual</h3>
<p>{estado}</p>
<h3>📌 Estrategia sugerida:</h3>
<ul>
<li>Si buscás entrada, considerá esperar un RSI < 40 o pullback a MA50</li>
<li>Si ya tenés la acción, monitoreá zona de ${ath:.2f} como techo técnico</li>
<li>Si EPS es positivo, mantené en largo plazo mientras RSI esté < 70</li>
</ul>
</div>
""", unsafe_allow_html=True)
