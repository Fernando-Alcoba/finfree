import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import feedparser
import streamlit.components.v1 as components
import xgboost as xgb
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

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
    width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box;
    animation: marquee 20s linear infinite; font-size: 1.2em;
    background-color: #1c1f26; color: #fff; padding: 10px; border-bottom: 2px solid #c084fc;
}
@keyframes marquee { 0% { transform: translate(0,0); } 100% { transform: translate(-100%,0); } }
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
# Barra de cotizaciones
# =======================
def render_ticker_bar():
    tickers = ["AAPL","MSFT","TSLA","AMZN","NVDA","GOOGL","META","JPM","DIS","MCD"]
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
# Dataset S&P500
# =======================
@st.cache_data
def load_companies():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    df["SearchKey"] = df["Security"].fillna("").str.lower()
    return df

company_df = load_companies()
adr_latam = ["YPF","GGAL","BMA","PAM","CEPU","SUPV","TX","TGS","BBAR","MELI"]

# =======================
# Implementación manual de RSI
# =======================
def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# =======================
# IA Predictiva (XGBoost)
# =======================
MODEL_PATH = "xgboost_model.pkl"

def feature_engineering(df):
    # Implementación manual de RSI para evitar errores en la biblioteca ta
    df["RSI"] = calculate_rsi(df["Close"])
    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    
    # Implementación manual de MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    
    df["Volume"] = df["Volume"]
    df.dropna(inplace=True)
    return df

def train_or_update_model(ticker):
    df = yf.download(ticker, period="2y")
    df = feature_engineering(df)

    df["Target_30"] = df["Close"].shift(-30)
    df["Target_90"] = df["Close"].shift(-90)
    df.dropna(inplace=True)

    X = df[["Close","RSI","MA50","MA200","MACD","Volume"]]
    y30 = df["Target_30"]
    y90 = df["Target_90"]

    X_train, X_test, y_train_30, y_test_30 = train_test_split(X, y30, test_size=0.2, shuffle=False)
    X_train_90, X_test_90, y_train_90, y_test_90 = train_test_split(X, y90, test_size=0.2, shuffle=False)

    if os.path.exists(MODEL_PATH):
        model_30, model_90 = joblib.load(MODEL_PATH)
    else:
        model_30 = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05)
        model_90 = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05)

    model_30.fit(X_train, y_train_30)
    model_90.fit(X_train_90, y_train_90)

    preds_30 = model_30.predict(X_test)
    preds_90 = model_90.predict(X_test_90)

    mae30 = mean_absolute_error(y_test_30, preds_30)
    mae90 = mean_absolute_error(y_test_90, preds_90)

    joblib.dump((model_30, model_90), MODEL_PATH)

    last_row = X.iloc[[-1]]
    pred_30d = model_30.predict(last_row)[0]
    pred_90d = model_90.predict(last_row)[0]

    return pred_30d, pred_90d, mae30, mae90

# =======================
# Página 1: Dashboard
# =======================
if page == "Dashboard Principal":
    st.markdown("<h1 style='color:#fff;'>👋 Bienvenido a FinAdvisor AI</h1>", unsafe_allow_html=True)

    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = "AAPL"

    st.markdown("### 🔍 Buscar empresa")
    query = st.text_input("Ingresá el nombre o parte del nombre").lower()
    filtered_df = company_df[company_df["SearchKey"].str.contains(query, na=False)] if query else pd.DataFrame()

    if not filtered_df.empty:
        opciones = filtered_df["Security"] + " (" + filtered_df["Symbol"] + ")"
        seleccion = st.selectbox("Elegí la empresa:", opciones)
        if seleccion:
            st.session_state.selected_ticker = seleccion.split("(")[-1].replace(")", "").strip()

    selected_ticker = st.session_state.selected_ticker
    stock = yf.Ticker(selected_ticker)
    df = stock.history(period="6mo")

    if df.empty:
        st.warning("No hay datos históricos.")
    else:
        st.subheader(f"✅ Análisis de {selected_ticker}")
        pred_30d, pred_90d, mae30, mae90 = train_or_update_model(selected_ticker)
        current_price = df['Close'].iloc[-1]
        
        # Calcular cambios porcentuales
        change_30d = ((pred_30d - current_price) / current_price) * 100
        change_90d = ((pred_90d - current_price) / current_price) * 100
        
        # Determinar colores según los cambios
        color_30d = "lime" if change_30d > 0 else "red"
        color_90d = "lime" if change_90d > 0 else "red"
        
        st.markdown(f"""
        **Predicción IA:**  
        - Precio actual: ${current_price:.2f}  
        - 30 días: ${pred_30d:.2f} (<span style='color:{color_30d};'>{change_30d:.2f}%</span>) 
        - 90 días: ${pred_90d:.2f} (<span style='color:{color_90d};'>{change_90d:.2f}%</span>) 
        - Error esperado (MAE): 30d={mae30:.2f}, 90d={mae90:.2f}  
        """, unsafe_allow_html=True)

    # Noticias
    st.markdown("### 📰 Noticias recientes")
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={selected_ticker}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"**[{entry.title}]({entry.link})**")
    else:
        st.info("No hay noticias.")

# =======================
# Página 2: Ranking IA
# =======================
if page == "Top Picks AI":
    st.markdown("<h1 style='color:#fff;'>🚀 Ranking Acciones con Mayor Potencial</h1>", unsafe_allow_html=True)
    tickers = ["AAPL","MSFT","TSLA","AMZN","NVDA","GOOGL","META","JPM","DIS","MCD"] + adr_latam
    ranking = []
    
    with st.spinner('🔍 Analizando acciones...'):
        for t in tickers:
            try:
                pred_30d, pred_90d, _, _ = train_or_update_model(t)
                current_price = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
                upside_30 = ((pred_30d - current_price) / current_price) * 100
                ranking.append({
                    "Ticker": t, 
                    "Precio": current_price, 
                    "Pred 30d": pred_30d, 
                    "Potencial %": upside_30
                })
            except Exception as e:
                st.error(f"Error con {t}: {str(e)}")
                continue
    
    if ranking:
        df_rank = pd.DataFrame(ranking).sort_values(by="Potencial %", ascending=False).head(10)
        
        # Formatear y aplicar estilos
        df_rank["Precio"] = df_rank["Precio"].apply(lambda x: f"${x:.2f}")
        df_rank["Pred 30d"] = df_rank["Pred 30d"].apply(lambda x: f"${x:.2f}")
        df_rank["Potencial %"] = df_rank["Potencial %"].apply(lambda x: f"{x:.2f}%")
        
        # Resaltar valores positivos/negativos
        def color_potential(val):
            try:
                num = float(val.replace('%', ''))
                color = 'green' if num > 0 else 'red'
                return f'color: {color}; font-weight: bold'
            except:
                return ''
        
        styled_df = df_rank.style.applymap(color_potential, subset=['Potencial %'])
        
        # Mostrar tabla formateada
        st.table(styled_df)
    else:
        st.warning("No se pudo generar el ranking. Intente nuevamente.")
