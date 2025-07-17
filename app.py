import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="FinAdvisor AI")

# CSS personalizado
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

st.markdown("<h1 style='color:#ffffff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#cccccc;'>Descubrí oportunidades de inversión con datos en tiempo real y análisis técnico/fundamental.</p>", unsafe_allow_html=True)

# ======================
# ▶️ DASHBOARD DE INICIO
# ======================

tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]
data = yf.download(tickers, period="1d", interval="1m")['Adj Close'].iloc[-1]
prev_close = yf.download(tickers, period="2d", interval="1d")['Adj Close'].iloc[0]

st.markdown("<div class='section-title'>📊 Tendencias USA</div>", unsafe_allow_html=True)
cols = st.columns(5)

selected_ticker = None

for i, ticker in enumerate(tickers[:5]):
    change = ((data[ticker] - prev_close[ticker]) / prev_close[ticker]) * 100
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols[i]:
        if st.button(f"{ticker}\n\n${data[ticker]:.2f} ({change:.2f}%)"):
            selected_ticker = ticker
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{ticker}</div>
            <div class="price">${data[ticker]:.2f}</div>
            <div class="{color_class}">{change:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-title'>🔥 Más negociadas</div>", unsafe_allow_html=True)
cols2 = st.columns(5)
for i, ticker in enumerate(tickers[5:]):
    change = ((data[ticker] - prev_close[ticker]) / prev_close[ticker]) * 100
    color_class = "change-pos" if change > 0 else "change-neg"
    with cols2[i]:
        if st.button(f"{ticker}\n\n${data[ticker]:.2f} ({change:.2f}%)", key=f"vol_{ticker}"):
            selected_ticker = ticker
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{ticker}</div>
            <div class="price">${data[ticker]:.2f}</div>
            <div class="{color_class}">{change:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

# ======================
# ▶️ ANÁLISIS SI SELECCIONA UNA ACCIÓN
# ======================

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

    # MA
    st.markdown(f"<div class='metric-box'><h3>📈 MA50: {ma50:.2f} | MA200: {ma200:.2f} | Precio: {price_now:.2f}</h3>", unsafe_allow_html=True)
    if price_now > ma50 > ma200:
        st.markdown("<p>🟢 Tendencia alcista. Momentum positivo.</p></div>", unsafe_allow_html=True)
    elif price_now < ma50 < ma200:
        st.markdown("<p>🔴 Tendencia bajista. Cautela recomendada.</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p>🟡 Señal mixta. Esperar confirmación.</p></div>", unsafe_allow_html=True)

    # Bollinger
    st.markdown(f"<div class='metric-box'><h3>📊 Bollinger Bands</h3><p>Superior: {bb_upper:.2f} | Inferior: {bb_lower:.2f}</p>", unsafe_allow_html=True)
    if price_now >= bb_upper:
        st.markdown("<p>🚨 Precio rozando la banda superior. Riesgo de corrección.</p></div>", unsafe_allow_html=True)
    elif price_now <= bb_lower:
        st.markdown("<p>🟢 Precio tocando banda inferior. Potencial rebote técnico.</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p>📎 Dentro del canal. Volatilidad normal.</p></div>", unsafe_allow_html=True)

    # ATH
    st.markdown(f"<div class='metric-box'><h3>🏔 Máximo Histórico: {ath:.2f} | Upside: {upside:.2f}%</h3>", unsafe_allow_html=True)
    if upside > 30:
        st.markdown("<p>🚀 Potencial alto. Puede subir fuerte.</p></div>", unsafe_allow_html=True)
    elif upside < 10:
        st.markdown("<p>📉 Upside bajo. Ya está cerca del techo.</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p>📊 Potencial moderado. Evaluar junto a técnica.</p></div>", unsafe_allow_html=True)

    # Fundamentales
    st.markdown(f"<div class='metric-box'><h3>📘 Fundamentos</h3><p>PE: {pe} | EPS: {eps} | Market Cap: ${mkt_cap:,}</p>", unsafe_allow_html=True)
    if pe and pe < 15:
        st.markdown("<p>💲 PE bajo. Posible infravaloración.</p>", unsafe_allow_html=True)
    elif pe and pe > 30:
        st.markdown("<p>⚠️ PE alto. Podría estar sobrevalorada.</p>", unsafe_allow_html=True)
    if eps and eps > 0:
        st.markdown("<p>🟢 EPS positivo. La empresa gana dinero.</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p>🔴 EPS negativo. Riesgo de rentabilidad.</p></div>", unsafe_allow_html=True)

    # Resumen
    st.markdown(f"<div class='metric-box'><h3>🧠 Asistente AI</h3>", unsafe_allow_html=True)
    if rsi < 30 and upside > 25 and eps > 0:
        st.markdown("🟢 Escenario optimista. Entrada técnica válida.", unsafe_allow_html=True)
    elif rsi > 70 or price_now > bb_upper:
        st.markdown("🔴 Posible corrección. Cautela recomendada.", unsafe_allow_html=True)
    else:
        st.markdown("🟡 Esperar mejor oportunidad.", unsafe_allow_html=True)

    st.markdown("""
    <ul>
    <li>Si buscás entrada, RSI < 40 o rebote en MA50</li>
    <li>Si ya tenés, mantené mientras EPS siga positivo</li>
    <li>Zona objetivo: ${:.2f}</li>
    </ul>
    </div>
    """.format(ath), unsafe_allow_html=True)

    # TradingView
    st.markdown("### 📈 Gráfico interactivo")
    tv_widget = f"""
    <iframe src="https://s.tradingview.com/widgetembed/?symbol=NASDAQ:{selected_ticker}&interval=1D&theme=dark&style=1&timezone=America%2FBuenos_Aires"
    width="100%" height="500" frameborder="0" scrolling="no"></iframe>
    """
    components.html(tv_widget, height=500)

