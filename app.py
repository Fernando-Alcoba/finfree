import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components

# Configurar la página
st.set_page_config(page_title="FinAdvisor AI", layout="wide")

# Título y descripción
st.markdown("""
    <h1 style='font-size: 3em; color: #0e1117;'>💹 FinAdvisor AI</h1>
    <p style='font-size: 1.2em; color: #5c5c5c;'>Comparador de acciones en tiempo real con gráficos interactivos de TradingView.</p>
    <hr style='border: 1px solid #ddd;'/>
""", unsafe_allow_html=True)

# Lista de acciones
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL", "META", "NVDA"]

# Sidebar para elegir el ticker
selected_ticker = st.sidebar.selectbox("📌 Elegí una acción", tickers)

# Mostrar gráfico interactivo (TradingView widget)
st.markdown(f"### 📈 Gráfico en vivo de {selected_ticker}")
tradingview_widget = f"""
<iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_{selected_ticker}&symbol=NASDAQ%3A{selected_ticker}&interval=60&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=[]&theme=light&style=1&timezone=America%2FArgentina%2FBuenos_Aires&withdateranges=1&hidevolume=0" 
    width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
"""
components.html(tradingview_widget, height=500)

# Datos en tabla
st.markdown("### 💵 Comparador de precios y variación")

# Descargar datos
data = yf.download(tickers, period="1d", interval="1m")['Adj Close'].iloc[-1]
hist_data = yf.download(tickers, period="5d", interval="1d")['Adj Close']
variation = (hist_data.iloc[-1] - hist_data.iloc[-2]) / hist_data.iloc[-2] * 100

# Crear DataFrame
df = pd.DataFrame({
    "Ticker": tickers,
    "Precio Actual (USD)": data.values.round(2),
    "Variación % Día": variation.values.round(2)
})

# Colorear variaciones positivas y negativas
def highlight_variation(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}'

# Mostrar tabla con formato
st.dataframe(df.style.applymap(highlight_variation, subset=["Variación % Día"])
             .format({"Precio Actual (USD)": "${:,.2f}", "Variación % Día": "{:+.2f}%"}))

st.caption("💡 Los datos se actualizan automáticamente cada minuto durante horario de mercado.")
