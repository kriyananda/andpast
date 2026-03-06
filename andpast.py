import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime
import plotly.graph_objects as go
import json, os, time

# ── CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="andpast",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    :root {
        --bg:      #111214;
        --card:    #1c1e21;
        --hover:   #26282c;
        --bdr:     #2e3035;
        --txt:     #e0e2e5;
        --muted:   #7a7e87;
        --pos:     #4caf82;
        --neg:     #c05f5f;
        --hi:      #9aa3b0;
    }

    .main { background: var(--bg); }

    .app-header {
        background: var(--card);
        border-bottom: 1px solid var(--bdr);
        padding: 1rem 1.5rem;
        margin: -1rem -1rem 1.5rem -1rem;
    }
    .app-title   { font-size:1.8rem; font-weight:700; color:var(--txt); }
    .app-sub     { color:var(--muted); font-size:0.85rem; margin-top:0.2rem; }

    .kv-box {
        background: var(--card);
        border: 1px solid var(--bdr);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
    }
    .kv-box table { width:100%; border-collapse:collapse; font-size:0.88rem; }
    .kv-box td    { padding:0.28rem 0; }
    .kv-box tr    { border-top: 1px solid var(--bdr); }
    .kv-box tr:first-child { border-top: none; }
    .kv-label { color:var(--muted); }
    .kv-val   { color:var(--txt); font-weight:600; text-align:right; }
    .kv-pos   { color:var(--pos); font-weight:700; text-align:right; }
    .kv-neg   { color:var(--neg); font-weight:700; text-align:right; }

    .order-buy  { background:rgba(76,175,130,.08); border-left:3px solid var(--pos);
                  border-radius:0 8px 8px 0; padding:.55rem 1rem; margin:.35rem 0;
                  color:var(--pos); font-weight:600; font-size:.9rem; }
    .order-sell { background:rgba(192,95,95,.08); border-left:3px solid var(--neg);
                  border-radius:0 8px 8px 0; padding:.55rem 1rem; margin:.35rem 0;
                  color:var(--neg); font-weight:600; font-size:.9rem; }

    .tp-box {
        background: rgba(76,175,130,.06);
        border: 1px solid var(--pos);
        border-radius:10px; padding:.8rem 1.2rem; margin:.7rem 0;
    }
    .tp-label { color:var(--muted); font-size:.72rem; text-transform:uppercase; letter-spacing:1px; }
    .tp-val   { color:var(--pos); font-size:1.3rem; font-weight:700; margin-top:.15rem; }
    .tp-sub   { color:var(--muted); font-size:.78rem; margin-top:.1rem; }

    .r-badge {
        display:inline-block; background:var(--hover);
        border:1px solid var(--bdr); border-radius:6px;
        padding:.2rem .6rem; font-size:.78rem; color:var(--hi);
        margin-left:.4rem; vertical-align:middle;
    }

    .greek-box {
        background: var(--card); border:1px solid var(--bdr);
        border-radius:10px; padding:.8rem 1rem; margin:.7rem 0;
    }
    .greek-title { color:var(--muted); font-size:.72rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:.5rem; }
    .greek-grid  { display:flex; gap:0; }
    .greek-item  { flex:1; text-align:center; }
    .greek-item + .greek-item { border-left:1px solid var(--bdr); }
    .greek-lbl   { color:var(--muted); font-size:.72rem; }
    .greek-num   { color:var(--txt); font-size:1rem; font-weight:700; }

    /* Sidebar */
    [data-testid="stSidebar"] { background:#18191c; border-right:1px solid #3a3d44; }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stRadio label { color:#d0d3d8 !important; font-size:.88rem !important; font-weight:500 !important; }
    [data-testid="stSidebar"] h3 { color:#fff !important; font-size:.95rem !important; font-weight:700 !important; }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea {
        background:#26282c !important; color:#e8eaed !important;
        border:1px solid #44474e !important; border-radius:6px !important; }
    [data-testid="stSidebar"] hr { border-color:#3a3d44 !important; }
    [data-testid="stSidebar"] small { color:#7a7e87 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"]  { background:var(--card); border-radius:10px; padding:4px; }
    .stTabs [data-baseweb="tab"]       { color:var(--muted); border-radius:8px; }
    .stTabs [aria-selected="true"]     { background:var(--hover) !important; color:var(--txt) !important; }

    /* Buttons */
    .stButton > button {
        background:var(--hover); color:var(--txt);
        border:1px solid var(--bdr); border-radius:8px; font-weight:600; transition:all .2s; }
    .stButton > button:hover { border-color:var(--hi); background:#2e3035; }

    /* Expander */
    .streamlit-expanderHeader {
        background:var(--card) !important; border:1px solid var(--bdr) !important;
        border-radius:10px !important; color:var(--txt) !important; }

    /* Mobile */
    @media (max-width:768px) {
        .app-title  { font-size:1.3rem !important; }
        .kv-box table { font-size:.80rem !important; }
        .order-buy, .order-sell { font-size:.80rem !important; }
        .tp-val     { font-size:1.1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ── STORAGE ──────────────────────────────────────────────────────
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trade_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(h):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(h, f, indent=2)

def add_trade(trade):
    h = load_history()
    trade['id']            = int(time.time())
    trade['data_apertura'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    trade['stato']         = 'Aperto'
    h.insert(0, trade)
    save_history(h)

# ── BLACK-SCHOLES + GREEKS ───────────────────────────────────────
def bs(S, K, T, r, σ, typ):
    if T <= 0:
        return max(S-K,0) if typ=='call' else max(K-S,0)
    d1 = (np.log(S/K) + (r + .5*σ**2)*T) / (σ*np.sqrt(T))
    d2 = d1 - σ*np.sqrt(T)
    if typ == 'call': return float(S*norm.cdf(d1)  - K*np.exp(-r*T)*norm.cdf(d2))
    else:             return float(K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1))

def calc_greeks(S, K, T, r, σ, typ):
    if T <= 0: return dict(delta=0, gamma=0, theta=0, vega=0)
    d1 = (np.log(S/K) + (r + .5*σ**2)*T) / (σ*np.sqrt(T))
    d2 = d1 - σ*np.sqrt(T)
    delta = norm.cdf(d1) if typ=='call' else -norm.cdf(-d1)
    gamma = norm.pdf(d1) / (S*σ*np.sqrt(T))
    theta = (-(S*norm.pdf(d1)*σ)/(2*np.sqrt(T))
             - r*K*np.exp(-r*T)*(norm.cdf(d2) if typ=='call' else norm.cdf(-d2)))/365
    vega  = S*norm.pdf(d1)*np.sqrt(T)/100
    return dict(delta=round(delta,3), gamma=round(gamma,4), theta=round(theta,4), vega=round(vega,4))

def get_hv(ticker):
    data = yf.download(ticker, period='3mo', progress=False, auto_adjust=True)
    if data.empty: return None
    ret = np.log(data['Close']/data['Close'].shift(1)).dropna()
    v   = ret.std()
    return float(v.iloc[0] if hasattr(v,'iloc') else v) * np.sqrt(252)

# ── SCAN ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def scan_candidates(tickers):
    out = []
    for t in tickers:
        try:
            price = yf.Ticker(t).fast_info.last_price
            if not price or price < 5: continue
            hv = get_hv(t)
            if not hv or not (0.15 <= hv <= 0.90): continue

            hist  = yf.download(t, period='3mo', progress=False, auto_adjust=True)
            if hist.empty or len(hist) < 22: continue
            close = hist['Close'].squeeze()

            ret_1m = float((close.iloc[-1]-close.iloc[-21])/close.iloc[-21])
            ret_1w = float((close.iloc[-1]-close.iloc[-5]) /close.iloc[-5])

            # RSI
            d = close.diff()
            gain = d.where(d>0,0).rolling(14).mean()
            loss = (-d.where(d<0,0)).rolling(14).mean()
            rsi  = float(100 - 100/(1 + gain.iloc[-1]/loss.iloc[-1]))

            # MA
            ma20 = float(close.rolling(20).mean().iloc[-1])
            ma50 = float(close.rolling(50).mean().iloc[-1])
            c    = float(close.iloc[-1])

            # Score bilanciato — ogni segnale pesa indipendentemente
            bullish = 0
            bearish = 0
            if ret_1m >  0.03: bullish += 2
            if ret_1m < -0.03: bearish += 2
            if ret_1w >  0.01: bullish += 1
            if ret_1w < -0.01: bearish += 1
            if c > ma20:       bullish += 1
            else:              bearish += 1
            if c > ma50:       bullish += 1
            else:              bearish += 1
            if rsi > 55:       bullish += 1
            if rsi < 45:       bearish += 1

            # Direzione basata su chi vince
            score     = bullish - bearish
            direzione = 'call' if score >= 0 else 'put'

            # IV dalla catena opzioni (ATM call più vicina a DTE=30)
            iv_raw = None
            try:
                tk_obj = yf.Ticker(t)
                exps   = tk_obj.options
                if exps:
                    from datetime import date
                    today = date.today()
                    best_exp = min(exps, key=lambda e: abs((datetime.strptime(e, '%Y-%m-%d').date() - today).days - 30))
                    chain = tk_obj.option_chain(best_exp)
                    calls = chain.calls
                    atm   = calls.iloc[(calls['strike'] - float(price)).abs().argsort()[:1]]
                    iv_raw = float(atm['impliedVolatility'].values[0])
            except Exception:
                iv_raw = hv  # fallback a HV se IV non disponibile

            iv_hv = round(iv_raw / hv, 2) if (hv and hv > 0 and iv_raw) else None

            out.append({
                'Ticker':      t,
                'Prezzo':      round(float(price), 2),
                'HV (%)':      round(hv*100, 1),
                'IV (%)':      round(iv_raw*100, 1) if iv_raw else None,
                'IV/HV':       iv_hv,
                'RSI':         round(rsi, 1),
                'Trend 1M (%)':round(ret_1m*100, 2),
                'Trend 1W (%)':round(ret_1w*100, 2),
                'Score':       score,
                'Bull':        bullish,
                'Bear':        bearish,
                'direzione':   direzione,
                'hv_raw':      hv,
                'iv_raw':      iv_raw if iv_raw else hv,
                'price_raw':   float(price),
            })
        except Exception:
            continue
    return sorted(out, key=lambda x: abs(x['Score']), reverse=True)

# ── BUILD SPREAD ─────────────────────────────────────────────────
def build_spread(ticker, price, hv, direction, R_dollar, tp_R, dte, r=0.05, width_pct=0.05):
    """
    R_dollar  = valore monetario di 1R (la perdita massima per trade)
    tp_R      = multiplo di R per il take profit (es. 2.5 → target = 2.5R)
    """
    T    = dte / 365
    step = 1 if price < 50 else (2.5 if price < 100 else 5)

    if direction == 'call':
        K_long  = round(price / step) * step
        K_short = round((price*(1+width_pct)) / step) * step
        if K_short <= K_long: K_short = K_long + step
        pl  = bs(price, K_long,  T, r, hv, 'call')
        ps  = bs(price, K_short, T, r, hv, 'call')
        gl  = calc_greeks(price, K_long,  T, r, hv, 'call')
        gs  = calc_greeks(price, K_short, T, r, hv, 'call')
        net_debit  = (pl - ps) * 100
        max_profit_1c = (K_short - K_long)*100 - net_debit
        strat_name = 'Bull Call Spread'
        buy_label  = f"CALL {K_long}"
        sell_label = f"CALL {K_short}"
        breakeven  = K_long + net_debit/100
    else:
        K_long  = round(price / step) * step
        K_short = round((price*(1-width_pct)) / step) * step
        if K_short >= K_long: K_short = K_long - step
        pl  = bs(price, K_long,  T, r, hv, 'put')
        ps  = bs(price, K_short, T, r, hv, 'put')
        gl  = calc_greeks(price, K_long,  T, r, hv, 'put')
        gs  = calc_greeks(price, K_short, T, r, hv, 'put')
        net_debit  = (pl - ps) * 100
        max_profit_1c = (K_long - K_short)*100 - net_debit
        strat_name = 'Bear Put Spread'
        buy_label  = f"PUT {K_long}"
        sell_label = f"PUT {K_short}"
        breakeven  = K_long - net_debit/100

    if net_debit <= 0: net_debit = 0.01

    contracts      = max(1, int(R_dollar / net_debit))
    ingresso_tot   = round(net_debit * contracts, 2)   # quanto hai effettivamente pagato
    max_profit_tot = max_profit_1c * contracts

    # R_dollar rimane SEMPRE quello impostato dall'utente — non viene mai sovrascritto
    # tp_dollar = guadagno target in $
    tp_dollar      = round(R_dollar * tp_R, 2)
    actual_tp_R    = tp_R  # è esattamente il multiplo impostato

    # ── Prezzi di uscita da inserire su IBKR ─────────────────────
    # tp_exit  = ingresso_tot + profitto target   (es. 475.50 + 39.00 = 514.50)
    # sl_exit  = ingresso_tot - perdita massima   (es. 475.50 - 30.00 = 445.50)
    tp_exit_price  = round(ingresso_tot + tp_dollar, 2)
    sl_exit_price  = round(ingresso_tot - R_dollar, 2)

    # Premio per azione (per mostrarlo nella tabella)
    net_debit_per_sh = round(net_debit / 100, 2)

    net_delta = (gl['delta'] - gs['delta']) * contracts * 100
    net_theta = (gl['theta'] - gs['theta']) * contracts * 100
    net_vega  = (gl['vega']  - gs['vega'])  * contracts * 100

    return {
        'ticker':        ticker,
        'strategia':     strat_name,
        'direzione':     direction,
        'buy_label':     buy_label,
        'sell_label':    sell_label,
        'K_long':        K_long,
        'K_short':       K_short,
        'premio_buy':    round(pl, 2),
        'premio_sell':   round(ps, 2),
        'net_debit':     round(net_debit, 2),
        'net_debit_per_sh': round(net_debit_per_sh, 2),
        'contratti':     contracts,
        'ingresso_totale': round(ingresso_tot, 2),
        'max_loss':      round(ingresso_tot, 2),
        'max_profit':    round(max_profit_tot, 2),
        'R_dollar':      round(R_dollar, 2),
        'tp_R':          tp_R,
        'tp_dollar':     tp_dollar,
        'tp_exit_price': tp_exit_price,
        'sl_exit_price': sl_exit_price,
        'actual_tp_R':   actual_tp_R,
        'breakeven':     round(breakeven, 2),
        'dte':           dte,
        'price':         round(price, 2),
        'hv':            hv,
        'T':             T,
        'delta':         round(net_delta, 2),
        'theta':         round(net_theta, 4),
        'vega':          round(net_vega, 4),
        'rr_ratio':      round(max_profit_tot / ingresso_tot, 2) if ingresso_tot > 0 else 0,
    }

# ── GRAFICO P&L ──────────────────────────────────────────────────
def plot_pnl(s):
    prices = np.linspace(s['price']*0.78, s['price']*1.22, 500)
    Kl, Ks = s['K_long'], s['K_short']
    nd, c   = s['net_debit']/100, s['contratti']

    if s['direzione'] == 'call':
        pnl = np.where(prices<=Kl, -nd,
              np.where(prices>=Ks, (Ks-Kl)-nd, prices-Kl-nd)) * c * 100
    else:
        pnl = np.where(prices>=Kl, -nd,
              np.where(prices<=Ks, (Kl-Ks)-nd, Kl-prices-nd)) * c * 100

    fig = go.Figure()

    # Aree colorate
    fig.add_trace(go.Scatter(
        x=np.concatenate([prices, prices[::-1]]),
        y=np.concatenate([np.where(pnl>0,pnl,0), np.zeros(len(prices))]),
        fill='toself', fillcolor='rgba(76,175,130,0.10)',
        line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter(
        x=np.concatenate([prices, prices[::-1]]),
        y=np.concatenate([np.where(pnl<0,pnl,0), np.zeros(len(prices))]),
        fill='toself', fillcolor='rgba(192,95,95,0.10)',
        line=dict(width=0), showlegend=False, hoverinfo='skip'))

    # Curva P&L
    fig.add_trace(go.Scatter(
        x=prices, y=pnl, mode='lines',
        line=dict(color='#7ecfb0', width=2.5),
        name='P&L',
        hovertemplate='<b>$%{x:.2f}</b><br>P&L: <b>$%{y:.0f}</b><extra></extra>'))

    # Linee chiave
    fig.add_vline(x=s['price'],    line_dash='dash', line_color='#9aa3b0', line_width=1.5,
                  annotation=dict(text=f"<b>${s['price']}</b>", font=dict(color='#d0d3d8', size=11), bgcolor='#1c1e21', borderpad=3))
    fig.add_vline(x=s['breakeven'], line_dash='dot', line_color='#5a6272', line_width=1,
                  annotation=dict(text=f"BE ${s['breakeven']}", font=dict(color='#9aa3b0', size=10), bgcolor='#1c1e21', borderpad=3))
    fig.add_hline(y=0, line_color='rgba(255,255,255,0.15)', line_width=1)
    fig.add_hline(y=s['tp_dollar'],
                  line_dash='dash', line_color='#4caf82', line_width=1.2,
                  annotation=dict(text=f"TP {s['tp_R']}R = ${s['tp_dollar']:.0f}",
                                  font=dict(color='#4caf82', size=10), bgcolor='#1c1e21', borderpad=3))
    fig.add_hline(y=-s['max_loss'],
                  line_dash='dash', line_color='#c05f5f', line_width=1.2,
                  annotation=dict(text=f"1R = ${s['max_loss']:.0f}",
                                  font=dict(color='#c05f5f', size=10), bgcolor='#1c1e21', borderpad=3))

    fig.update_layout(
        height=420,
        paper_bgcolor='#111214', plot_bgcolor='#111214',
        font=dict(family='Inter', color='#d0d3d8', size=11),
        xaxis=dict(
            title='Prezzo ($)', gridcolor='#2e3035',
            showgrid=True, zeroline=False,
            tickfont=dict(size=10), tickformat='$.0f',
            fixedrange=False,   # ← permette zoom/pan
        ),
        yaxis=dict(
            title='P&L ($)', gridcolor='#2e3035',
            showgrid=True, zeroline=False,
            tickfont=dict(size=10), tickformat='$.0f',
            fixedrange=False,   # ← permette zoom/pan
        ),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10),
                    orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        margin=dict(l=55, r=20, t=45, b=50),
        autosize=True,
        dragmode='pan',         # ← default: panning con un dito/mouse
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='#7a7e87',
            activecolor='#e0e2e5',
        ),
    )
    return fig

# ── GRAFICO STORICO ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def plot_price_history(ticker):
    hist = yf.download(ticker, period='3mo', progress=False, auto_adjust=True)
    if hist.empty: return None
    close = hist['Close'].squeeze()
    ma20  = close.rolling(20).mean()
    ma50  = close.rolling(50).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=close, mode='lines',
                             line=dict(color='#7ecfb0', width=2), name='Prezzo'))
    fig.add_trace(go.Scatter(x=hist.index, y=ma20, mode='lines',
                             line=dict(color='#9aa3b0', width=1.2, dash='dash'), name='MA20'))
    fig.add_trace(go.Scatter(x=hist.index, y=ma50, mode='lines',
                             line=dict(color='#c05f5f', width=1.2, dash='dot'), name='MA50'))
    fig.update_layout(
        height=210,
        paper_bgcolor='#111214', plot_bgcolor='#111214',
        font=dict(family='Inter', color='#d0d3d8', size=10),
        xaxis=dict(gridcolor='#2e3035', showgrid=True, tickfont=dict(size=9), fixedrange=False),
        yaxis=dict(gridcolor='#2e3035', showgrid=True, tickfont=dict(size=9), tickformat='$.0f', fixedrange=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=9),
                    orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        margin=dict(l=50, r=10, t=35, b=30),
        autosize=True,
        dragmode='pan',
    )
    return fig

# ── SESSION STATE ────────────────────────────────────────────────
for k, v in [('scan_results',[]),('strategies',{})]:
    if k not in st.session_state: st.session_state[k] = v

# ── HEADER ───────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-title">andpast</div>
  <div class="app-sub">Debit Spread Advisor · Dati in tempo reale · Yahoo Finance</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Risk Management")

    risk_mode = st.radio(
        "Modalità rischio",
        ["R multiplo", "Valore assoluto ($)"],
        help="R multiplo: definisci 1R e il target in multipli. Valore assoluto: inserisci max loss e TP in dollari."
    )

    if risk_mode == "R multiplo":
        R_dollar = st.number_input(
            "Valore di 1R ($)", min_value=10.0, max_value=10000.0, value=200.0, step=10.0,
            help="Quanto sei disposto a perdere per trade (1R)"
        )
        tp_R = st.number_input(
            "Take Profit (multiplo di R)", min_value=0.5, max_value=10.0, value=2.5, step=0.5,
            help="Es: 2.5 → esci quando guadagni 2.5R"
        )
        # Calcola max_loss e tp_dollar da R
        max_loss_input = R_dollar
        tp_dollar_input = R_dollar * tp_R
        st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #2e3035;border-radius:8px;padding:.7rem 1rem;margin-top:.5rem;font-size:.85rem;">
  <div style="color:#7a7e87;">Max Loss &nbsp;<b style="color:#c05f5f;">${max_loss_input:.0f}</b></div>
  <div style="color:#7a7e87;margin-top:.3rem;">Take Profit &nbsp;<b style="color:#4caf82;">${tp_dollar_input:.0f}</b> &nbsp;({tp_R}R)</div>
</div>
""", unsafe_allow_html=True)
    else:
        max_loss_input = st.number_input(
            "Max Loss ($)", min_value=10.0, max_value=10000.0, value=300.0, step=10.0
        )
        tp_dollar_input = st.number_input(
            "Take Profit ($)", min_value=10.0, max_value=50000.0, value=600.0, step=10.0
        )
        R_dollar = max_loss_input
        tp_R     = round(tp_dollar_input / max_loss_input, 2)
        st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #2e3035;border-radius:8px;padding:.7rem 1rem;margin-top:.5rem;font-size:.85rem;">
  <div style="color:#7a7e87;">Rapporto R/R &nbsp;<b style="color:#9aa3b0;">{tp_R}R</b></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📐 Parametri Strategia")
    dte       = st.slider("DTE (giorni a scadenza)", 7, 60, 30)
    width_pct = st.slider("Ampiezza spread (%)", 3, 15, 5,
                           help="Distanza % tra i due strike") / 100
    direction = st.radio("Direzione", ['Auto (basata su trend)', 'Solo Rialzista', 'Solo Ribassista'])

    st.markdown("---")
    st.markdown("### 📋 Lista Titoli")
    default_tickers = "AAPL,MSFT,NVDA,TSLA,AMZN,META,GOOGL,AMD,SPY,QQQ,NFLX,COIN,MSTR,JPM,GS,XOM,BA"
    custom    = st.text_area("Ticker (separati da virgola)", default_tickers, height=100)
    scan_btn  = st.button("🔍 Scansiona Mercato", use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["📊 Scanner & Strategie", "📈 Dashboard", "📋 Storico", "📊 Statistiche"])

# ── TAB 1: SCANNER ───────────────────────────────────────────────
with tab1:
    if scan_btn:
        tickers_list = [t.strip().upper() for t in custom.split(',') if t.strip()]
        with st.spinner(f"Analisi di {len(tickers_list)} titoli..."):
            results = scan_candidates(tuple(tickers_list))
            st.session_state['scan_results'] = results
            st.session_state['strategies']   = {}
            for r in results:
                dir_code = r.get('direzione','call')
                if direction == 'Solo Rialzista':  dir_code = 'call'
                if direction == 'Solo Ribassista': dir_code = 'put'
                tk = r.get('Ticker','')
                if not tk: continue
                try:
                    s = build_spread(tk, r['price_raw'], r['hv_raw'],
                                     dir_code, R_dollar, tp_R, dte, width_pct=width_pct)
                    st.session_state['strategies'][tk] = s
                except Exception as e:
                    st.warning(f"Errore su {tk}: {e}")

    results    = st.session_state['scan_results']
    strategies = st.session_state['strategies']

    if not results:
        st.markdown("""
<div style="text-align:center;padding:4rem;color:#7a7e87;">
  <div style="font-size:2.5rem;">🔍</div>
  <div style="margin-top:1rem;font-size:1rem;">Imposta i parametri e clicca <b>Scansiona Mercato</b></div>
</div>""", unsafe_allow_html=True)
    else:
        # Summary strip
        n_call = sum(1 for r in results if r.get('direzione')=='call')
        n_put  = len(results) - n_call
        avg_hv = np.mean([r['HV (%)'] for r in results])
        c1,c2,c3,c4 = st.columns(4)
        def mcard(col, label, val, cls=''):
            col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div>'
                         f'<div class="metric-value {cls}">{val}</div></div>', unsafe_allow_html=True)
        mcard(c1,'Candidati',len(results))
        mcard(c2,'📈 / 📉',f'{n_call} / {n_put}','yellow')
        mcard(c3,'HV media',f'{avg_hv:.1f}%')
        mcard(c4,'Rischio 1R',f'${R_dollar:.0f}','red')

        st.markdown("<br>", unsafe_allow_html=True)

        for r in results:
            tk = r['Ticker']
            s  = strategies.get(tk)
            if not s: continue

            dir_emoji = "📈" if s['direzione']=='call' else "📉"
            bull_bar  = '█' * r['Bull'] + '░' * (5 - r['Bull'])
            bear_bar  = '█' * r['Bear'] + '░' * (5 - r['Bear'])

            with st.expander(
                f"{dir_emoji} **{tk}** — {s['strategia']} | "
                f"1R=${s['R_dollar']:.2f} | TP=${s['tp_exit_price']:.2f} · SL=${s['sl_exit_price']:.2f} | "
                f"R/R {s['rr_ratio']}x",
                expanded=False
            ):
                col_l, col_r = st.columns([1, 1.6])

                # ── COLONNA SINISTRA ──────────────────────────────
                with col_l:
                    # intestazione
                    st.markdown(f"""
<div class="kv-box" style="margin-bottom:.5rem;">
  <div style="font-size:1.15rem;font-weight:700;color:var(--txt);">{tk}
    <span style="font-size:.82rem;color:var(--muted);font-weight:400;">{s['strategia']}</span>
  </div>
  <div style="margin-top:.4rem;font-size:.82rem;color:var(--muted);">
    Prezzo <b style="color:var(--txt)">${s['price']:.2f}</b> &nbsp;·&nbsp;
    HV <b style="color:var(--txt)">{r['HV (%)']}%</b> &nbsp;·&nbsp;
    IV <b style="color:var(--txt)">{r.get('IV (%)', '—')}%</b> &nbsp;·&nbsp;
    IV/HV <b style="color:var(--txt)">{r.get('IV/HV', '—')}</b> &nbsp;·&nbsp;
    RSI <b style="color:var(--txt)">{r['RSI']}</b>
  </div>
  <div style="margin-top:.3rem;font-size:.78rem;color:var(--muted);">
    Bull: <span style="color:var(--pos);letter-spacing:1px;">{bull_bar}</span>
    &nbsp;&nbsp;
    Bear: <span style="color:var(--neg);letter-spacing:1px;">{bear_bar}</span>
  </div>
</div>
""", unsafe_allow_html=True)

                    # ordini
                    st.markdown(f'<div class="order-buy">▲ COMPRA {s["buy_label"]} @ ${s["premio_buy"]:.2f}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="order-sell">▼ VENDI {s["sell_label"]} @ ${s["premio_sell"]:.2f}</div>', unsafe_allow_html=True)

                    # tabella valori
                    st.markdown(f"""
<div class="kv-box">
<table>
  <tr><td class="kv-label">Contratti</td>      <td class="kv-val">{s['contratti']}</td></tr>
  <tr><td class="kv-label">Premio netto</td>   <td class="kv-val">${s['net_debit_per_sh']:.2f} / az.</td></tr>
  <tr><td class="kv-label">Ingresso totale</td><td class="kv-val">${s['ingresso_totale']:.2f}</td></tr>
  <tr><td class="kv-label">1R (Max Loss)</td>  <td class="kv-neg">${s['R_dollar']:.2f}</td></tr>
  <tr><td class="kv-label">Target profitto</td><td class="kv-pos">+${s['tp_dollar']:.2f} ({s['tp_R']}R)</td></tr>
  <tr><td class="kv-label">Max Profit teorico</td><td class="kv-pos">${s['max_profit']:.2f}</td></tr>
  <tr><td class="kv-label">Breakeven</td>      <td class="kv-val">${s['breakeven']:.2f}</td></tr>
  <tr><td class="kv-label">R/R effettivo</td>  <td class="kv-val">{s['rr_ratio']}x</td></tr>
  <tr><td class="kv-label">Scadenza</td>       <td class="kv-val">{s['dte']} giorni</td></tr>
</table>
</div>
""", unsafe_allow_html=True)

                    # ordini TP e SL
                    st.markdown(f"""
<div class="tp-box">
  <div class="tp-label">📤 Ordini da inserire su IBKR</div>
  <div style="margin-top:.6rem;">
    <div style="font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;">Take Profit — {s['tp_R']}R</div>
    <div style="color:var(--pos);font-size:1.2rem;font-weight:700;margin-top:.2rem;">
      Chiudi a <b>${s['tp_exit_price']:.2f}</b>
      <span class="r-badge">+${s['tp_dollar']:.2f}</span>
    </div>
    <div style="font-size:.8rem;color:var(--muted);margin-top:.2rem;">
      Ingresso ${s['ingresso_totale']:.2f} + ${s['tp_dollar']:.2f} profitto = <b>${s['tp_exit_price']:.2f}</b>
    </div>
  </div>
  <div style="border-top:1px solid var(--bdr);margin:.7rem 0;"></div>
  <div>
    <div style="font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;">Stop Loss — 1R</div>
    <div style="color:var(--neg);font-size:1.2rem;font-weight:700;margin-top:.2rem;">
      Chiudi a <b>${s['sl_exit_price']:.2f}</b>
      <span class="r-badge" style="background:rgba(192,95,95,.12);border-color:#c05f5f;color:#c05f5f;">−${s['R_dollar']:.2f}</span>
    </div>
    <div style="font-size:.8rem;color:var(--muted);margin-top:.2rem;">
      Ingresso ${s['ingresso_totale']:.2f} − ${s['R_dollar']:.2f} rischio = <b>${s['sl_exit_price']:.2f}</b>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

                    # greeks
                    st.markdown(f"""
<div class="greek-box">
  <div class="greek-title">Greeks netti</div>
  <div class="greek-grid">
    <div class="greek-item"><div class="greek-lbl">Delta</div><div class="greek-num">{s['delta']}</div></div>
    <div class="greek-item"><div class="greek-lbl">Theta/gg</div><div class="greek-num">{s['theta']}</div></div>
    <div class="greek-item"><div class="greek-lbl">Vega</div><div class="greek-num">{s['vega']}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

                    note_input = st.text_area("📝 Note entrata", placeholder="Motivo del trade, setup, contesto di mercato...", key=f"note_{tk}", height=80)
                    if st.button("➕ Aggiungi a storico", key=f"add_{tk}"):
                        add_trade({
                            'ticker': tk, 'strategia': s['strategia'],
                            'buy': s['buy_label'], 'sell': s['sell_label'],
                            'contratti': s['contratti'],
                            'ingresso': s['ingresso_totale'],
                            'R_dollar': s['R_dollar'],
                            'tp_R': s['tp_R'],
                            'tp_dollar': s['tp_dollar'],
                            'max_profit': s['max_profit'],
                            'breakeven': s['breakeven'],
                            'dte': s['dte'],
                            'note_entrata': note_input,
                        })
                        st.success("Trade aggiunto!")

                # ── COLONNA DESTRA ────────────────────────────────
                with col_r:
                    # Config grafico: mostra pulsanti zoom/pan
                    pnl_fig = plot_pnl(s)
                    st.plotly_chart(
                        pnl_fig,
                        use_container_width=True,
                        config={
                            'scrollZoom':     True,   # zoom con scroll/pinch
                            'displayModeBar': True,
                            'modeBarButtonsToRemove': ['select2d','lasso2d','autoScale2d','toImage'],
                            'modeBarButtonsToAdd': ['drawopenpath'],
                            'displaylogo':    False,
                        }
                    )
                    hist_fig = plot_price_history(tk)
                    if hist_fig:
                        st.plotly_chart(
                            hist_fig,
                            use_container_width=True,
                            config={
                                'scrollZoom':     True,
                                'displayModeBar': True,
                                'modeBarButtonsToRemove': ['select2d','lasso2d','toImage'],
                                'displaylogo':    False,
                            }
                        )

# ── TAB 2: DASHBOARD ─────────────────────────────────────────────
with tab2:
    history      = load_history()
    open_trades  = [h for h in history if h.get('stato')=='Aperto']
    closed_trades= [h for h in history if h.get('stato')=='Chiuso']

    st.markdown("### 📈 Dashboard Portfolio")

    if not history:
        st.info("Nessun trade registrato. Usa lo Scanner e clicca ➕ Aggiungi a storico.")
    else:
        tot_rischio   = sum(t.get('R_dollar', t.get('max_loss',0)) for t in open_trades)
        tot_tp        = sum(t.get('tp_dollar', t.get('max_profit',0)) for t in open_trades)
        tot_pnl       = sum(t.get('pnl_finale',0) for t in closed_trades)

        d1,d2,d3,d4 = st.columns(4)
        mcard(d1, 'Trade aperti',    len(open_trades))
        mcard(d2, 'Rischio totale',  f'${tot_rischio:.0f}', 'red')
        mcard(d3, 'Profit potenziale',f'${tot_tp:.0f}',      'green')
        pnl_cls = 'green' if tot_pnl >= 0 else 'red'
        mcard(d4, 'P&L realizzato',  f'${tot_pnl:.0f}',      pnl_cls)

        st.markdown("<br>", unsafe_allow_html=True)

        if open_trades:
            st.markdown("### 🔔 Monitoraggio trade aperti")
            for trade in open_trades:
                tk2 = trade.get('ticker','')
                try:
                    cur = yf.Ticker(tk2).fast_info.last_price
                    be  = trade.get('breakeven', 0)
                    tp  = trade.get('tp_dollar', trade.get('tp_target', 0))
                    ml  = trade.get('R_dollar', trade.get('max_loss',1))
                    strat = trade.get('strategia','')
                    if 'Call' in strat:
                        prog = max(0, (cur - be) / max(tp - be, 0.01))
                    else:
                        prog = max(0, (be - cur) / max(be - tp, 0.01))
                    prog  = min(prog, 1.0)
                    col   = '#4caf82' if prog>=0.8 else ('#9aa3b0' if prog>=0.4 else '#c05f5f')
                    icon  = '🚨' if prog>=0.9 else ('⚡' if prog>=0.5 else '·')
                    tp_R_lbl = trade.get('tp_R','')
                    st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #2e3035;border-radius:10px;padding:1rem;margin:.4rem 0;">
  <div style="display:flex;justify-content:space-between;margin-bottom:.5rem;">
    <span style="color:#e0e2e5;font-weight:600;">{icon} {tk2} — {strat}</span>
    <span style="color:{col};font-weight:700;">{prog*100:.0f}% del target</span>
  </div>
  <div style="background:#111214;border-radius:4px;height:7px;">
    <div style="background:{col};width:{prog*100:.0f}%;height:7px;border-radius:4px;"></div>
  </div>
  <div style="color:#7a7e87;font-size:.8rem;margin-top:.35rem;">
    Prezzo: ${cur:.2f} · Target: ${tp:.0f} ({tp_R_lbl}R) · 1R: ${ml:.0f}
  </div>
</div>
""", unsafe_allow_html=True)
                except Exception:
                    st.caption(f"· {tk2} — dati non disponibili")

# ── TAB 3: STORICO ───────────────────────────────────────────────
with tab3:
    st.markdown("### 📋 Storico Operazioni")
    history = load_history()

    if not history:
        st.info("Nessuna operazione registrata.")
    else:
        cf1, cf2 = st.columns([2,1])
        with cf1:
            filtro = st.selectbox("Filtra", ["Tutti","Aperto","Chiuso"])
        with cf2:
            if st.button("🗑️ Cancella tutto"):
                save_history([]); st.rerun()

        filtered = history if filtro=='Tutti' else [h for h in history if h.get('stato')==filtro]

        for trade in filtered:
            stato_c = '#4caf82' if trade.get('stato')=='Chiuso' else '#9aa3b0'
            with st.expander(
                f"**{trade.get('ticker','')}** — {trade.get('strategia','')} | "
                f"{trade.get('data_apertura','')} | {trade.get('stato','')}",
                expanded=False
            ):
                e1, e2 = st.columns(2)
                with e1:
                    st.markdown(f"🟢 **COMPRA:** {trade.get('buy','')}")
                    st.markdown(f"🔴 **VENDI:** {trade.get('sell','')}")
                    st.markdown(f"**Contratti:** {trade.get('contratti','')}")
                    st.markdown(f"**Ingresso:** ${trade.get('ingresso','')}")
                with e2:
                    st.markdown(f"**1R (Max Loss):** ${trade.get('R_dollar', trade.get('max_loss',''))}")
                    st.markdown(f"**Target ({trade.get('tp_R','')}R):** ${trade.get('tp_dollar', trade.get('tp_target',''))}")
                    st.markdown(f"**Max Profit:** ${trade.get('max_profit','')}")
                    st.markdown(f"**Breakeven:** ${trade.get('breakeven','')}")

                # note
                ne = trade.get('note_entrata','')
                nu = trade.get('note_uscita','')
                if ne:
                    st.markdown(f"📝 **Note entrata:** {ne}")
                if nu:
                    st.markdown(f"📤 **Note uscita:** {nu}")

                st.markdown("---")
                if trade.get('stato') == 'Aperto':
                    note_u = st.text_area("📤 Note uscita", placeholder="Perché hai chiuso? TP / SL / tempo / altro...", key=f"noteu_{trade['id']}", height=70)
                    ca, cb, cc = st.columns(3)
                    with ca:
                        pnl_in = st.number_input("P&L finale ($)", value=0.0, key=f"pnl_{trade['id']}")
                    motivo_options = ["Take Profit ✅", "Stop Loss ❌", "Regola tempo ⏱️", "Manuale 🖐️"]
                    with cb:
                        motivo = st.selectbox("Motivo chiusura", motivo_options, key=f"mot_{trade['id']}")
                    with cc:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("✅ Chiudi", key=f"close_{trade['id']}"):
                            for h in history:
                                if h['id']==trade['id']:
                                    h['stato']='Chiuso'
                                    h['data_chiusura']=datetime.now().strftime("%d/%m/%Y %H:%M")
                                    h['pnl_finale']=pnl_in
                                    h['motivo_chiusura']=motivo
                                    h['note_uscita']=note_u
                            save_history(history); st.rerun()
                else:
                    pnl_f = trade.get('pnl_finale', 0)
                    mot_f = trade.get('motivo_chiusura','—')
                    data_c = trade.get('data_chiusura','—')
                    pnl_col = '#4caf82' if pnl_f >= 0 else '#c05f5f'
                    st.markdown(f"""
<div style="background:#1c1e21;border:1px solid #2e3035;border-radius:8px;padding:.7rem 1rem;font-size:.88rem;">
  <span style="color:#7a7e87;">Chiuso il</span> <b style="color:#e0e2e5;">{data_c}</b> &nbsp;·&nbsp;
  <span style="color:#7a7e87;">Motivo:</span> <b style="color:#e0e2e5;">{mot_f}</b> &nbsp;·&nbsp;
  <span style="color:#7a7e87;">P&L:</span> <b style="color:{pnl_col};">${pnl_f:.0f}</b>
</div>""", unsafe_allow_html=True)

                if st.button("🗑️ Elimina", key=f"del_{trade['id']}"):
                    save_history([h for h in history if h['id']!=trade['id']]); st.rerun()

# ── TAB 4: STATISTICHE ──────────────────────────────────────────
with tab4:
    st.markdown("### 📊 Statistiche & Edge Analysis")
    history_s = load_history()
    closed_s  = [h for h in history_s if h.get('stato')=='Chiuso' and 'pnl_finale' in h]

    if len(closed_s) < 2:
        st.info("Servono almeno 2 trade chiusi per calcolare le statistiche. Completa qualche operazione e torna qui.")
    else:
        pnls      = [h['pnl_finale'] for h in closed_s]
        wins      = [p for p in pnls if p > 0]
        losses    = [p for p in pnls if p <= 0]
        n         = len(pnls)
        n_win     = len(wins)
        n_loss    = len(losses)
        win_rate  = n_win / n * 100
        avg_win   = np.mean(wins)   if wins   else 0
        avg_loss  = abs(np.mean(losses)) if losses else 0
        expectancy= np.mean(pnls)
        pf        = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else float('inf')

        # Streak
        best_streak = worst_streak = cur_streak = 0
        cur_type = None
        for p in pnls:
            t = 'w' if p > 0 else 'l'
            if t == cur_type:
                cur_streak += 1
            else:
                cur_type   = t
                cur_streak = 1
            if t == 'w': best_streak  = max(best_streak,  cur_streak)
            else:        worst_streak = max(worst_streak, cur_streak)

        # R multipli
        r_list = []
        for h in closed_s:
            r_val = h.get('R_dollar', h.get('max_loss', 1))
            if r_val and r_val > 0:
                r_list.append(h['pnl_finale'] / r_val)
        avg_r = np.mean(r_list) if r_list else 0

        # ── Metriche principali ──
        s1,s2,s3,s4 = st.columns(4)
        def scard(col, label, val, cls=''):
            col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div>'
                         f'<div class="metric-value {cls}">{val}</div></div>', unsafe_allow_html=True)

        scard(s1, 'Trade totali',  n)
        wr_cls = 'green' if win_rate >= 50 else 'red'
        scard(s2, 'Win Rate',      f'{win_rate:.1f}%', wr_cls)
        exp_cls = 'green' if expectancy >= 0 else 'red'
        scard(s3, 'Expectancy',    f'${expectancy:.1f}', exp_cls)
        pf_cls = 'green' if pf >= 1 else 'red'
        scard(s4, 'Profit Factor', f'{pf:.2f}', pf_cls)

        st.markdown("<br>", unsafe_allow_html=True)

        s5,s6,s7,s8 = st.columns(4)
        scard(s5, 'Avg Win',       f'${avg_win:.1f}',  'green')
        scard(s6, 'Avg Loss',      f'${avg_loss:.1f}', 'red')
        scard(s7, 'Best streak',   f'{best_streak} ✅')
        scard(s8, 'Worst streak',  f'{worst_streak} ❌')

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Spiegazione edge ──
        edge_color = '#4caf82' if expectancy > 0 else '#c05f5f'
        edge_label = 'EDGE POSITIVO ✅' if expectancy > 0 else 'EDGE NEGATIVO ❌'
        edge_msg   = (f"Su {n} trade, guadagni mediamente ${expectancy:.1f} per operazione. "
                      f"Il tuo Profit Factor è {pf:.2f} (>1 = profittevole). "
                      f"Media R per trade: {avg_r:.2f}R.") if expectancy > 0 else                      (f"Su {n} trade, perdi mediamente ${abs(expectancy):.1f} per operazione. "
                      f"Profit Factor {pf:.2f} (<1 = non profittevole ancora). "
                      f"Analizza le note dei trade perdenti per trovare pattern da correggere.")
        st.markdown(f"""
<div style="background:#1c1e21;border:1px solid {edge_color};border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;">
  <div style="color:{edge_color};font-size:1rem;font-weight:700;margin-bottom:.4rem;">{edge_label}</div>
  <div style="color:#d0d3d8;font-size:.88rem;">{edge_msg}</div>
</div>
""", unsafe_allow_html=True)

        # ── Equity Curve ──
        st.markdown("#### Equity Curve")
        cumulative = np.cumsum([0] + pnls).tolist()
        trade_nums = list(range(len(cumulative)))
        dates_lbl  = ['Start'] + [h.get('data_chiusura', f'T{i+1}') for i,h in enumerate(closed_s)]

        fig_eq = go.Figure()
        # Area colore
        fig_eq.add_trace(go.Scatter(
            x=trade_nums, y=cumulative,
            fill='tozeroy',
            fillcolor='rgba(76,175,130,0.08)' if cumulative[-1] >= 0 else 'rgba(192,95,95,0.08)',
            line=dict(color='#4caf82' if cumulative[-1] >= 0 else '#c05f5f', width=2.5),
            mode='lines+markers',
            marker=dict(
                size=7,
                color=['#4caf82' if (cumulative[i]-cumulative[i-1])>=0 else '#c05f5f'
                       for i in range(len(cumulative))],
                line=dict(width=1, color='#111214')
            ),
            text=dates_lbl,
            hovertemplate='<b>%{text}</b><br>Equity: $%{y:.0f}<extra></extra>',
            name='Equity'
        ))
        fig_eq.add_hline(y=0, line_color='rgba(255,255,255,0.15)', line_width=1)

        # Drawdown max
        peak = max(cumulative)
        trough_after_peak = min(cumulative[cumulative.index(peak):]) if peak > 0 else 0
        max_dd = peak - trough_after_peak
        if max_dd > 0:
            fig_eq.add_annotation(
                text=f"Max DD: −${max_dd:.0f}",
                xref="paper", yref="paper", x=0.98, y=0.02,
                showarrow=False, font=dict(color='#c05f5f', size=10),
                bgcolor='#1c1e21', borderpad=4
            )

        fig_eq.update_layout(
            height=320, paper_bgcolor='#111214', plot_bgcolor='#111214',
            font=dict(family='Inter', color='#d0d3d8', size=11),
            xaxis=dict(title='Numero trade', gridcolor='#2e3035', tickfont=dict(size=10), fixedrange=False),
            yaxis=dict(title='P&L cumulativo ($)', gridcolor='#2e3035', tickfont=dict(size=10),
                       tickformat='$.0f', fixedrange=False),
            margin=dict(l=55,r=20,t=20,b=45),
            showlegend=False, dragmode='pan',
        )
        st.plotly_chart(fig_eq, use_container_width=True,
                        config={'scrollZoom':True,'displayModeBar':True,'displaylogo':False,
                                'modeBarButtonsToRemove':['select2d','lasso2d','toImage']})

        # ── Distribuzione P&L ──
        st.markdown("#### Distribuzione P&L per trade")
        colors_bar = ['#4caf82' if p >= 0 else '#c05f5f' for p in pnls]
        labels_bar = [h.get('ticker','?') + '<br>' + h.get('data_chiusura','')[:10] for h in closed_s]

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Bar(
            x=list(range(1, n+1)), y=pnls,
            marker_color=colors_bar,
            text=[f'${p:.0f}' for p in pnls],
            textposition='outside',
            textfont=dict(size=9),
            customdata=labels_bar,
            hovertemplate='<b>%{customdata}</b><br>P&L: $%{y:.0f}<extra></extra>',
        ))
        fig_dist.add_hline(y=0, line_color='rgba(255,255,255,0.2)', line_width=1)
        fig_dist.add_hline(y=expectancy, line_dash='dash', line_color='#9aa3b0', line_width=1,
                           annotation=dict(text=f'Media ${expectancy:.0f}', font=dict(color='#9aa3b0', size=10)))
        fig_dist.update_layout(
            height=280, paper_bgcolor='#111214', plot_bgcolor='#111214',
            font=dict(family='Inter', color='#d0d3d8', size=10),
            xaxis=dict(title='Trade #', gridcolor='#2e3035', tickfont=dict(size=9), fixedrange=False),
            yaxis=dict(title='P&L ($)', gridcolor='#2e3035', tickfont=dict(size=9),
                       tickformat='$.0f', fixedrange=False),
            margin=dict(l=50,r=20,t=20,b=45),
            showlegend=False, dragmode='pan',
        )
        st.plotly_chart(fig_dist, use_container_width=True,
                        config={'scrollZoom':True,'displayModeBar':True,'displaylogo':False,
                                'modeBarButtonsToRemove':['select2d','lasso2d','toImage']})

        # ── Tabella dettaglio per motivo ──
        st.markdown("#### Performance per motivo di chiusura")
        motivi = {}
        for h in closed_s:
            m = h.get('motivo_chiusura','Non specificato')
            if m not in motivi: motivi[m] = []
            motivi[m].append(h['pnl_finale'])

        rows = []
        for m, vals in motivi.items():
            w = len([v for v in vals if v > 0])
            rows.append({
                'Motivo':    m,
                'Trade':     len(vals),
                'Win Rate':  f"{w/len(vals)*100:.0f}%",
                'P&L Medio': f"${np.mean(vals):.1f}",
                'P&L Tot':   f"${sum(vals):.0f}",
            })
        if rows:
            df_mot = pd.DataFrame(rows)
            st.dataframe(df_mot.set_index('Motivo'), use_container_width=True)

        # ── Analisi per ticker ──
        st.markdown("#### Performance per ticker")
        tickers_stat = {}
        for h in closed_s:
            tk_ = h.get('ticker','?')
            if tk_ not in tickers_stat: tickers_stat[tk_] = []
            tickers_stat[tk_].append(h['pnl_finale'])

        rows_t = []
        for tk_, vals in sorted(tickers_stat.items(), key=lambda x: sum(x[1]), reverse=True):
            w = len([v for v in vals if v > 0])
            rows_t.append({
                'Ticker':    tk_,
                'Trade':     len(vals),
                'Win Rate':  f"{w/len(vals)*100:.0f}%",
                'P&L Medio': f"${np.mean(vals):.1f}",
                'P&L Tot':   f"${sum(vals):.0f}",
            })
        if rows_t:
            df_tk = pd.DataFrame(rows_t)
            st.dataframe(df_tk.set_index('Ticker'), use_container_width=True)

st.markdown("---")
st.caption("⚠️ andpast è uno strumento educativo. Non costituisce consulenza finanziaria. Il trading di opzioni comporta rischi significativi.")
