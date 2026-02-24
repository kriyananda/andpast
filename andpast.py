import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import time

# ── CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="andpast - Debit Spread Advisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    :root {
        --bg-base:    #111214;
        --bg-card:    #1c1e21;
        --bg-hover:   #26282c;
        --border:     #2e3035;
        --text-main:  #e0e2e5;
        --text-muted: #7a7e87;
        --pos:        #4caf82;
        --neg:        #c05f5f;
        --hi:         #9aa3b0;
    }

    .main { background-color: var(--bg-base); }

    .app-header {
        background: var(--bg-card);
        border-bottom: 1px solid var(--border);
        padding: 1.2rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
    }
    .app-title { font-size: 2rem; font-weight: 700; color: var(--text-main); letter-spacing: -0.5px; }
    .app-subtitle { color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem; }

    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.1rem 1.4rem;
        text-align: center;
    }
    .metric-label { color: var(--text-muted); font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { color: var(--text-main); font-size: 1.7rem; font-weight: 700; margin-top: 0.3rem; }
    .metric-value.green  { color: var(--pos); }
    .metric-value.red    { color: var(--neg); }
    .metric-value.yellow { color: var(--hi); }

    .order-buy {
        background: rgba(76,175,130,0.07);
        border-left: 3px solid var(--pos);
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 1rem; margin: 0.4rem 0;
        color: var(--pos); font-weight: 600;
    }
    .order-sell {
        background: rgba(192,95,95,0.07);
        border-left: 3px solid var(--neg);
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 1rem; margin: 0.4rem 0;
        color: var(--neg); font-weight: 600;
    }

    .alert-box {
        background: rgba(154,163,176,0.07);
        border: 1px solid var(--hi);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        color: var(--hi);
        font-size: 0.9rem; margin: 0.5rem 0;
    }

    .history-row {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.8rem 1.2rem; margin: 0.4rem 0;
    }

    .ib-connected {
        background: rgba(76,175,130,0.1);
        border: 1px solid var(--pos);
        color: var(--pos);
        padding: 0.3rem 0.8rem; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600;
    }
    .ib-disconnected {
        background: rgba(192,95,95,0.1);
        border: 1px solid var(--neg);
        color: var(--neg);
        padding: 0.3rem 0.8rem; border-radius: 20px;
        font-size: 0.8rem; font-weight: 600;
    }

    .stTabs [data-baseweb="tab-list"] { background: var(--bg-card); border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: var(--text-muted); border-radius: 8px; }
    .stTabs [aria-selected="true"] { background: var(--bg-hover) !important; color: var(--text-main) !important; }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] { background: #18191c; border-right: 1px solid #3a3d44; }

    /* Labels sidebar — molto più leggibili */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stTextArea label,
    [data-testid="stSidebar"] p {
        color: #d0d3d8 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
    }

    /* Titoli sezione sidebar */
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
        margin-top: 1rem;
    }

    /* Input fields sidebar */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        background: #26282c !important;
        color: #e8eaed !important;
        border: 1px solid #44474e !important;
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }

    /* Radio buttons */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #c8ccd2 !important;
        font-size: 0.87rem !important;
    }

    /* Slider track e valore */
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {
        color: #8a8d94 !important;
    }

    /* Caption / help text */
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] .stCaption {
        color: #7a7e87 !important;
    }

    /* Separatore */
    [data-testid="stSidebar"] hr {
        border-color: #3a3d44 !important;
        margin: 0.8rem 0;
    }

    .stButton > button {
        background: var(--bg-hover);
        color: var(--text-main);
        border: 1px solid var(--border);
        border-radius: 8px; font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: var(--hi);
        color: var(--text-main);
        background: #2e3035;
    }

    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-main) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── STORAGE FILE ─────────────────────────────────────────────────
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trade_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def add_trade(trade):
    history = load_history()
    trade['id'] = int(time.time())
    trade['data_apertura'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    trade['stato'] = 'Aperto'
    trade['pnl_corrente'] = 0.0
    history.insert(0, trade)
    save_history(history)

# ── BLACK-SCHOLES + GREEKS ───────────────────────────────────────
def black_scholes(S, K, T, r, sigma, option_type='call'):
    if T <= 0:
        return max(S - K, 0) if option_type == 'call' else max(K - S, 0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return float(S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2))
    else:
        return float(K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1))

