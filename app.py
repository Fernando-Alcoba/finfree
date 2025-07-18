import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import numpy as np
import json
from bs4 import BeautifulSoup
import translators as ts

# =======================
# CONFIGURACIÓN RÁPIDA
# =======================
st.set_page_config(layout="wide", page_title="FinAdvisor Pro", page_icon="📈")

# =======================
# ESTILOS OPTIMIZADOS
# =======================
st.markdown("""
<style>
:root {
    --primary: #2563eb;
    --secondary: #1d4ed8;
    --dark: #1e293b;
    --darker: #0f172a;
    --light: #f1f5f9;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', sans-serif;
}

body {
    background-color: var(--darker);
    color: var(--light);
    overflow-x: hidden;
}

.header {
    background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 100%);
    padding: 1.5rem;
    border-radius: 0 0 15px 15px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.search-container {
    background-color: rgba(30, 41, 59, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.section-title {
    color: var(--primary);
    font-size: 1.5rem;
    font-weight: 700;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--primary);
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}

.stock-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
    border-radius: 12px;
    padding: 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.stock-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
    border-color: var(--primary);
}

.stock-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.stock-ticker {
    font-weight: 700;
    font-size: 1.2rem;
    color: var(--light);
}

.stock-price {
    font-weight: 700;
    font-size: 1.2rem;
}

.positive {
    color: var(--success);
}

.negative {
    color: var(--danger);
}

.neutral {
    color: var(--warning);
}

.stock-volume {
    color: #94a3b8;
    font-size: 0.9rem;
}

.stock-change {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
}

.news-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}

.news-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.news-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
    border-color: var(--primary);
}

.news-img-container {
    height: 180px;
    overflow: hidden;
}

.news-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.news-card:hover .news-img {
    transform: scale(1.05);
}

.news-content {
    padding: 1.2rem;
}

.news-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    line-height: 1.4;
}

.news-summary {
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.5;
    margin-bottom: 1rem;
}

.news-footer {
    display: flex;
    justify-content: space-between;
    color: #64748b;
    font-size: 0.85rem;
}

.chart-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.tradingview-widget-container {
    height: 500px;
    border-radius: 10px;
    overflow: hidden;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}

.stat-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
    border-radius: 12px;
    padding: 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0.5rem 0;
}

.stat-label {
    color: #94a3b8;
    font-size: 0.95rem;
}

.recommendation-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.recommendation-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.recommendation-icon {
    font-size: 2rem;
    margin-right: 1rem;
}

.buy { color: var(--success); }
.sell { color: var(--danger); }
.hold { color: var(--warning); }

.recommendation-title {
    font-size: 1.5rem;
    font-weight: 700;
}

.recommendation-content {
    line-height: 1.6;
}

.recommendation-content p {
    margin-bottom: 0.8rem;
}

.recommendation-content ul {
    padding-left: 1.5rem;
    margin-bottom: 1rem;
}

.recommendation-content li {
    margin-bottom: 0.5rem;
}

.footer {
    text-align: center;
    padding: 1.5rem;
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* Animaciones */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.card {
    animation: fadeIn 0.5s ease-out;
    animation-fill-mode: both;
}

/* Retrasos para animaciones escalonadas */
.card:nth-child(1) { animation-delay: 0.1s; }
.card:nth-child(2) { animation-delay: 0.2s; }
.card:nth-child(3) { animation-delay: 0.3s; }
.card:nth-child(4) { animation-delay: 0.4s; }
.card:nth-child(5) { animation-delay: 0.5s; }
</style>
""", unsafe_allow_html=True)

# =======================
# FUNCIONES OPTIMIZADAS
# =======================

