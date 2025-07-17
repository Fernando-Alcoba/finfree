import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="FinAdvisor AI")

# ========= CARGAR LISTA DE EMPRESAS =========
@st.cache_data
def load_company_list():
    url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed-symbols.csv"
    df = pd.read_csv(url)
    return df[["Symbol", "Company Name"]]

company_df = load_company_list()

# ========= BUSCADOR CON AUTOCOMPLETADO =========
st.markdown("### 🔍 Buscar empresa por nombre")
query = st.text_input("Escribí parte del nombre de la empresa (ej: Netflix, Apple)").lower()

filtered_df = company_df[company_df["Company Name"].fillna("").str.lower().str.contains(query, na=False)]
selected_ticker = None

if not filtered_df.empty:
    option = st.selectbox("Seleccioná la empresa:", filtered_df["Company Name"] + " (" + filtered_df["Symbol"] + ")")
    selected_ticker = option.split("(")[-1].replace(")", "").strip()
elif query:
    st.warning("⚠️ No se encontraron resultados para esa búsqueda.")

# ========= TICKERS DESTACADOS =========
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]
last_prices, prev_closes = {}, {}

for ticker in tickers:
    try:
        df = yf.Ticker(ticker).history(period="2d", interval="1m")
        if len(df) >= 2:
            last_prices[ticker] = df["Close"].iloc[-1]
            prev_closes[ticker] = df["Close"].iloc[0]
        else:
            last_prices[ticker] = None
            prev_closes[ticker] = None
    except:
        last_prices[ticker] = None
        prev_closes[ticker] = None

# ========= SECCIONES VISUALES =========
st.markdown("## 📊 Tendencias USA")
cols = st.columns(5)

for i, ticker in enumerate(tickers[:5]):
    price = last_prices[ticker]
    prev = prev_closes[ticker]
    change = ((price - prev) / prev) * 100 if price and prev else 0
    label = f"${price:.2f}" if price else "N/A"
    with cols[i]:
        if st.button(ticker, key=f"top_{ticker}"):
            selected_ticker = ticker
        st.markdown(f"{label} ({change:.2f}%)")

st.markdown("## 🔥 Más negociadas")
cols2 = st.columns(5)

for i, ticker in enumerate(tickers[5:]):
    price = last_prices[ticker]
    prev = prev_closes[ticker]
    change = ((price - prev) / prev) * 100 if price and prev else 0
    label = f"${price:.2f}" if price else "N/A"
    with cols2[i]:
        if st.button(ticker, key=f"bottom_{ticker}"):
            selected_ticker = ticker
        st.markdown(f"{label} ({change:.2f}%)")

# ========= ANÁLISIS =========
if selected_ticker:
    try:
        stock = yf.Ticker(selected_ticker)
        hist = stock.history(period="max")
        if hist.empty:
            st.error("No se encontraron datos históricos.")
        else:
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

            st.markdown(f"## 📌 Análisis de {selected_ticker}")

            # RSI
            st.markdown(f"**📉 RSI: {rsi:.2f}**")
            if rsi < 30:
                st.success("📉 Sobrevendido. Probabilidad de rebote: ALTA ✅")
            elif rsi > 70:
                st.warning("📈 Sobrecomprado. Riesgo de caída: ELEVADO ⚠️")
            else:
                st.info("📊 RSI neutral. Esperar confirmación.")

            # MA
            st.markdown(f"**📈 MA50: {ma50:.2f} | MA200: {ma200:.2f} | Precio: {price_now:.2f}**")
            if price_now > ma50 > ma200:
                st.success("🟢 Tendencia alcista.")
            elif price_now < ma50 < ma200:
                st.error("🔴 Tendencia bajista.")
            else:
                st.info("🟡 Señal mixta.")

            # Bollinger Bands
            st.markdown(f"**📊 Bollinger Bands**\n- Superior: {bb_upper:.2f}\n- Inferior: {bb_lower:.2f}")
            if price_now >= bb_upper:
                st.warning("🚨 Precio en banda superior. Riesgo de corrección.")
            elif price_now <= bb_lower:
                st.success("🟢 Precio en banda inferior. Potencial rebote.")
            else:
                st.info("📎 Dentro del canal.")

            # ATH
            st.markdown(f"**🏔 Máximo Histórico: {ath:.2f} | Upside: {upside:.2f}%**")

            # Fundamentos
            st.markdown("**📘 Fundamentos**")
            st.markdown(f"- PE: {pe}\n- EPS: {eps}\n- Market Cap: ${mkt_cap:,}" if mkt_cap else "- Datos no disponibles")

            # Gráfico interactivo
            st.markdown("### 📈 Gráfico interactivo")
            tv_widget = f"""
            <iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=1D&theme=dark&style=1&timezone=America%2FBuenos_Aires"
            width="100%" height="500" frameborder="0" scrolling="no"></iframe>
            """
            components.html(tv_widget, height=500)
    except Exception as e:
        st.error(f"❌ Error al obtener datos de {selected_ticker}: {e}")