def greeks(S, K, T, r, sigma, option_type='call'):
    if T <= 0:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    delta = norm.cdf(d1) if option_type == 'call' else -norm.cdf(-d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
             - r * K * np.exp(-r * T) * (norm.cdf(d2) if option_type == 'call' else norm.cdf(-d2))) / 365
    vega  = S * norm.pdf(d1) * np.sqrt(T) / 100
    return {'delta': round(delta, 3), 'gamma': round(gamma, 4),
            'theta': round(theta, 4), 'vega': round(vega, 4)}

def get_hv(ticker, period='3mo'):
    data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    if data.empty:
        return None
    returns = np.log(data['Close'] / data['Close'].shift(1)).dropna()
    return float(returns.std().iloc[0] * np.sqrt(252)) if hasattr(returns.std(), 'iloc') else float(returns.std() * np.sqrt(252))

# ── INTERACTIVE BROKERS CONNECTION ───────────────────────────────
def try_ib_connect(host, port, client_id):
    """Tenta connessione a IB TWS/Gateway. Restituisce (connected, ib_object, message)"""
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        import threading

        class IBApp(EWrapper, EClient):
            def __init__(self):
                EClient.__init__(self, self)
                self.connected = False
                self.next_order_id = None

            def nextValidId(self, orderId):
                self.connected = True
                self.next_order_id = orderId

            def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
                if errorCode not in [2104, 2106, 2158]:  # warning codes normali
                    st.session_state['ib_error'] = f"IB Error {errorCode}: {errorString}"

        app = IBApp()
        app.connect(host, port, client_id)
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        time.sleep(2)
        if app.connected:
            return True, app, "✅ Connesso a Interactive Brokers"
        else:
            return False, None, "❌ Connessione fallita. Verifica che TWS o IB Gateway sia aperto."
    except ImportError:
        return False, None, "⚠️ ibapi non installata. Esegui: pip install ibapi"
    except Exception as e:
        return False, None, f"❌ Errore: {str(e)}"

def get_ib_option_price(ib_app, ticker, strike, expiry, right):
    """Ottiene prezzo reale opzione da IB (richiede connessione attiva)"""
    try:
        from ibapi.contract import Contract
        contract = Contract()
        contract.symbol = ticker
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.strike = strike
        contract.right = right  # 'C' o 'P'
        contract.lastTradeDateOrContractMonth = expiry
        contract.multiplier = "100"
        return contract
    except:
        return None