# Caché para datos de acciones
@st.cache_data(ttl=3600, show_spinner=False)
def load_stock_data():
    return pd.DataFrame([
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical"},
        {"symbol": "META", "name": "Meta Platforms, Inc.", "sector": "Communication"},
        {"symbol": "TSLA", "name": "Tesla, Inc.", "sector": "Automotive"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services"},
        {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services"},
        {"symbol": "PG", "name": "Procter & Gamble", "sector": "Consumer Defensive"},
        {"symbol": "MA", "name": "Mastercard Incorporated", "sector": "Financial Services"},
        {"symbol": "DIS", "name": "The Walt Disney Company", "sector": "Entertainment"},
        {"symbol": "PYPL", "name": "PayPal Holdings, Inc.", "sector": "Financial Services"},
        {"symbol": "ADBE", "name": "Adobe Inc.", "sector": "Technology"},
        {"symbol": "NFLX", "name": "Netflix, Inc.", "sector": "Entertainment"},
        {"symbol": "CRM", "name": "Salesforce, Inc.", "sector": "Technology"},
        {"symbol": "PEP", "name": "PepsiCo, Inc.", "sector": "Consumer Defensive"},
        {"symbol": "KO", "name": "The Coca-Cola Company", "sector": "Consumer Defensive"},
        {"symbol": "INTC", "name": "Intel Corporation", "sector": "Technology"},
        {"symbol": "CSCO", "name": "Cisco Systems, Inc.", "sector": "Technology"}
    ])

# Datos de mercado en tiempo real (simplificado para velocidad)
@st.cache_data(ttl=60, show_spinner=False)
def get_realtime_prices():
    # En un entorno real, aquí se conectaría a una API rápida de precios
    return {
        "AAPL": {"price": 185.20, "change": 1.25, "volume": 58203120},
        "MSFT": {"price": 340.65, "change": 0.78, "volume": 27459321},
        "GOOGL": {"price": 138.42, "change": -0.32, "volume": 19874523},
        "AMZN": {"price": 178.90, "change": 2.15, "volume": 43782910},
        "META": {"price": 480.30, "change": -1.05, "volume": 18743291},
        "TSLA": {"price": 265.50, "change": 5.32, "volume": 78291038},
        "NVDA": {"price": 885.60, "change": 3.78, "volume": 48291047},
        "JPM": {"price": 195.75, "change": -0.45, "volume": 12874532},
        "V": {"price": 280.40, "change": 0.92, "volume": 8749321},
        "PG": {"price": 162.30, "change": 0.35, "volume": 7432198},
        "MA": {"price": 425.80, "change": 1.20, "volume": 5321874},
        "DIS": {"price": 112.60, "change": -0.85, "volume": 12874321},
        "PYPL": {"price": 68.90, "change": 3.25, "volume": 18743210},
        "ADBE": {"price": 525.40, "change": -0.65, "volume": 2874312},
        "NFLX": {"price": 620.30, "change": 2.15, "volume": 3874321},
        "CRM": {"price": 300.75, "change": -1.20, "volume": 4873210},
        "PEP": {"price": 178.20, "change": 0.45, "volume": 5432198},
        "KO": {"price": 62.50, "change": 0.15, "volume": 8743219},
        "INTC": {"price": 44.30, "change": -1.25, "volume": 38743219},
        "CSCO": {"price": 52.80, "change": 0.30, "volume": 18743210}
    }

# Acciones con mayor potencial (datos precalculados)
@st.cache_data(ttl=3600, show_spinner=False)
def get_high_potential_stocks():
    return [
        {"symbol": "PYPL", "name": "PayPal", "potential": 28.5, "reason": "Recuperación en pagos digitales"},
        {"symbol": "TSLA", "name": "Tesla", "potential": 22.3, "reason": "Nuevos modelos y expansión global"},
        {"symbol": "AMZN", "name": "Amazon", "potential": 19.7, "reason": "Crecimiento en AWS y comercio"},
        {"symbol": "NVDA", "name": "NVIDIA", "potential": 18.9, "reason": "Demanda de chips para AI"},
        {"symbol": "DIS", "name": "Disney", "potential": 17.4, "reason": "Recuperación de parques y streaming"},
        {"symbol": "GOOGL", "name": "Alphabet", "potential": 15.8, "reason": "Dominio en búsqueda y publicidad"},
        {"symbol": "META", "name": "Meta", "potential": 14.2, "reason": "Eficiencia en metaverso y publicidad"}
    ]

# Noticias financieras con caché
@st.cache_data(ttl=600, show_spinner=False)
def get_financial_news():
    # Fuente de noticias en español
    feed = feedparser.parse("https://www.eleconomista.es/rss/rss-ultimas-noticias.php")
    news_items = []
    
    for entry in feed.entries[:10]:
        # Extraer imagen de la noticia
        img_url = None
        if 'media_content' in entry and entry.media_content:
            img_url = entry.media_content[0]['url']
        elif 'summary' in entry:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and 'src' in img_tag.attrs:
                img_url = img_tag['src']
        
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").strftime("%d/%m/%Y %H:%M"),
            "summary": entry.summary.split('</p>')[0].replace('<p>', '').strip() if 'summary' in entry else "",
            "image": img_url
        })
    
    return news_items

