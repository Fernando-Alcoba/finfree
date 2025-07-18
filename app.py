import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components
import feedparser
import datetime

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
.news-card { display: flex; background: #1c1f26; border-radius: 12px; padding: 10px; margin-bottom: 10px; }
.news-card img { width: 80px; height: 80px; border-radius: 8px; margin-right: 10px; object-fit: cover; }
.news-content { flex: 1; }
.news-title { font-weight: bold; font-size: 1.1em; }
.reco-title { font-size: 1.4em; font-weight: bold; color: #f472b6; }
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
# Análisis técnico + fundamentals con recomendación profesional
# =======================
selected_ticker = st.session_state.selected_ticker
stock = yf.Ticker(selected_ticker)
df = stock.history(period="6mo")
hist_all = stock.history(period="max")
info = stock.info

st.markdown(f"## 📌 {info.get('shortName', selected_ticker)} ({selected_ticker}) – Recomendación de inversión ({datetime.datetime.now().strftime('%B %Y')})")

if df.empty:
    st.warning("No hay datos históricos para análisis.")
else:
    price_now = df["Close"].iloc[-1]
    rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    ma200 = df["Close"].rolling(200).mean().iloc[-1]
    bb = ta.volatility.BollingerBands(df["Close"])
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]
    macd = ta.trend.MACD(df["Close"])
    macd_val = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]
    support = df["Close"].min()
    resistance = df["Close"].max()
    ath = hist_all["Close"].max()
    upside = ((ath - price_now) / price_now) * 100

    # Fundamentals básicos
    pe = info.get("forwardPE", "N/A")
    roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else "N/A"
    fcf = info.get("freeCashflow", 0)

    st.markdown(f"""
    **Precio actual:** USD {price_now:.2f}  
    **Potencial upside 12 meses:** +{upside:.0f}% (objetivo ~USD {ath:.0f})  
    **Valuación:** P/E: {pe}, ROE: {roe}%, FCF: {fcf}  
    **Técnico:** RSI {rsi:.1f}, MA50 {ma50:.1f}, MA200 {ma200:.1f}, Soporte {support:.1f}, Resistencia {resistance:.1f}  
    """)

    st.markdown("---")
    st.markdown("### ✅ Conclusión")
    if upside > 20 and rsi < 70:
        st.success("Alta probabilidad de upside. Ideal para mantener o comprar en retrocesos.")
    elif rsi > 70:
        st.warning("Sobrecomprada. Podría corregir pronto. Mejor esperar.")
    else:
        st.info("Escenario mixto. Comprar parcialmente o esperar señales más claras.")

# =======================
# Noticias con imagen
# =======================
st.markdown("### 📰 Noticias recientes")
rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={selected_ticker}&region=US&lang=en-US"
feed = feedparser.parse(rss_url)

if feed.entries:
    for entry in feed.entries[:5]:
        img_url = f"https://logo.clearbit.com/{info.get('website', 'example.com')}"
        st.markdown(f"""
        <div class="news-card">
            <img src="{img_url}" alt="Logo">
            <div class="news-content">
                <div class="news-title"><a href="{entry.link}" target="_blank">{entry.title}</a></div>
                <div>{entry.published}</div>
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