# ── SCANSIONE TITOLI ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def scan_candidates(tickers, min_vol=0.18, max_vol=0.85):
    candidates = []
    for t in tickers:
        try:
            ticker_obj = yf.Ticker(t)
            info = ticker_obj.fast_info
            price = info.last_price
            if price is None or price < 5:
                continue
            hv = get_hv(t)
            if hv is None or not (min_vol <= hv <= max_vol):
                continue
            hist = yf.download(t, period='3mo', progress=False, auto_adjust=True)
            if hist.empty or len(hist) < 20:
                continue
            close = hist['Close'].squeeze()
            ret_1m = float((close.iloc[-1] - close.iloc[-21]) / close.iloc[-21])
            ret_1w = float((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5])
            # RSI semplice
            delta_c = close.diff()
            gain = delta_c.where(delta_c > 0, 0).rolling(14).mean()
            loss = (-delta_c.where(delta_c < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = float(100 - (100 / (1 + rs.iloc[-1])))
            # Trend
            ma20 = float(close.rolling(20).mean().iloc[-1])
            above_ma = float(close.iloc[-1]) > ma20
            score = 0
            direction = 'call'
            if ret_1m > 0.03 and ret_1w > 0: score += 2
            if ret_1m < -0.03 and ret_1w < 0: score -= 2; direction = 'put'
            if above_ma: score += 1
            else: score -= 1; direction = 'put'
            if rsi > 55: score += 1
            if rsi < 45: score -= 1; direction = 'put'
            if score >= 0: direction = 'call'
            candidates.append({
                'Ticker': t,
                'Prezzo': round(float(price), 2),
                'HV (%)': round(hv * 100, 1),
                'RSI': round(rsi, 1),
                'Trend 1M (%)': round(ret_1m * 100, 2),
                'Trend 1W (%)': round(ret_1w * 100, 2),
                'Score': score,
                'Direzione': direction,
                'hv_raw': hv,
                'price_raw': float(price)
            })
        except Exception:
            continue
    return sorted(candidates, key=lambda x: abs(x['Score']), reverse=True)

# ── COSTRUISCI STRATEGIA ─────────────────────────────────────────
def build_spread(ticker, price, hv, direction, max_loss, take_profit_pct, dte, r=0.05, width_pct=0.05):
    T = dte / 365
    step = 1 if price < 50 else (2.5 if price < 100 else 5)

    if direction == 'call':
        K_long  = round(price / step) * step
        K_short = round((price * (1 + width_pct)) / step) * step
        if K_short <= K_long:
            K_short = K_long + step
        pl = black_scholes(price, K_long,  T, r, hv, 'call')
        ps = black_scholes(price, K_short, T, r, hv, 'call')
        gl = greeks(price, K_long,  T, r, hv, 'call')
        gs = greeks(price, K_short, T, r, hv, 'call')
        net_debit   = (pl - ps) * 100
        max_profit  = (K_short - K_long) * 100 - net_debit
        strat_name  = 'Bull Call Spread'
        buy_label   = f"CALL {K_long}"
        sell_label  = f"CALL {K_short}"
    else:
        K_long  = round(price / step) * step
        K_short = round((price * (1 - width_pct)) / step) * step
        if K_short >= K_long:
            K_short = K_long - step
        pl = black_scholes(price, K_long,  T, r, hv, 'put')
        ps = black_scholes(price, K_short, T, r, hv, 'put')
        gl = greeks(price, K_long,  T, r, hv, 'put')
        gs = greeks(price, K_short, T, r, hv, 'put')
        net_debit   = (pl - ps) * 100
        max_profit  = (K_long - K_short) * 100 - net_debit
        strat_name  = 'Bear Put Spread'
        buy_label   = f"PUT {K_long}"
        sell_label  = f"PUT {K_short}"

    if net_debit <= 0:
        net_debit = 0.01
    contracts = max(1, int(max_loss / net_debit))
    net_debit_tot  = net_debit * contracts
    max_profit_tot = max_profit * contracts
    tp_value = net_debit_tot + (take_profit_pct / 100) * max_profit_tot
    breakeven = K_long + net_debit / 100 if direction == 'call' else K_long - net_debit / 100
    net_delta = (gl['delta'] - gs['delta']) * contracts * 100
    net_theta = (gl['theta'] - gs['theta']) * contracts * 100
    net_vega  = (gl['vega']  - gs['vega'])  * contracts * 100

    return {
        'ticker': ticker, 'strategia': strat_name, 'direzione': direction,
        'buy_label': buy_label, 'sell_label': sell_label,
        'K_long': K_long, 'K_short': K_short,
        'premio_buy': round(pl, 2), 'premio_sell': round(ps, 2),
        'net_debit': round(net_debit, 2),
        'contratti': contracts,
        'ingresso_totale': round(net_debit_tot, 2),
        'max_loss': round(net_debit_tot, 2),
        'max_profit': round(max_profit_tot, 2),
        'tp_target': round(tp_value, 2),
        'tp_pct': take_profit_pct,
        'breakeven': round(breakeven, 2),
        'dte': dte, 'price': price, 'hv': hv, 'T': T,
        'delta': round(net_delta, 2),
        'theta': round(net_theta, 4),
        'vega': round(net_vega, 4),
        'rr_ratio': round(max_profit_tot / net_debit_tot, 2) if net_debit_tot > 0 else 0
    }

# ── GRAFICO P&L ──────────────────────────────────────────────────
def plot_pnl(s, height=480):
    prices = np.linspace(s['price'] * 0.75, s['price'] * 1.25, 400)
    K_long, K_short = s['K_long'], s['K_short']
    nd = s['net_debit'] / 100
    c  = s['contratti']

    if s['direzione'] == 'call':
        pnl = np.where(prices <= K_long, -nd,
              np.where(prices >= K_short, (K_short - K_long) - nd,
              prices - K_long - nd)) * c * 100
    else:
        pnl = np.where(prices >= K_long, -nd,
              np.where(prices <= K_short, (K_long - K_short) - nd,
              K_long - prices - nd)) * c * 100

    # Zona profitto / perdita
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.concatenate([prices, prices[::-1]]),
        y=np.concatenate([np.where(pnl > 0, pnl, 0), np.zeros(len(prices))]),
        fill='toself', fillcolor='rgba(0,212,160,0.12)',
        line=dict(width=0), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=np.concatenate([prices, prices[::-1]]),
        y=np.concatenate([np.where(pnl < 0, pnl, 0), np.zeros(len(prices))]),
        fill='toself', fillcolor='rgba(255,77,109,0.12)',
        line=dict(width=0), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=prices, y=pnl, mode='lines',
        line=dict(color='#64ffda', width=2.5),
        name='P&L a scadenza',
        hovertemplate='Prezzo: $%{x:.2f}<br>P&L: $%{y:.0f}<extra></extra>'
    ))

    # Linee verticali chiave
    fig.add_vline(x=s['price'],    line_dash='dash', line_color='#ffd166', line_width=1.5,
                  annotation=dict(text=f"Attuale<br>${s['price']}", font_color='#ffd166', bgcolor='#1a1f35'))
    fig.add_vline(x=s['breakeven'], line_dash='dot', line_color='#ffffff', line_width=1,
                  annotation=dict(text=f"Breakeven<br>${s['breakeven']}", font_color='#ffffff', bgcolor='#1a1f35'))
    fig.add_hline(y=0, line_color='rgba(255,255,255,0.2)', line_width=1)
    fig.add_hline(y=s['max_profit'] * (s['tp_pct'] / 100),
                  line_dash='dash', line_color='#00d4a0', line_width=1,
                  annotation=dict(text=f"Take Profit ({s['tp_pct']}%)", font_color='#00d4a0'))
    fig.add_hline(y=-s['max_loss'],
                  line_dash='dash', line_color='#ff4d6d', line_width=1,
                  annotation=dict(text=f"Max Loss", font_color='#ff4d6d'))

    fig.update_layout(
        height=height,
        paper_bgcolor='#0f1117', plot_bgcolor='#0f1117',
        font=dict(family='Inter', color='#ccd6f6'),
        xaxis=dict(title='Prezzo sottostante ($)', gridcolor='#2d3561', showgrid=True, zeroline=False),
        yaxis=dict(title='P&L ($)', gridcolor='#2d3561', showgrid=True, zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', font_color='#ccd6f6'),
        margin=dict(l=60, r=40, t=30, b=60)
    )
    return fig

# ── GRAFICO PREZZO STORICO ───────────────────────────────────────
@st.cache_data(ttl=300)
def plot_price_history(ticker):
    hist = yf.download(ticker, period='3mo', progress=False, auto_adjust=True)
    if hist.empty:
        return None
    close = hist['Close'].squeeze()
    ma20  = close.rolling(20).mean()
    ma50  = close.rolling(50).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=close, mode='lines',
                             line=dict(color='#64ffda', width=2), name='Prezzo'))
    fig.add_trace(go.Scatter(x=hist.index, y=ma20, mode='lines',
                             line=dict(color='#ffd166', width=1.2, dash='dash'), name='MA20'))
    fig.add_trace(go.Scatter(x=hist.index, y=ma50, mode='lines',
                             line=dict(color='#ff4d6d', width=1.2, dash='dot'), name='MA50'))
    fig.update_layout(
        height=250, paper_bgcolor='#0f1117', plot_bgcolor='#0f1117',
        font=dict(family='Inter', color='#ccd6f6'),
        xaxis=dict(gridcolor='#2d3561', showgrid=True),
        yaxis=dict(gridcolor='#2d3561', showgrid=True),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=50, r=20, t=20, b=40)
    )
    return fig