# Datos fundamentales (simplificado)
@st.cache_data(ttl=3600, show_spinner=False)
def get_fundamental_data(symbol):
    # Datos de ejemplo - en producción usaría yfinance o una API
    fundamentals = {
        "AAPL": {
            "market_cap": "2.8T",
            "pe_ratio": 29.5,
            "eps": 6.13,
            "dividend_yield": 0.55,
            "beta": 1.21,
            "profit_margin": 25.3,
            "analyst_target": 195.00
        },
        "MSFT": {
            "market_cap": "2.5T",
            "pe_ratio": 35.2,
            "eps": 9.65,
            "dividend_yield": 0.76,
            "beta": 0.89,
            "profit_margin": 36.4,
            "analyst_target": 350.00
        },
        "TSLA": {
            "market_cap": "820B",
            "pe_ratio": 68.3,
            "eps": 3.62,
            "dividend_yield": 0.00,
            "beta": 2.05,
            "profit_margin": 15.8,
            "analyst_target": 280.00
        },
        "NVDA": {
            "market_cap": "1.2T",
            "pe_ratio": 75.4,
            "eps": 11.93,
            "dividend_yield": 0.02,
            "beta": 1.50,
            "profit_margin": 42.6,
            "analyst_target": 950.00
        }
    }
    
    # Datos por defecto si no se encuentra el símbolo
    return fundamentals.get(symbol, {
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "eps": "N/A",
        "dividend_yield": "N/A",
        "beta": "N/A",
        "profit_margin": "N/A",
        "analyst_target": "N/A"
    })

# Recomendación IA (simulada para demostración)
def get_ai_recommendation(symbol):
    # Simulamos un retraso de análisis
    time.sleep(1.5)
    
    # En producción real, aquí se ejecutaría el modelo de IA
    recommendations = {
        "AAPL": {
            "recommendation": "COMPRAR",
            "icon": "📈",
            "confidence": "Alta",
            "price_target": 205.00,
            "upside": 10.7,
            "time_frame": "3-6 meses",
            "reasoning": [
                "Fuerte crecimiento en servicios y ecosistema",
                "Innovación continua en productos",
                "Balance sólido con alto flujo de caja",
                "Demanda constante de productos premium"
            ],
            "strategy": "Comprar en niveles actuales con objetivo a $205. Stop loss en $175."
        },
        "MSFT": {
            "recommendation": "MANTENER",
            "icon": "⏸️",
            "confidence": "Moderada",
            "price_target": 355.00,
            "upside": 4.2,
            "time_frame": "6-12 meses",
            "reasoning": [
                "Liderazgo en cloud computing con Azure",
                "Crecimiento estable en software empresarial",
                "Integración exitosa de adquisiciones",
                "Exposición a múltiples tendencias tecnológicas"
            ],
            "strategy": "Mantener posición actual. Considerar compras en retrocesos a $325."
        },
        "TSLA": {
            "recommendation": "COMPRAR",
            "icon": "📈",
            "confidence": "Moderada",
            "price_target": 310.00,
            "upside": 16.8,
            "time_frame": "6-12 meses",
            "reasoning": [
                "Lanzamiento exitoso de nuevos modelos",
                "Expansión global de infraestructura de carga",
                "Liderazgo en tecnología de baterías",
                "Potencial en vehículos autónomos"
            ],
            "strategy": "Acumular en retrocesos. Objetivo inicial $300, objetivo final $350."
        },
        "NVDA": {
            "recommendation": "COMPRAR",
            "icon": "📈",
            "confidence": "Alta",
            "price_target": 1000.00,
            "upside": 12.9,
            "time_frame": "12-18 meses",
            "reasoning": [
                "Demanda explosiva por chips de AI",
                "Posicionamiento único en mercado gaming",
                "Crecimiento en centros de datos",
                "Ventajas tecnológicas sostenibles"
            ],
            "strategy": "Comprar en niveles actuales. Objetivo a $950 con stop loss en $800."
        }
    }
    
    # Recomendación por defecto si no se encuentra el símbolo
    return recommendations.get(symbol, {
        "recommendation": "ANALIZAR",
        "icon": "🔍",
        "confidence": "Moderada",
        "price_target": "N/A",
        "upside": "N/A",
        "time_frame": "N/A",
        "reasoning": ["No hay suficiente información para esta acción"],
        "strategy": "Investigar más antes de tomar decisión"
    })

