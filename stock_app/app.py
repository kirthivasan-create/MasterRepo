import yfinance as yf
import streamlit as st
import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator, IchimokuIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
import anthropic

# Load images for recommendations (optional)
try:
    buy_image = "buy.png"  # Path to buy image
except:
    buy_image = None

try:
    sell_image = "sell.png"  # Path to sell image
except:
    sell_image = None

try:
    hold_image = "hold.png"  # Path to hold image
except:
    hold_image = None

def get_rec_color(rec):
    if rec == "Buy":
        return "green"
    elif rec == "Sell":
        return "red"
    elif rec == "Hold":
        return "orange"
    else:
        return "blue"

def get_rec_image(rec):
    if rec == "Buy" and buy_image:
        return buy_image
    elif rec == "Sell" and sell_image:
        return sell_image
    elif rec == "Hold" and hold_image:
        return hold_image
    else:
        return None

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('regularMarketPrice')
    except:
        return None

def analyze_pe(ticker):
    try:
        info = yf.Ticker(ticker).info
        pe = info.get('trailingPE')
        if pe is None:
            return "N/A", "N/A"
        if pe < 15:
            rec = "Buy"
        elif pe < 25:
            rec = "Hold"
        else:
            rec = "Sell"
        return f"{pe:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_eps_growth(ticker):
    try:
        stock = yf.Ticker(ticker)
        financials = stock.financials
        info = stock.info
        shares = info.get('sharesOutstanding')
        if shares is None or financials.empty:
            return "N/A", "N/A"
        net_income = financials.loc['Net Income']
        if len(net_income) < 2:
            return "N/A", "N/A"
        eps_current = net_income.iloc[0] / shares
        eps_prev = net_income.iloc[1] / shares
        if eps_prev == 0:
            growth = 0
        else:
            growth = ((eps_current - eps_prev) / abs(eps_prev)) * 100
        if growth > 10:
            rec = "Buy"
        elif growth > 0:
            rec = "Hold"
        else:
            rec = "Sell"
        return f"{growth:.2f}%", rec
    except:
        return "N/A", "N/A"

def analyze_debt_to_equity(ticker):
    try:
        info = yf.Ticker(ticker).info
        de = info.get('debtToEquity')
        if de is None:
            return "N/A", "N/A"
        if de < 0.5:
            rec = "Buy"
        elif de < 1.0:
            rec = "Hold"
        else:
            rec = "Sell"
        return f"{de:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_revenue_growth(ticker):
    try:
        financials = yf.Ticker(ticker).financials
        revenue = financials.loc['Total Revenue']
        if len(revenue) < 2:
            return "N/A", "N/A"
        growth = ((revenue.iloc[0] - revenue.iloc[1]) / abs(revenue.iloc[1])) * 100
        if growth > 10:
            rec = "Buy"
        elif growth > 0:
            rec = "Hold"
        else:
            rec = "Sell"
        return f"{growth:.2f}%", rec
    except:
        return "N/A", "N/A"

def analyze_profit_margins(ticker):
    try:
        financials = yf.Ticker(ticker).financials
        net_income = financials.loc['Net Income']
        revenue = financials.loc['Total Revenue']
        if revenue.iloc[0] == 0:
            margin = 0
        else:
            margin = (net_income.iloc[0] / revenue.iloc[0]) * 100
        if margin > 10:
            rec = "Buy"
        elif margin > 5:
            rec = "Hold"
        else:
            rec = "Sell"
        return f"{margin:.2f}%", rec
    except:
        return "N/A", "N/A"