# ── SESSION STATE ────────────────────────────────────────────────
if 'ib_connected' not in st.session_state:
    st.session_state['ib_connected'] = False
if 'ib_app' not in st.session_state:
    st.session_state['ib_app'] = None
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = []
if 'strategies' not in st.session_state:
    st.session_state['strategies'] = {}

# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <div class="app-title">andpast</div>
    <div class="app-subtitle">Debit Spread Advisor — Dati in tempo reale · Interactive Brokers</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Parametri Strategia")
    max_loss    = st.number_input("Max Loss ($)", 50, 10000, 500, 50)
    tp_pct      = st.number_input("Take Profit (%)", 10, 100, 50, 5,
                                   help="% del max profit a cui chiudi la posizione")
    dte         = st.slider("DTE (giorni a scadenza)", 7, 60, 21)
    width_pct   = st.slider("Ampiezza spread (%)", 3, 15, 5,
                             help="Distanza % tra i due strike") / 100
    direction   = st.radio("Direzione", ['Auto (basata su trend)', 'Solo Rialzista', 'Solo Ribassista'])

    st.markdown("---")
    st.markdown("### 📋 Lista Titoli")
    default_tickers = "AAPL,MSFT,NVDA,TSLA,AMZN,META,GOOGL,AMD,SPY,QQQ,NFLX,COIN,MSTR"
    custom = st.text_area("Ticker (separati da virgola)", default_tickers, height=100)
    scan_btn = st.button("🔍 Scansiona Mercato", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔌 Interactive Brokers")
    st.caption("⚠️ La connessione IB funziona solo in locale (Mac). Su cloud usa solo lo scanner.")
    ib_host = st.text_input("Host", "127.0.0.1")
    ib_port = st.number_input("Porta", value=7497, help="7497 = TWS Paper, 7496 = TWS Live, 4002 = Gateway Paper, 4001 = Gateway Live")
    ib_cid  = st.number_input("Client ID", value=1)

    col_ib1, col_ib2 = st.columns(2)
    with col_ib1:
        if st.button("Connetti", use_container_width=True):
            with st.spinner("Connessione..."):
                ok, app, msg = try_ib_connect(ib_host, int(ib_port), int(ib_cid))
                st.session_state['ib_connected'] = ok
                st.session_state['ib_app'] = app
                st.toast(msg)
    with col_ib2:
        if st.button("Disconnetti", use_container_width=True):
            if st.session_state.get('ib_app'):
                try:
                    st.session_state['ib_app'].disconnect()
                except:
                    pass
            st.session_state['ib_connected'] = False
            st.session_state['ib_app'] = None

    if st.session_state['ib_connected']:
        st.markdown('<span class="ib-connected">● CONNESSO</span>', unsafe_allow_html=True)
        st.caption(f"TWS @ {ib_host}:{ib_port}")
    else:
        st.markdown('<span class="ib-disconnected">● NON CONNESSO</span>', unsafe_allow_html=True)
        st.caption("Apri TWS o IB Gateway prima di connetterti")

# ════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📊 Scanner & Strategie", "📈 Dashboard Portfolio", "📋 Storico Operazioni"])

# ────────────────────────────────────────────────────────────────
# TAB 1: SCANNER
# ────────────────────────────────────────────────────────────────
with tab1:
    if scan_btn:
        tickers = [t.strip().upper() for t in custom.split(',') if t.strip()]
        with st.spinner(f"Analisi di {len(tickers)} titoli in corso..."):
            results = scan_candidates(tuple(tickers))
            st.session_state['scan_results'] = results
            st.session_state['strategies'] = {}
            for r in results:
                dir_code = r.get('direzione', 'call')
                if direction == 'Solo Rialzista':
                    dir_code = 'call'
                elif direction == 'Solo Ribassista':
                    dir_code = 'put'
                ticker_key = r.get('Ticker', '')
                price_val  = r.get('price_raw', r.get('Prezzo', 100))
                hv_val     = r.get('hv_raw', r.get('HV (%)', 30) / 100)
                if not ticker_key:
                    continue
                try:
                    s = build_spread(ticker_key, price_val, hv_val,
                                     dir_code, max_loss, tp_pct, dte, width_pct=width_pct)
                    st.session_state['strategies'][ticker_key] = s
                except Exception as e:
                    st.warning(f"Errore su {ticker_key}: {e}")
                    continue

    results = st.session_state.get('scan_results', [])
    strategies = st.session_state.get('strategies', {})

    if not results:
        st.markdown("""
        <div style="text-align:center; padding: 4rem; color: #8892b0;">
            <div style="font-size:3rem;">🔍</div>
            <div style="font-size:1.1rem; margin-top:1rem;">Imposta i parametri nella sidebar e clicca <b>Scansiona Mercato</b></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary bar
        n_call = sum(1 for r in results if r.get('direzione') == 'call')
        n_put  = len(results) - n_call
        avg_hv = np.mean([r['HV (%)'] for r in results])
        best   = results[0]['Ticker'] if results else '-'

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Candidati trovati</div><div class="metric-value">{len(results)}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Rialzisti / Ribassisti</div><div class="metric-value yellow">{n_call} / {n_put}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">HV media</div><div class="metric-value">{avg_hv:.1f}%</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Miglior candidato</div><div class="metric-value green">{best}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Lista strategie
        for r in results:
            t  = r['Ticker']
            s  = strategies.get(t)
            if not s:
                continue

            dir_emoji = "📈" if s['direzione'] == 'call' else "📉"
            rr_color  = "green" if s['rr_ratio'] >= 1.5 else ("yellow" if s['rr_ratio'] >= 1 else "red")

            with st.expander(f"{dir_emoji}  **{t}**  —  {s['strategia']}  |  Max Loss: ${s['max_loss']}  |  Max Profit: ${s['max_profit']}  |  R/R: {s['rr_ratio']}x", expanded=False):

                col_left, col_right = st.columns([1, 1.8])

                with col_left:
                    st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #2e3035;border-radius:10px;padding:1rem 1.2rem;margin-bottom:0.8rem;">
  <div style="font-size:1.2rem;font-weight:700;color:#e0e2e5;">{t} <span style="font-size:0.85rem;color:#7a7e87;font-weight:400;">{s['strategia']}</span></div>
  <div style="margin-top:0.5rem;font-size:0.85rem;color:#7a7e87;">
    Prezzo <b style="color:#e0e2e5">${s['price']}</b> &nbsp;|&nbsp;
    HV <b style="color:#e0e2e5">{r['HV (%)']}%</b> &nbsp;|&nbsp;
    RSI <b style="color:#e0e2e5">{r['RSI']}</b> &nbsp;|&nbsp;
    1M <b style="color:#e0e2e5">{r['Trend 1M (%)']}%</b>
  </div>
</div>
""", unsafe_allow_html=True)

                    st.markdown(f'<div class="order-buy">▲ &nbsp;COMPRA &nbsp;{s["buy_label"]} &nbsp;@ &nbsp;${s["premio_buy"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="order-sell">▼ &nbsp;VENDI &nbsp;&nbsp;{s["sell_label"]} &nbsp;@ &nbsp;${s["premio_sell"]}</div>', unsafe_allow_html=True)

                    st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #2e3035;border-radius:10px;padding:1rem 1.2rem;margin-top:0.8rem;">
  <table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
    <tr><td style="color:#7a7e87;padding:0.3rem 0;">Contratti</td><td style="color:#e0e2e5;font-weight:600;text-align:right;">{s['contratti']}</td></tr>
    <tr style="border-top:1px solid #2e3035;"><td style="color:#7a7e87;padding:0.3rem 0;">Ingresso totale</td><td style="color:#e0e2e5;font-weight:600;text-align:right;">${s['ingresso_totale']}</td></tr>
    <tr style="border-top:1px solid #2e3035;"><td style="color:#7a7e87;padding:0.3rem 0;">Max Loss</td><td style="color:#c05f5f;font-weight:700;text-align:right;">${s['max_loss']}</td></tr>
    <tr style="border-top:1px solid #2e3035;"><td style="color:#7a7e87;padding:0.3rem 0;">Max Profit</td><td style="color:#4caf82;font-weight:700;text-align:right;">${s['max_profit']}</td></tr>
    <tr style="border-top:1px solid #2e3035;"><td style="color:#7a7e87;padding:0.3rem 0;">Breakeven</td><td style="color:#e0e2e5;font-weight:600;text-align:right;">${s['breakeven']}</td></tr>
    <tr style="border-top:1px solid #2e3035;"><td style="color:#7a7e87;padding:0.3rem 0;">R/R ratio</td><td style="color:#e0e2e5;font-weight:600;text-align:right;">{s['rr_ratio']}x</td></tr>
    <tr style="border-top:1px solid #2e3035;"><td style="color:#7a7e87;padding:0.3rem 0;">Scadenza</td><td style="color:#e0e2e5;font-weight:600;text-align:right;">{s['dte']} giorni</td></tr>
  </table>
</div>
""", unsafe_allow_html=True)

                    st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #4caf82;border-radius:10px;padding:0.85rem 1.2rem;margin-top:0.8rem;">
  <div style="color:#7a7e87;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;">Target uscita ({tp_pct}% del max profit)</div>
  <div style="color:#4caf82;font-size:1.35rem;font-weight:700;margin-top:0.2rem;">${s['tp_target']}</div>
  <div style="color:#7a7e87;font-size:0.8rem;margin-top:0.15rem;">valore premio spread alla chiusura</div>
</div>
""", unsafe_allow_html=True)

                    st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #2e3035;border-radius:10px;padding:0.85rem 1.2rem;margin-top:0.8rem;">
  <div style="color:#7a7e87;font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">Greeks netti</div>
  <div style="display:flex;gap:0;">
    <div style="flex:1;text-align:center;"><div style="color:#7a7e87;font-size:0.75rem;">Delta</div><div style="color:#e0e2e5;font-size:1.05rem;font-weight:700;">{s['delta']}</div></div>
    <div style="flex:1;text-align:center;border-left:1px solid #2e3035;"><div style="color:#7a7e87;font-size:0.75rem;">Theta/gg</div><div style="color:#e0e2e5;font-size:1.05rem;font-weight:700;">{s['theta']}</div></div>
    <div style="flex:1;text-align:center;border-left:1px solid #2e3035;"><div style="color:#7a7e87;font-size:0.75rem;">Vega</div><div style="color:#e0e2e5;font-size:1.05rem;font-weight:700;">{s['vega']}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"➕ Aggiungi a storico", key=f"add_{t}"):
                        add_trade({
                            'ticker': t, 'strategia': s['strategia'],
                            'buy': s['buy_label'], 'sell': s['sell_label'],
                            'contratti': s['contratti'],
                            'ingresso': s['ingresso_totale'],
                            'max_loss': s['max_loss'], 'max_profit': s['max_profit'],
                            'tp_target': s['tp_target'], 'dte': s['dte'],
                            'breakeven': s['breakeven']
                        })
                        st.success("Trade aggiunto allo storico!")

                with col_right:
                    st.plotly_chart(plot_pnl(s, height=420), use_container_width=True)
                    price_fig = plot_price_history(t)
                    if price_fig:
                        st.plotly_chart(price_fig, use_container_width=True)

