import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import feedparser
import streamlit.components.v1 as components

# =======================
# Configuración
# =======================
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
.news-card {
    background-color: #1c1f26;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    display: flex;
    gap: 15px;
}
.news-img {
    width: 120px;
    height: 80px;
    object-fit: cover;
    border-radius: 8px;
}
.news-content { flex: 1; }
.news-title { font-size: 1.1em; font-weight: bold; color: #fff; }
.news-link { color: #c084fc; text-decoration: none; }
.rank-card {
    background-color: #1c1f26;
    border-radius: 12px;
    padding: 15px;
    margin: 10px;
    text-align: center;
}
.rank-img {
    width: 50px;
    height: 50px;
    border-radius: 8px;
}
.rank-title { font-weight: bold; color: #c084fc; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#fff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)

# =======================
# Estado
# =======================
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "AAPL"

# =======================
# Dataset S&P500
# =======================
@st.cache_data
def load_companies():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    df["SearchKey"] = df["Security"].fillna("").str.lower()
    return df

company_df = load_companies()

# Lista ADRs y LatAm
adr_latam = ["YPF", "GGAL", "BMA", "PAM", "CEPU", "SUPV", "TX", "TGS", "BBAR", "MELI"]

# =======================
# 🔥 Ranking Acciones con Mayor Potencial
# =======================
st.markdown("## 🚀 Acciones con Mayor Potencial (Ranking AI)")

@st.cache_data
def get_top_picks():
    tickers = company_df["Symbol"].tolist()[:70] + adr_latam
    ranking = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            df = stock.history(period="6mo")
            hist_all = stock.history(period="max")
            if df.empty: continue

            price = df["Close"].iloc[-1]
            ath = hist_all["Close"].max()
            upside = ((ath - price) / price) * 100

            # Técnicos
            rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
            ma50 = df["Close"].rolling(50).mean().iloc[-1]
            ma200 = df["Close"].rolling(200).mean().iloc[-1]
            macd = ta.trend.MACD(df["Close"])
            macd_val = macd.macd().iloc[-1]
            macd_signal = macd.macd_signal().iloc[-1]

            # Fundamentals
            info = stock.info
            pe = info.get("forwardPE", None)
            roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0
            fcf = info.get("freeCashflow", 0)
            logo = info.get("logo_url", "https://via.placeholder.com/50")
            name = info.get("shortName", t)
            sector = info.get("sector", "Desconocido")

            # Scoring
            score = 0
            if rsi < 40: score += 2
            if price > ma50 > ma200: score += 1
            if macd_val > macd_signal: score += 1
            if upside > 15: score += 2
            if price > ma200: score += 1
            if pe and pe < 20: score += 1
            if roe > 15: score += 1
            if fcf and fcf > 0: score += 1

            ranking.append({
                "Ticker": t,
                "Nombre": name,
                "Precio": f"${price:.2f}",
                "Upside": f"{upside:.0f}%",
                "Sector": sector,
                "Score": score,
                "Logo": logo
            })
        except:
            continue

    df_rank = pd.DataFrame(ranking).sort_values(by="Score", ascending=False).head(10)
    return df_rank

top_picks = get_top_picks()

# Mostrar Ranking con Cards
cols = st.columns(5)
for i, row in enumerate(top_picks.itertuples()):
    with cols[i % 5]:
        st.markdown(f"""
        <div class="rank-card">
            <img src="{row.Logo}" class="rank-img"/>
            <div class="rank-title">{row.Ticker}</div>
            <div>{row.Nombre}</div>
            <div>{row.Precio}</div>
            <div>Upside: {row.Upside}</div>
            <div>Sector: {row.Sector}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Analizar {row.Ticker}", key=f"rank_{row.Ticker}"):
            st.session_state.selected_ticker = row.Ticker

# =======================
# Buscador
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
# Análisis técnico + fundamental
# =======================
selected_ticker = st.session_state.selected_ticker
st.markdown(f"## ✅ Análisis y Recomendación: **{selected_ticker}**")

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

    info = stock.info
    pe = info.get("forwardPE", "N/A")
    roe = info.get("returnOnEquity", 0)
    fcf = info.get("freeCashflow", 0)

    # Recomendación extendida
    st.markdown(f"""
    ### 📌 {info.get('shortName', selected_ticker)} ({selected_ticker}) – Recomendación de inversión
    **Precio actual:** USD {price_now:.2f}  
    **Potencial upside 12 meses:** {upside:.1f}% (ATH: {ath:.2f})  
    **Valuación:** P/E: {pe}, ROE: {roe:.2%}, FCF: {fcf}  
    **Técnico:** RSI {rsi:.2f}, soporte {support:.2f}, resistencia {resistance:.2f}  
    """)

# =======================
# Noticias recientes
# =======================
st.markdown("### 📰 Noticias recientes")
rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={selected_ticker}&region=US&lang=en-US"
feed = feedparser.parse(rss_url)
if feed.entries:
    for entry in feed.entries[:5]:
        image = entry.get("media_content", [{}])[0].get("url", "https://via.placeholder.com/120")
        st.markdown(f"""
        <div class="news-card">
            <img src="{image}" class="news-img" />
            <div class="news-content">
                <a href="{entry.link}" class="news-link" target="_blank">
                    <div class="news-title">{entry.title}</div>
                </a>
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