# =======================
# INTERFAZ DE USUARIO
# =======================
def main():
    # Estado de la sesión para controlar la acción seleccionada
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = None
    
    # Página de inicio
    if st.session_state.selected_stock is None:
        show_home_page()
    else:
        show_stock_detail(st.session_state.selected_stock)

def show_home_page():
    """Muestra la página de inicio con todas las secciones principales"""
    # Encabezado
    st.markdown(f"""
    <div class="header">
        <h1 style="margin-bottom: 0.5rem;">FinAdvisor Pro</h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">Plataforma inteligente para inversiones en bolsa</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Buscador de acciones
    with st.container():
        st.markdown("""
        <div class="search-container">
            <h3 style="margin-bottom: 1rem;">🔍 Buscar Acción</h3>
        """, unsafe_allow_html=True)
        
        stock_data = load_stock_data()
        realtime_prices = get_realtime_prices()
        
        # Buscador por nombre o símbolo
        search_query = st.text_input("Ingrese nombre o símbolo de la acción:", "", key="search_input")
        
        # Filtrado de acciones
        filtered_stocks = stock_data
        if search_query:
            mask = stock_data['name'].str.contains(search_query, case=False) | stock_data['symbol'].str.contains(search_query, case=False)
            filtered_stocks = stock_data[mask]
        
        # Mostrar resultados en un selectbox con vista previa
        if not filtered_stocks.empty:
            stock_options = filtered_stocks.apply(
                lambda row: f"{row['symbol']} - {row['name']} ({realtime_prices.get(row['symbol'], {}).get('price', 'N/A')})", 
                axis=1
            ).tolist()
            
            selected_option = st.selectbox("Seleccione una acción:", stock_options)
            
            if selected_option:
                selected_symbol = selected_option.split(" - ")[0]
                if st.button("Ver análisis completo", type="primary"):
                    st.session_state.selected_stock = selected_symbol
                    st.rerun()
        else:
            st.info("No se encontraron acciones que coincidan con la búsqueda")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Sección de acciones más negociadas
    st.markdown('<div class="section-title">📈 Acciones Más Negociadas Hoy</div>', unsafe_allow_html=True)
    
    # Obtener datos de volumen
    volume_data = []
    for symbol, data in get_realtime_prices().items():
        stock_info = stock_data[stock_data['symbol'] == symbol]
        if not stock_info.empty:
            volume_data.append({
                "symbol": symbol,
                "name": stock_info.iloc[0]['name'],
                "price": data['price'],
                "change": data['change'],
                "volume": data['volume']
            })
    
    # Ordenar por volumen descendente
    volume_data_sorted = sorted(volume_data, key=lambda x: x['volume'], reverse=True)[:8]
    
    # Mostrar en grid
    with st.container():
        st.markdown('<div class="card-grid">', unsafe_allow_html=True)
        
        for stock in volume_data_sorted:
            change_class = "positive" if stock['change'] >= 0 else "negative"
            change_icon = "▲" if stock['change'] >= 0 else "▼"
            
            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-header">
                    <div class="stock-ticker">{stock['symbol']}</div>
                    <div class="stock-price">${stock['price']:.2f}</div>
                </div>
                <div class="stock-name" style="color: #94a3b8; margin-bottom: 0.8rem;">{stock['name']}</div>
                <div class="stock-volume">Volumen: {stock['volume']/1e6:.2f}M</div>
                <div class="stock-change {change_class}">
                    {change_icon} {abs(stock['change']):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección de acciones con mayor potencial
    st.markdown('<div class="section-title">🚀 Acciones con Mayor Potencial</div>', unsafe_allow_html=True)
    
    # Obtener acciones con potencial
    potential_stocks = get_high_potential_stocks()
    
    # Mostrar en grid
    with st.container():
        st.markdown('<div class="card-grid">', unsafe_allow_html=True)
        
        for stock in potential_stocks:
            realtime_data = get_realtime_prices().get(stock['symbol'], {})
            price = realtime_data.get('price', 'N/A')
            change = realtime_data.get('change', 0)
            
            change_class = "positive" if change >= 0 else "negative"
            change_icon = "▲" if change >= 0 else "▼"
            
            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-header">
                    <div class="stock-ticker">{stock['symbol']}</div>
                    <div class="stock-price">${price if price != 'N/A' else price}</div>
                </div>
                <div class="stock-name" style="color: #94a3b8; margin-bottom: 0.5rem;">{stock['name']}</div>
                <div class="stock-potential positive" style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">
                    Potencial: +{stock['potential']}%
                </div>
                <div class="stock-change {change_class}" style="margin-bottom: 0.5rem;">
                    {change_icon} {abs(change):.2f}% (hoy)
                </div>
                <div style="color: #94a3b8; font-size: 0.9rem;">
                    {stock['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección de noticias financieras
    st.markdown('<div class="section-title">📰 Últimas Noticias Financieras</div>', unsafe_allow_html=True)
    
    # Obtener noticias
    news_items = get_financial_news()
    
    # Mostrar noticias en grid
    with st.container():
        st.markdown('<div class="news-grid">', unsafe_allow_html=True)
        
        for news in news_items:
            # Usar imagen de placeholder si no hay imagen
            image_html = ""
            if news['image']:
                image_html = f'<div class="news-img-container"><img src="{news["image"]}" class="news-img" alt="News image"></div>'
            else:
                image_html = """
                <div class="news-img-container" style="background: linear-gradient(135deg, #2563eb 0%, #1e293b 100%); 
                    display: flex; align-items: center; justify-content: center;">
                    <div style="font-size: 2rem; color: white;">📰</div>
                </div>
                """
            
            st.markdown(f"""
            <a href="{news['link']}" target="_blank" style="text-decoration: none; color: inherit;">
                <div class="news-card">
                    {image_html}
                    <div class="news-content">
                        <div class="news-title">{news['title']}</div>
                        <div class="news-summary">
                            {news['summary'][:150]}{'...' if len(news['summary']) > 150 else ''}
                        </div>
                        <div class="news-footer">
                            <span>{news['published']}</span>
                            <span>Leer más →</span>
                        </div>
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>FinAdvisor Pro • Plataforma de análisis financiero • Datos con propósitos educativos</p>
        <p>© 2023 FinAdvisor Pro. Todos los derechos reservados.</p>
    </div>
    """, unsafe_allow_html=True)

def show_stock_detail(symbol):
    """Muestra la página de detalle para una acción específica"""
    stock_data = load_stock_data()
    stock_info = stock_data[stock_data['symbol'] == symbol]
    
    if stock_info.empty:
        st.error(f"No se encontró información para {symbol}")
        st.session_state.selected_stock = None
        time.sleep(1)
        st.rerun()
        return
    
    stock_name = stock_info.iloc[0]['name']
    realtime_data = get_realtime_prices().get(symbol, {})
    price = realtime_data.get('price', 'N/A')
    change = realtime_data.get('change', 0)
    
    # Botón para volver al inicio
    if st.button("← Volver al inicio"):
        st.session_state.selected_stock = None
        st.rerun()
    
    # Encabezado de la acción
    change_class = "positive" if change >= 0 else "negative"
    change_icon = "▲" if change >= 0 else "▼"
    
    st.markdown(f"""
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin-bottom: 0.5rem;">{stock_name} ({symbol})</h1>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 1.8rem; font-weight: 700;">${price if price != 'N/A' else price}</div>
                    <div class="stock-change {change_class}" style="font-size: 1.2rem; padding: 0.3rem 1rem;">
                        {change_icon} {abs(change):.2f}%
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.1rem; color: #94a3b8;">{stock_info.iloc[0]['sector']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico de TradingView
    st.markdown('<div class="section-title">📊 Gráfico de Trading</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chart-container">
        <!-- TradingView Widget -->
        <div class="tradingview-widget-container">
            <div id="tradingview_{symbol}" style="height: 100%;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget(
                {{
                    "width": "100%",
                    "height": "500",
                    "symbol": "{symbol}",
                    "interval": "D",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "es",
                    "toolbar_bg": "#0f172a",
                    "enable_publishing": false,
                    "hide_top_toolbar": false,
                    "hide_legend": true,
                    "save_image": false,
                    "container_id": "tradingview_{symbol}"
                }}
            );
            </script>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Datos fundamentales
    st.markdown('<div class="section-title">📊 Datos Fundamentales</div>', unsafe_allow_html=True)
    fundamental_data = get_fundamental_data(symbol)
    
    with st.container():
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
        
        stats = [
            {"label": "Capitalización", "value": fundamental_data["market_cap"], "icon": "🏦"},
            {"label": "P/E Ratio", "value": fundamental_data["pe_ratio"], "icon": "📊"},
            {"label": "EPS", "value": fundamental_data["eps"], "icon": "💰"},
            {"label": "Dividendo", "value": f"{fundamental_data['dividend_yield']}%", "icon": "💵"},
            {"label": "Beta", "value": fundamental_data["beta"], "icon": "📉"},
            {"label": "Margen Beneficio", "value": f"{fundamental_data['profit_margin']}%", "icon": "📈"},
            {"label": "Objetivo Analistas", "value": f"${fundamental_data['analyst_target']}", "icon": "🎯"},
            {"label": "Potencial", "value": f"+{((fundamental_data.get('analyst_target', 0) - price)/price*100):.1f}%" if price != 'N/A' and fundamental_data.get('analyst_target', 'N/A') != 'N/A' else "N/A", "icon": "🚀"}
        ]
        
        for stat in stats:
            st.markdown(f"""
            <div class="stat-card">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="font-size: 1.5rem;">{stat['icon']}</div>
                    <div class="stat-label">{stat['label']}</div>
                </div>
                <div class="stat-value">{stat['value']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recomendación de IA
    st.markdown('<div class="section-title">🤖 Recomendación de Inteligencia Artificial</div>', unsafe_allow_html=True)
    
    with st.spinner("Generando análisis de IA..."):
        ai_recommendation = get_ai_recommendation(symbol)
    
    # Determinar clase CSS según la recomendación
    if "COMPRAR" in ai_recommendation["recommendation"]:
        rec_class = "buy"
    elif "VENDER" in ai_recommendation["recommendation"]:
        rec_class = "sell"
    else:
        rec_class = "hold"
    
    # Construir lista de razones
    reasons_html = "\n".join([f"<li>{reason}</li>" for reason in ai_recommendation["reasoning"]])
    
    st.markdown(f"""
    <div class="recommendation-card">
        <div class="recommendation-header">
            <div class="recommendation-icon {rec_class}">{ai_recommendation['icon']}</div>
            <div>
                <div class="recommendation-title {rec_class}">{ai_recommendation['recommendation']}</div>
                <div style="color: #94a3b8;">Confianza: {ai_recommendation['confidence']} | Objetivo: ${ai_recommendation['price_target']:.2f} (+{ai_recommendation['upside']}%)</div>
            </div>
        </div>
        
        <div class="recommendation-content">
            <p><strong>Análisis Fundamentado:</strong></p>
            <ul>
                {reasons_html}
            </ul>
            
            <p><strong>Estrategia Recomendada:</strong></p>
            <p>{ai_recommendation['strategy']}</p>
            
            <p><strong>Horizonte Temporal:</strong> {ai_recommendation['time_frame']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Noticias relacionadas
    st.markdown('<div class="section-title">📰 Noticias Relacionadas</div>', unsafe_allow_html=True)
    
    # Filtrar noticias por el símbolo de la acción
    all_news = get_financial_news()
    related_news = [news for news in all_news if symbol.lower() in news['title'].lower() or symbol.lower() in news['summary'].lower()][:4]
    
    if not related_news:
        st.info("No hay noticias recientes específicas para esta acción")
    else:
        with st.container():
            st.markdown('<div class="news-grid">', unsafe_allow_html=True)
            
            for news in related_news:
                # Usar imagen de placeholder si no hay imagen
                image_html = ""
                if news['image']:
                    image_html = f'<div class="news-img-container"><img src="{news["image"]}" class="news-img" alt="News image"></div>'
                else:
                    image_html = """
                    <div class="news-img-container" style="background: linear-gradient(135deg, #2563eb 0%, #1e293b 100%); 
                        display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 2rem; color: white;">📰</div>
                    </div>
                    """
                
                st.markdown(f"""
                <a href="{news['link']}" target="_blank" style="text-decoration: none; color: inherit;">
                    <div class="news-card">
                        {image_html}
                        <div class="news-content">
                            <div class="news-title">{news['title']}</div>
                            <div class="news-footer">
                                <span>{news['published']}</span>
                                <span>Leer más →</span>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>FinAdvisor Pro • Análisis de {symbol} • Datos con propósitos educativos</p>
        <p>© 2023 FinAdvisor Pro. Todos los derechos reservados.</p>
    </div>
    """, unsafe_allow_html=True)

# =======================
# EJECUCIÓN PRINCIPAL
# =======================
if __name__ == "__main__":
    main()
