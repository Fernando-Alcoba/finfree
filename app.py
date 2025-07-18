import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import feedparser
import streamlit.components.v1 as components
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objects as go

# =======================
# CONFIG
# =======================
st.set_page_config(layout="wide", page_title="FinAdvisor AI")

# =======================
# CSS
# =======================
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
.marquee {
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    box-sizing: border-box;
    animation: marquee 20s linear infinite;
    font-size: 1.2em;
    background-color: #1c1f26;
    color: #fff;
    padding: 10px;
    border-bottom: 2px solid #c084fc;
}
@keyframes marquee {
    0% { transform: translate(0, 0); }
    100% { transform: translate(-100%, 0); }
}
.ticker-item { margin: 0 30px; }
.card { background-color: #1c1f26; border-radius: 12px; padding: 15px; text-align: center; }
.metric-box { background-color: #1c1f26; border-radius: 12px; padding: 15px; margin: 15px 0; }
.news-card { background-color: #1c1f26; border-radius: 12px; padding: 15px; margin-bottom: 15px; display: flex; gap: 15px; }
.news-img { width: 120px; height: 80px; object-fit: cover; border-radius: 8px; }
.news-content { flex: 1; }
.news-title { font-size: 1.1em; font-weight: bold; color: #fff; }
.news-link { color: #c084fc; text-decoration: none; }
.rank-card { background-color: #1c1f26; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 20px; }
.green { color: lime; font-weight: bold; }
.yellow { color: gold; font-weight: bold; }
.red { color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =======================
# Barra de cotizaciones en movimiento
# =======================
def render_ticker_bar():
    tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]
    prices = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            p = stock.fast_info.last_price
            prev = stock.fast_info.previous_close
            change = ((p - prev) / prev) * 100
            color = "lime" if change > 0 else "red"
            prices.append(f"<span class='ticker-item'>{t}: ${p:.2f} (<span style='color:{color};'>{change:.2f}%</span>)</span>")
        except:
            continue
    st.markdown(f"<div class='marquee'>{' '.join(prices)}</div>", unsafe_allow_html=True)

render_ticker_bar()

# =======================
# Sidebar Navegación
# =======================
page = st.sidebar.radio("📌 Navegación", ["Dashboard Principal", "Top Picks AI"])

# =======================
# Dataset
# =======================
@st.cache_data
def load_companies():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    df["SearchKey"] = df["Security"].fillna("").str.lower()
    return df

company_df = load_companies()
adr_latam = ["YPF", "GGAL", "BMA", "PAM", "CEPU", "SUPV", "TX", "TGS", "BBAR", "MELI"]

# =======================
# Página 1: Dashboard Principal
# =======================
if page == "Dashboard Principal":
    st.markdown("<h1 style='color:#fff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)

    # Estado
    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = "AAPL"

    # Buscador
    st.markdown("### 🔍 Buscar empresa")
    query = st.text_input("Ingresá el nombre o parte del nombre").lower()
    filtered_df = company_df[company_df["SearchKey"].str.contains(query, na=False)] if query else pd.DataFrame()

    if not filtered_df.empty:
        opciones = filtered_df["Security"] + " (" + filtered_df["Symbol"] + ")"
        seleccion = st.selectbox("Elegí la empresa:", opciones)
        if seleccion:
            st.session_state.selected_ticker = seleccion.split("(")[-1].replace(")", "").strip()

    selected_ticker = st.session_state.selected_ticker

    # Análisis técnico + fundamental
    stock = yf.Ticker(selected_ticker)
    df = stock.history(period="6mo")
    hist_all = stock.history(period="max")

    if df.empty:
        st.warning("No hay datos históricos.")
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

        # Modelo Prophet
        forecast_text = ""
        try:
            df_prophet = stock.history(period="1y")[["Close"]].reset_index()
            df_prophet = df_prophet.rename(columns={"Date": "ds", "Close": "y"})
            model = Prophet(daily_seasonality=True)
            model.fit(df_prophet)
            future = model.make_future_dataframe(periods=90)
            forecast = model.predict(future)
            price_30d = forecast.iloc[-60]["yhat"]
            price_90d = forecast.iloc[-1]["yhat"]
            forecast_text = f"**Predicción IA:** 30 días: ${price_30d:.2f} | 90 días: ${price_90d:.2f}"
        except:
            forecast_text = "No se pudo calcular la predicción IA."

        # Mostrar análisis
        st.markdown(f"""
        ### ✅ {info.get('shortName', selected_ticker)} ({selected_ticker})
        **Precio actual:** ${price_now:.2f}  
        **Upside a ATH:** {upside:.1f}%  
        **Valuación:** P/E: {pe}, ROE: {roe:.2%}, FCF: {fcf}  
        **Técnico:** RSI {rsi:.2f}, soporte {support:.2f}, resistencia {resistance:.2f}  
        {forecast_text}
        """)

    # Noticias
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

    # Gráfico TradingView
    st.markdown("### 📈 Gráfico interactivo")
    tv_widget = f"""
    <iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=1D&theme=dark&style=1"
    width="100%" height="500" frameborder="0" scrolling="no"></iframe>
    """
    components.html(tv_widget, height=500)

# =======================
# Página 2: Top Picks AI
# =======================
if page == "Top Picks AI":
    st.markdown("<h1 style='color:#fff;'>🚀 Ranking Acciones con Mayor Potencial</h1>", unsafe_allow_html=True)

    @st.cache_data
    def get_top_picks():
        tickers = company_df["Symbol"].tolist()[:50] + adr_latam
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

                rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]
                ma50 = df["Close"].rolling(50).mean().iloc[-1]
                ma200 = df["Close"].rolling(200).mean().iloc[-1]
                macd = ta.trend.MACD(df["Close"])
                macd_val = macd.macd().iloc[-1]
                macd_signal = macd.macd_signal().iloc[-1]

                info = stock.info
                pe = info.get("forwardPE", None)
                roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0
                logo = info.get("logo_url", "https://via.placeholder.com/50")
                name = info.get("shortName", t)

                score = 0
                if rsi < 40: score += 2
                if price > ma50 > ma200: score += 1
                if macd_val > macd_signal: score += 1
                if upside > 15: score += 2
                if pe and pe < 20: score += 1
                if roe > 15: score += 1

                ranking.append({
                    "Ticker": t,
                    "Nombre": name,
                    "Precio": f"${price:.2f}",
                    "Upside": upside,
                    "Score": score,
                    "Logo": logo
                })
            except:
                continue

        return pd.DataFrame(ranking).sort_values(by="Score", ascending=False).head(10)

    top_picks = get_top_picks()

    for row in top_picks.itertuples():
        color_class = "green" if row.Score >= 6 else "yellow" if row.Score >= 3 else "red"
        with st.container():
            st.markdown(f"""
            <div class="rank-card">
                <img src="{row.Logo}" style="width:50px;height:50px;"/>
                <h3>{row.Ticker} - {row.Nombre}</h3>
                <p>Precio: {row.Precio} | Upside: {row.Upside:.1f}%</p>
                <p class="{color_class}">Score AI: {row.Score}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Ver Predicción {row.Ticker}", key=f"btn_pred_{row.Ticker}"):
                stock = yf.Ticker(row.Ticker)
                df_prophet = stock.history(period="1y")[["Close"]].reset_index()
                df_prophet = df_prophet.rename(columns={"Date": "ds", "Close": "y"})
                model = Prophet(daily_seasonality=True)
                model.fit(df_prophet)
                future = model.make_future_dataframe(periods=90)
                forecast = model.predict(future)

                st.subheader(f"Predicción IA para {row.Ticker}")
                st.write(f"Precio proyectado a 30 días: ${forecast.iloc[-60]['yhat']:.2f}")
                st.write(f"Precio proyectado a 90 días: ${forecast.iloc[-1]['yhat']:.2f}")
                fig = plot_plotly(model, forecast)
                st.plotly_chart(fig)