def analyze_rsi(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 14:
            return "N/A", "N/A"
        rsi = RSIIndicator(data['Close'], window=14).rsi().iloc[-1]
        if rsi < 30:
            rec = "Buy"
        elif rsi > 70:
            rec = "Sell"
        else:
            rec = "Hold"
        return f"{rsi:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_macd(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 26:
            return "N/A", "N/A"
        macd = MACD(data['Close'])
        macd_val = macd.macd().iloc[-1]
        signal = macd.macd_signal().iloc[-1]
        if macd_val > signal:
            rec = "Buy"
        else:
            rec = "Sell"
        return f"{macd_val:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_bb(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 20:
            return "N/A", "N/A"
        bb = BollingerBands(data['Close'])
        upper = bb.bollinger_hband().iloc[-1]
        lower = bb.bollinger_lband().iloc[-1]
        current = data['Close'].iloc[-1]
        if current < lower:
            rec = "Buy"
        elif current > upper:
            rec = "Sell"
        else:
            rec = "Hold"
        return f"U:{upper:.2f} L:{lower:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_ma(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 20:
            return "N/A", "N/A"
        sma = SMAIndicator(data['Close'], window=20).sma_indicator().iloc[-1]
        ema = EMAIndicator(data['Close'], window=20).ema_indicator().iloc[-1]
        current = data['Close'].iloc[-1]
        if current > sma:
            rec = "Buy"
        else:
            rec = "Sell"
        return f"SMA:{sma:.2f} EMA:{ema:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_volume(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 20:
            return "N/A", "N/A"
        avg_vol = data['Volume'].tail(20).mean()
        current_vol = data['Volume'].iloc[-1]
        if current_vol > avg_vol * 1.5:
            rec = "Buy"
        else:
            rec = "Hold"
        return f"{current_vol:.0f} (Avg:{avg_vol:.0f})", rec
    except:
        return "N/A", "N/A"

def analyze_stoch(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 14:
            return "N/A", "N/A"
        stoch = StochasticOscillator(data['High'], data['Low'], data['Close'])
        k = stoch.stoch().iloc[-1]
        d = stoch.stoch_signal().iloc[-1]
        if k < 20:
            rec = "Buy"
        elif k > 80:
            rec = "Sell"
        else:
            rec = "Hold"
        return f"K:{k:.2f} D:{d:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_adx(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 14:
            return "N/A", "N/A"
        adx = ADXIndicator(data['High'], data['Low'], data['Close'])
        adx_val = adx.adx().iloc[-1]
        if adx_val > 25:
            rec = "Strong Trend"
        else:
            rec = "Weak Trend"
        return f"{adx_val:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_atr(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 14:
            return "N/A", "N/A"
        atr = AverageTrueRange(data['High'], data['Low'], data['Close'])
        atr_val = atr.average_true_range().iloc[-1]
        return f"{atr_val:.2f}", "Info"
    except:
        return "N/A", "N/A"

def analyze_obv(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 1:
            return "N/A", "N/A"
        obv = OnBalanceVolumeIndicator(data['Close'], data['Volume'])
        obv_val = obv.on_balance_volume().iloc[-1]
        prev_obv = obv.on_balance_volume().iloc[-2] if len(obv.on_balance_volume()) > 1 else obv_val
        if obv_val > prev_obv:
            rec = "Buy"
        else:
            rec = "Sell"
        return f"{obv_val:.0f}", rec
    except:
        return "N/A", "N/A"

def analyze_ichimoku(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        if len(data) < 52:
            return "N/A", "N/A"
        ichi = IchimokuIndicator(data['High'], data['Low'])
        tenkan = ichi.ichimoku_conversion_line().iloc[-1]
        kijun = ichi.ichimoku_base_line().iloc[-1]
        current = data['Close'].iloc[-1]
        if current > tenkan and current > kijun:
            rec = "Buy"
        else:
            rec = "Sell"
        return f"T:{tenkan:.2f} K:{kijun:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_fib(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        high = data['High'].max()
        low = data['Low'].min()
        fib_618 = low + (high - low) * 0.618
        current = data['Close'].iloc[-1]
        if current < fib_618:
            rec = "Buy"
        else:
            rec = "Sell"
        return f"0.618:{fib_618:.2f}", rec
    except:
        return "N/A", "N/A"

def analyze_sr(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        recent_high = data['High'].tail(20).max()
        recent_low = data['Low'].tail(20).min()
        current = data['Close'].iloc[-1]
        if current > recent_high:
            rec = "Breakout Buy"
        elif current < recent_low:
            rec = "Breakdown Sell"
        else:
            rec = "Hold"
        return f"S:{recent_low:.2f} R:{recent_high:.2f}", rec
    except:
        return "N/A", "N/A"

def compare_stocks():
    tickers = [entry1.get().strip().upper(), entry2.get().strip().upper(), entry3.get().strip().upper(), entry4.get().strip().upper(), entry5.get().strip().upper()]
    if not all(tickers):
        messagebox.showerror("Error", "Please enter all five ticker symbols.")
        return
    for i, ticker in enumerate(tickers):
        price = get_current_price(ticker)
        if price is not None:
            price_labels[i].config(text=f"Price: ${price:.2f}", foreground="black")
        else:
            price_labels[i].config(text="Price: N/A", foreground="black")

        pe_val, pe_rec = analyze_pe(ticker)
        pe_labels[i].config(text=f"P/E: {pe_val} ({pe_rec})", foreground=get_rec_color(pe_rec), image=get_rec_image(pe_rec), compound="left")

        eps_val, eps_rec = analyze_eps_growth(ticker)
        eps_labels[i].config(text=f"EPS Growth: {eps_val} ({eps_rec})", foreground=get_rec_color(eps_rec), image=get_rec_image(eps_rec), compound="left")

        de_val, de_rec = analyze_debt_to_equity(ticker)
        de_labels[i].config(text=f"D/E: {de_val} ({de_rec})", foreground=get_rec_color(de_rec), image=get_rec_image(de_rec), compound="left")

        rev_val, rev_rec = analyze_revenue_growth(ticker)
        rev_labels[i].config(text=f"Rev Growth: {rev_val} ({rev_rec})", foreground=get_rec_color(rev_rec), image=get_rec_image(rev_rec), compound="left")

        pm_val, pm_rec = analyze_profit_margins(ticker)
        pm_labels[i].config(text=f"Profit Margin: {pm_val} ({pm_rec})", foreground=get_rec_color(pm_rec), image=get_rec_image(pm_rec), compound="left")

        rsi_val, rsi_rec = analyze_rsi(ticker)
        rsi_labels[i].config(text=f"RSI: {rsi_val} ({rsi_rec})", foreground=get_rec_color(rsi_rec), image=get_rec_image(rsi_rec), compound="left")

        macd_val, macd_rec = analyze_macd(ticker)
        macd_labels[i].config(text=f"MACD: {macd_val} ({macd_rec})", foreground=get_rec_color(macd_rec), image=get_rec_image(macd_rec), compound="left")

        bb_val, bb_rec = analyze_bb(ticker)
        bb_labels[i].config(text=f"Bollinger: {bb_val} ({bb_rec})", foreground=get_rec_color(bb_rec), image=get_rec_image(bb_rec), compound="left")

        ma_val, ma_rec = analyze_ma(ticker)
        ma_labels[i].config(text=f"MA: {ma_val} ({ma_rec})", foreground=get_rec_color(ma_rec), image=get_rec_image(ma_rec), compound="left")

        vol_val, vol_rec = analyze_volume(ticker)
        vol_labels[i].config(text=f"Volume: {vol_val} ({vol_rec})", foreground=get_rec_color(vol_rec), image=get_rec_image(vol_rec), compound="left")

        stoch_val, stoch_rec = analyze_stoch(ticker)
        stoch_labels[i].config(text=f"Stochastic: {stoch_val} ({stoch_rec})", foreground=get_rec_color(stoch_rec), image=get_rec_image(stoch_rec), compound="left")

        adx_val, adx_rec = analyze_adx(ticker)
        adx_labels[i].config(text=f"ADX: {adx_val} ({adx_rec})", foreground=get_rec_color(adx_rec), image=get_rec_image(adx_rec), compound="left")

        atr_val, atr_rec = analyze_atr(ticker)
        atr_labels[i].config(text=f"ATR: {atr_val} ({atr_rec})", foreground=get_rec_color(atr_rec), image=get_rec_image(atr_rec), compound="left")

        obv_val, obv_rec = analyze_obv(ticker)
        obv_labels[i].config(text=f"OBV: {obv_val} ({obv_rec})", foreground=get_rec_color(obv_rec), image=get_rec_image(obv_rec), compound="left")

        ichi_val, ichi_rec = analyze_ichimoku(ticker)
        ichi_labels[i].config(text=f"Ichimoku: {ichi_val} ({ichi_rec})", foreground=get_rec_color(ichi_rec), image=get_rec_image(ichi_rec), compound="left")

        fib_val, fib_rec = analyze_fib(ticker)
        fib_labels[i].config(text=f"Fib: {fib_val} ({fib_rec})", foreground=get_rec_color(fib_rec), image=get_rec_image(fib_rec), compound="left")

        sr_val, sr_rec = analyze_sr(ticker)
        sr_labels[i].config(text=f"S/R: {sr_val} ({sr_rec})", foreground=get_rec_color(sr_rec), image=get_rec_image(sr_rec), compound="left")

def get_stock_data(ticker):
    data = {}
    data['price'] = get_current_price(ticker)
    data['pe'], data['pe_rec'] = analyze_pe(ticker)
    data['eps'], data['eps_rec'] = analyze_eps_growth(ticker)
    data['de'], data['de_rec'] = analyze_debt_to_equity(ticker)
    data['rev'], data['rev_rec'] = analyze_revenue_growth(ticker)
    data['pm'], data['pm_rec'] = analyze_profit_margins(ticker)
    data['rsi'], data['rsi_rec'] = analyze_rsi(ticker)
    data['macd'], data['macd_rec'] = analyze_macd(ticker)
    data['bb'], data['bb_rec'] = analyze_bb(ticker)
    data['ma'], data['ma_rec'] = analyze_ma(ticker)
    data['vol'], data['vol_rec'] = analyze_volume(ticker)
    data['stoch'], data['stoch_rec'] = analyze_stoch(ticker)
    data['adx'], data['adx_rec'] = analyze_adx(ticker)
    data['atr'], data['atr_rec'] = analyze_atr(ticker)
    data['obv'], data['obv_rec'] = analyze_obv(ticker)
    data['ichi'], data['ichi_rec'] = analyze_ichimoku(ticker)
    data['fib'], data['fib_rec'] = analyze_fib(ticker)
    data['sr'], data['sr_rec'] = analyze_sr(ticker)
    
    # Consolidated
    recs = [data['pe_rec'], data['eps_rec'], data['de_rec'], data['rev_rec'], data['pm_rec']]
    buy_count = recs.count("Buy")
    if buy_count > len(recs) // 2:
        data['consolidated'] = "BUY"
    else:
        data['consolidated'] = "SELL"
    
    return data

# Streamlit UI
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Stock Comparison Tool</h1>", unsafe_allow_html=True)

st.header("Enter Stock Tickers")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    ticker1 = st.text_input("Stock 1", value="AAPL", key="t1")
with col2:
    ticker2 = st.text_input("Stock 2", value="MSFT", key="t2")
with col3:
    ticker3 = st.text_input("Stock 3", value="GOOGL", key="t3")
with col4:
    ticker4 = st.text_input("Stock 4", value="AMZN", key="t4")
with col5:
    ticker5 = st.text_input("Stock 5", value="TSLA", key="t5")

if st.button("Compare Stocks"):
    tickers = [ticker1.strip().upper(), ticker2.strip().upper(), ticker3.strip().upper(), ticker4.strip().upper(), ticker5.strip().upper()]
    if not all(tickers):
        st.error("Please enter all five ticker symbols.")
    else:
        stock_data = []
        for ticker in tickers:
            data = get_stock_data(ticker)
            stock_data.append((ticker, data))
        
        # Build combined fundamentals table (all stocks side by side)
        st.markdown("### Fundamentals")
        fund_rows = []
        for ticker, data in stock_data:
            price_str = f"${data['price']:.2f}" if data['price'] else "N/A"
            fund_rows.append({
                "Stock": ticker,
                "Price": price_str,
                "P/E": f"{data['pe']} ({data['pe_rec']})",
                "EPS Growth": f"{data['eps']} ({data['eps_rec']})",
                "D/E": f"{data['de']} ({data['de_rec']})",
                "Rev Growth": f"{data['rev']} ({data['rev_rec']})",
                "Profit Margin": f"{data['pm']} ({data['pm_rec']})",
            })
        fund_df = pd.DataFrame(fund_rows)
        st.dataframe(fund_df, hide_index=True, width="stretch")

        # Build combined technicals table
        st.markdown("### Technical Indicators")
        tech_rows = []
        for ticker, data in stock_data:
            tech_rows.append({
                "Stock": ticker,
                "RSI": f"{data['rsi']} ({data['rsi_rec']})",
                "MACD": f"{data['macd']} ({data['macd_rec']})",
                "Bollinger": f"{data['bb']} ({data['bb_rec']})",
                "MA": f"{data['ma']} ({data['ma_rec']})",
                "Volume": f"{data['vol']} ({data['vol_rec']})",
                "Stochastic": f"{data['stoch']} ({data['stoch_rec']})",
                "ADX": f"{data['adx']} ({data['adx_rec']})",
                "ATR": f"{data['atr']} ({data['atr_rec']})",
                "OBV": f"{data['obv']} ({data['obv_rec']})",
                "Ichimoku": f"{data['ichi']} ({data['ichi_rec']})",
                "Fib": f"{data['fib']} ({data['fib_rec']})",
                "S/R": f"{data['sr']} ({data['sr_rec']})",
            })
        tech_df = pd.DataFrame(tech_rows)
        st.dataframe(tech_df, hide_index=True, width="stretch")

        # Consolidated recommendations
        st.markdown("### Consolidated Recommendation")
        for ticker, data in stock_data:
            consolidated_color = get_rec_color(data['consolidated'])
            st.markdown(f"**{ticker}: <span style='color:{consolidated_color}'>{data['consolidated']}</span>**", unsafe_allow_html=True)

# Claude AI Integration
st.header("Ask Claude AI about Stocks")
api_key = st.text_input("Enter your Anthropic API Key", type="password")
query = st.text_input("Ask a question about the stocks")
if st.button("Ask Claude"):
    if not api_key:
        st.error("Please enter your API key")
    elif not query:
        st.error("Please enter a question")
    else:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Prepare context from stock data
            context = "Stock Data:\n"
            for ticker, data in stock_data:
                context += f"{ticker}: Price ${data['price']}, P/E {data['pe']}, EPS {data['eps']}, D/E {data['de']}, Rev Growth {data['rev']}, Profit Margin {data['pm']}, RSI {data['rsi']}, MACD {data['macd']}, Bollinger {data['bb']}, MA {data['ma']}, Volume {data['vol']}, Stochastic {data['stoch']}, ADX {data['adx']}, ATR {data['atr']}, OBV {data['obv']}, Ichimoku {data['ichi']}, Fib {data['fib']}, S/R {data['sr']}, Consolidated {data['consolidated']}\n"
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": f"{context}\n\nQuestion: {query}"}
                ]
            )
            st.write("**Claude's Response:**")
            st.write(message.content[0].text)
        except Exception as e:
            st.error(f"Error: {str(e)}")