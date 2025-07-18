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
.card { background-color: #1c1f26; border-radius: 12px; padding: 15px; text-align: center; }
.price { font-size: 1.3em; font-weight: bold; }
.change-pos { color: lime; }
.change-neg { color: red; }
.card-title { font-weight: bold; font-size: 1.1em; color: #c084fc; }
.section-title { font-size: 1.6em; margin-top: 30px; color: #c084fc; }
.metric-box { border-radius: 12px; background-color: #1c1f26; padding: 15px; margin: 10px 0; }
.metric-title { color: #c084fc; font-size: 1.3em; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#fff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)

# =======================
# Estado
# =======================
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "AAPL"

# =======================
# Dataset S&P500 para buscador
# =======================
@st.cache_data
def load_companies():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    df["SearchKey"] = df["Security"].fillna("").str.lower()
    return df

company_df = load_companies()

# =======================
# Buscador de acciones
# =======================
st.markdown("### 🔍 Buscar empresa del S&P 500")
query = st.text_input("Ingresá el nombre o parte del nombre").lower()
filtered_df = company_df[company_df["SearchKey"].str.contains(query, na=False)] if query else pd.DataFrame()

if not filtered_df.empty:
    opciones = filtered_df["Security"] + " (" + filtered_df["Symbol"] + ")"
    seleccion = st.selectbox("Elegí la empresa:", opciones)
    if seleccion:
        st.session_state.selected_ticker = seleccion.split("(")[-1].replace(")", "").strip()

# =======================
# Tickers populares
# =======================
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]
last_prices, changes = {}, {}

for ticker in tickers:
    stock = yf.Ticker(ticker)
    try:
        price = stock.fast_info.last_price
        prev_close = stock.fast_info.previous_close
        change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
        last_prices[ticker], changes[ticker] = price, change
    except:
        last_prices[ticker], changes[ticker] = None, 0

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
# Análisis técnico avanzado
# =======================
selected_ticker = st.session_state.selected_ticker
st.markdown(f"### ✅ Análisis de: **{selected_ticker}**")

stock = yf.Ticker(selected_ticker)
df = stock.history(period="6mo")
hist_all = stock.history(period="max")

if df.empty:
    st.warning("No hay datos históricos para análisis.")
else:
    price_now = df["Close"].iloc[-1]
    rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    ma200 = df["Close"].rolling(200).mean().iloc[-1]

    # Bandas Bollinger
    bb = ta.volatility.BollingerBands(df["Close"])
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    # MACD
    macd = ta.trend.MACD(df["Close"])
    macd_val = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]

    # Soporte y resistencia últimos 3 meses
    support = df["Close"].min()
    resistance = df["Close"].max()

    # Upside vs ATH
    ath = hist_all["Close"].max()
    upside = ((ath - price_now) / price_now) * 100

    # Mostrar métricas
    st.markdown(f"""
    <div class="metric-box">
    <p class="metric-title">📌 Precio actual: ${price_now:.2f}</p>
    <p>RSI: {rsi:.2f} | MA50: {ma50:.2f} | MA200: {ma200:.2f}</p>
    <p>Bandas Bollinger: Superior {bb_upper:.2f} | Inferior {bb_lower:.2f}</p>
    <p>MACD: {macd_val:.2f} | Señal: {macd_signal:.2f}</p>
    <p>Soporte: {support:.2f} | Resistencia: {resistance:.2f}</p>
    <p>ATH: {ath:.2f} | Upside: {upside:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

    # =======================
    # Recomendación AI con fundamentos
    # =======================
    info = stock.info
    market_cap = info.get("marketCap", 0)
    pe_ratio = info.get("forwardPE", None)
    eps = info.get("forwardEps", None)
    div_yield = (info.get("dividendYield", 0) or 0) * 100

    score = 0
    if rsi < 30: score += 2
    if price_now > ma50 > ma200: score += 2
    if price_now <= bb_lower: score += 2
    if macd_val > macd_signal: score += 1
    if upside > 25: score += 2
    if pe_ratio and pe_ratio < 20: score += 2
    if div_yield > 1: score += 1

    if score >= 8:
        recomendacion = "🟢 Comprar (Alta probabilidad) – Señales técnicas fuertes y fundamentos atractivos."
    elif score >= 5:
        recomendacion = "🟡 Mantener (Escenario mixto) – Señales intermedias, monitorear evolución."
    else:
        recomendacion = "🔴 Vender (Baja probabilidad) – Señales débiles y fundamentos poco atractivos."

    st.markdown(f"""
    ### ✅ **Recomendación AI**
    {recomendacion}

    **Fundamentales Clave:**
    - Market Cap: {market_cap/1e9:.2f}B
    - P/E Ratio: {pe_ratio if pe_ratio else 'N/A'}
    - EPS Est.: {eps if eps else 'N/A'}
    - Dividend Yield: {div_yield:.2f}%

    **Upside esperado:** {upside:.2f}%
    **Técnicos:** RSI: {rsi:.2f} | MA50: {ma50:.2f} | MA200: {ma200:.2f}
    """)

# =======================
# Noticias (RSS Yahoo Finance con imagen fallback)
# =======================
st.markdown("### 📰 Noticias recientes")

def get_news_rss(ticker):
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    news_list = []
    for entry in feed.entries[:5]:
        img = "https://via.placeholder.com/120"  # Imagen por defecto
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "img": img
        })
    return news_list

news = get_news_rss(selected_ticker)

if news:
    for n in news:
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin-bottom:15px; background:#1c1f26; border-radius:12px; padding:10px;">
            <img src="{n['img']}" width="100" style="border-radius:8px; margin-right:15px;">
            <div>
                <a href="{n['link']}" target="_blank" style="color:#c084fc; font-size:1.1em; text-decoration:none;">{n['title']}</a>
                <p style="color:#888; font-size:0.9em;">{n['summary'][:100]}...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No hay noticias recientes.")

# =======================
# Gráfico TradingView
# =======================
st.markdown("### 📈 Gráfico interactivo")
tv_widget = f"""
<iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=1D&theme=dark&style=1"
width="100%" height="500" frameborder="0" scrolling="no"></iframe>
"""
components.html(tv_widget, height=500)
