import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import streamlit.components.v1 as components
import requests

st.set_page_config(layout="wide", page_title="FinAdvisor AI")

# —— CARGAR LISTA DE EMPRESAS ——
@st.cache_data
def load_company_list():
    url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed-symbols.csv"
    df = pd.read_csv(url)
    return df[["Symbol", "Company Name"]].dropna()

company_df = load_company_list()

# —— BUSCADOR CON AUTOCOMPLETADO ——
st.markdown("### 🔍 Buscar empresa por nombre")
query = st.text_input("Escribí parte del nombre de la empresa...").lower()
filtered_df = company_df[company_df["Company Name"].str.lower().str.contains(query, na=False)]
selected_ticker = None
if not filtered_df.empty and query:
    option = st.selectbox("Seleccioná la empresa:", filtered_df["Company Name"] + " (" + filtered_df["Symbol"] + ")")
    selected_ticker = option.split("(")[-1].replace(")", "").strip()
elif query:
    st.warning("⚠️ No se encontraron resultados.")

# —— TICKERS DESTACADOS ——
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "JPM", "DIS", "MCD"]
last_prices, prev_closes = {}, {}
for t in tickers:
    try:
        df = yf.Ticker(t).history(period="2d", interval="1m")
        if len(df) >= 2:
            last_prices[t] = df["Close"].iloc[-1]; prev_closes[t] = df["Close"].iloc[0]
        else:
            last_prices[t] = prev_closes[t] = None
    except:
        last_prices[t] = prev_closes[t] = None

st.markdown("## 📊 Tendencias USA")
cols = st.columns(5)
for i, t in enumerate(tickers[:5]):
    price, prev = last_prices[t], prev_closes[t]
    change = ((price - prev) / prev) * 100 if price and prev else 0
    label = f"${price:.2f}" if price else "N/A"
    with cols[i]:
        if st.button(t, key=f"top_{t}"): selected_ticker = t
        st.markdown(f"{t}: {label} ({change:.2f}%)")

st.markdown("## 🔥 Más negociadas")
cols2 = st.columns(5)
for i, t in enumerate(tickers[5:]):
    price, prev = last_prices[t], prev_closes[t]
    change = ((price - prev) / prev) * 100 if price and prev else 0
    label = f"${price:.2f}" if price else "N/A"
    with cols2[i]:
        if st.button(t, key=f"bottom_{t}"): selected_ticker = t
        st.markdown(f"{t}: {label} ({change:.2f}%)")

# —— ANÁLISIS + GRÁFICO + NOTICIAS ——
if selected_ticker:
    cols_main = st.columns([3,1])
    with cols_main[0]:
        stock = yf.Ticker(selected_ticker)
        hist = stock.history(period="max")
        if hist.empty:
            st.error("No se encontraron datos históricos.")
        else:
            price_now = hist["Close"].iloc[-1]; ath = hist["Close"].max()
            upside = (ath-price_now)/price_now*100
            df6 = stock.history(period="6mo")
            rsi = ta.momentum.RSIIndicator(df6["Close"]).rsi().iloc[-1]
            ma50 = df6["Close"].rolling(50).mean().iloc[-1]
            ma200 = df6["Close"].rolling(200).mean().iloc[-1]
            bb = ta.volatility.BollingerBands(df6["Close"])
            bb_u, bb_l = bb.bollinger_hband().iloc[-1], bb.bollinger_lband().iloc[-1]
            info = stock.info; pe = info.get("trailingPE"); eps = info.get("trailingEps"); mkt = info.get("marketCap")

            st.markdown(f"## 📌 Análisis de {selected_ticker}")
            st.markdown(f"**RSI:** {rsi:.2f}  •  **MA50/200:** {ma50:.2f}/{ma200:.2f}  •  **Precio:** {price_now:.2f}")
            st.markdown(f"**Bollinger:** Superior {bb_u:.2f}, Inferior {bb_l:.2f}")
            st.markdown(f"**ATH:** {ath:.2f}  •  **Upside:** {upside:.2f}%")
            st.markdown(f"**Fundamentos:** PE={pe} EPS={eps} MarketCap=${mkt:,}")
            st.markdown("### 📈 Gráfico interactivo")
            iframe = f"""<iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=1D&theme=dark" width="100%" height="400"></iframe>"""
            components.html(iframe, height=420)
    with cols_main[1]:
        st.markdown("### 🗞 Noticias recientes")
        # — Extraer noticias relevantes según ticker —
        for nid in ["turn0news18","turn0news19","turn0news20","turn0news24","turn0news25","turn0news26"]:
            st.write("• ", end="")
            if selected_ticker == "MSFT" and nid in ["turn0news18","turn0news24","turn0news25","turn0news26"]:
                st.markdown(f"{web.run('')}")  # placeholder
            if selected_ticker == "AAPL" and nid in ["turn0news19","turn0news20"]:
                st.markdown(f"{web.run('')}")

# — NAVLIST PARA FUENTES DESTACADAS —
st.markdown("")  # espacio
nav_ids = []
if selected_ticker == "MSFT":
    nav_ids = ["turn0news18","turn0news24","turn0news25","turn0news26"]
elif selected_ticker == "AAPL":
    nav_ids = ["turn0news19","turn0news20"]
if nav_ids:
    st.markdown("")  # espacio
    st.navlist("Noticias destacadas", ",".join(nav_ids))