# ────────────────────────────────────────────────────────────────
# TAB 2: DASHBOARD
# ────────────────────────────────────────────────────────────────
with tab2:
    history = load_history()
    open_trades = [h for h in history if h.get('stato') == 'Aperto']
    closed_trades = [h for h in history if h.get('stato') == 'Chiuso']

    st.markdown("### 📈 Dashboard Portfolio")

    if not history:
        st.info("Nessuna operazione registrata. Scansiona il mercato e aggiungi trade dallo scanner.")
    else:
        total_rischio = sum(t['max_loss'] for t in open_trades)
        total_profit_potenziale = sum(t['max_profit'] for t in open_trades)
        total_pnl_chiusi = sum(t.get('pnl_finale', 0) for t in closed_trades)

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Trade aperti</div><div class="metric-value">{len(open_trades)}</div></div>', unsafe_allow_html=True)
        with d2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Rischio totale</div><div class="metric-value red">${total_rischio:.0f}</div></div>', unsafe_allow_html=True)
        with d3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Profit potenziale</div><div class="metric-value green">${total_profit_potenziale:.0f}</div></div>', unsafe_allow_html=True)
        with d4:
            pnl_color = "green" if total_pnl_chiusi >= 0 else "red"
            st.markdown(f'<div class="metric-card"><div class="metric-label">P&L realizzato</div><div class="metric-value {pnl_color}">${total_pnl_chiusi:.0f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Alert take profit
        if open_trades:
            st.markdown("### 🔔 Alert Take Profit")
            for trade in open_trades:
                t_tick = trade.get('ticker', '')
                try:
                    current_price = yf.Ticker(t_tick).fast_info.last_price
                    if current_price:
                        breakeven = trade.get('breakeven', 0)
                        tp_target = trade.get('tp_target', 0)
                        if 'Call' in trade.get('strategia', ''):
                            progress = max(0, (current_price - breakeven) / (tp_target - breakeven + 0.01)) if tp_target != breakeven else 0
                        else:
                            progress = max(0, (breakeven - current_price) / (breakeven - tp_target + 0.01)) if tp_target != breakeven else 0
                        progress = min(progress, 1.0)
                        color = "#00d4a0" if progress >= 0.8 else ("#ffd166" if progress >= 0.4 else "#ff4d6d")
                        alert_icon = "🚨" if progress >= 0.9 else ("⚡" if progress >= 0.5 else "•")
                        st.markdown(f"""
                        <div style="background:#1a1f35; border:1px solid #2d3561; border-radius:10px; padding:1rem; margin:0.5rem 0;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                                <span style="color:#ccd6f6; font-weight:600;">{alert_icon} {t_tick} — {trade.get('strategia','')}</span>
                                <span style="color:{color}; font-weight:700;">{progress*100:.0f}% del target</span>
                            </div>
                            <div style="background:#0f1117; border-radius:4px; height:8px;">
                                <div style="background:{color}; width:{progress*100:.0f}%; height:8px; border-radius:4px; transition:width 0.3s;"></div>
                            </div>
                            <div style="color:#8892b0; font-size:0.8rem; margin-top:0.4rem;">
                                Prezzo: ${current_price:.2f} | Target spread: ${tp_target:.2f} | Breakeven: ${breakeven:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                except:
                    st.caption(f"• {t_tick} — impossibile recuperare prezzo attuale")

        if st.session_state['ib_connected']:
            st.success("✅ Connesso a IB — I prezzi delle opzioni sono recuperati in tempo reale dal tuo account.")
        else:
            st.warning("⚠️ Non connesso a IB — Connettiti dalla sidebar per vedere i prezzi reali delle opzioni e il P&L live.")

# ────────────────────────────────────────────────────────────────
# TAB 3: STORICO
# ────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📋 Storico Operazioni")
    history = load_history()

    if not history:
        st.info("Nessuna operazione registrata ancora.")
    else:
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            filter_stato = st.selectbox("Filtra per stato", ["Tutti", "Aperto", "Chiuso"])
        with col_f2:
            if st.button("🗑️ Cancella tutto lo storico"):
                save_history([])
                st.rerun()

        filtered = history if filter_stato == "Tutti" else [h for h in history if h.get('stato') == filter_stato]

        for trade in filtered:
            stato_color = "#00d4a0" if trade.get('stato') == 'Chiuso' else "#ffd166"
            pnl = trade.get('pnl_finale', None)
            pnl_str = f"P&L: ${pnl:.0f}" if pnl is not None else ""

            with st.expander(f"**{trade.get('ticker','')}** — {trade.get('strategia','')} | {trade.get('data_apertura','')} | Stato: {trade.get('stato','')}", expanded=False):
                e1, e2 = st.columns(2)
                with e1:
                    st.markdown(f"**🟢 COMPRA:** {trade.get('buy','')}")
                    st.markdown(f"**🔴 VENDI:** {trade.get('sell','')}")
                    st.markdown(f"**Contratti:** {trade.get('contratti','')}")
                    st.markdown(f"**Ingresso totale:** ${trade.get('ingresso','')}")
                with e2:
                    st.markdown(f"**Max Loss:** ${trade.get('max_loss','')}")
                    st.markdown(f"**Max Profit:** ${trade.get('max_profit','')}")
                    st.markdown(f"**Take Profit Target:** ${trade.get('tp_target','')}")
                    st.markdown(f"**Breakeven:** ${trade.get('breakeven','')}")

                st.markdown("---")
                col_close1, col_close2, col_close3 = st.columns(3)
                with col_close1:
                    pnl_input = st.number_input("P&L finale ($)", value=0.0, key=f"pnl_{trade['id']}")
                with col_close2:
                    if st.button("✅ Chiudi operazione", key=f"close_{trade['id']}"):
                        for h in history:
                            if h['id'] == trade['id']:
                                h['stato'] = 'Chiuso'
                                h['data_chiusura'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                                h['pnl_finale'] = pnl_input
                        save_history(history)
                        st.rerun()
                with col_close3:
                    if st.button("🗑️ Elimina", key=f"del_{trade['id']}"):
                        history = [h for h in history if h['id'] != trade['id']]
                        save_history(history)
                        st.rerun()

st.markdown("---")
st.caption("⚠️ andpast è uno strumento educativo e informativo. Non costituisce consulenza finanziaria. Il trading di opzioni comporta rischi significativi di perdita del capitale.")
