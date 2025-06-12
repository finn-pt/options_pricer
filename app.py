import streamlit as st
import yfinance as yf
import numpy as np
from price import binomial_price, Black_Scholes_price, Monte_Carlo_price

st.set_page_config(page_title="Option Pricer", 
    layout="centered")
st.title("Option Pricer")
if "stock_price" not in st.session_state:
    st.session_state.stock_price: None | float = None
if "model" not in st.session_state:
    st.session_state.model: None | float = None

inputted_model = st.selectbox("Evaluation Model", ["Binomial CRR", 
    "Black Scholes", "Monte Carlo"], index = 0)

if st.button("Choose Stock"):
    st.session_state.model = inputted_model

if st.session_state.model != None:
    inputted_ticker: str = st.text_input("Enter the desired ticker:")
    if st.button("Enter Option Parameters"):
        try:
            ticker = yf.Ticker(inputted_ticker.upper())
            stock_info = ticker.info
            st.session_state.stock_price = float(
                stock_info.get("currentPrice",
                stock_info.get("regularMarketPrice",
                stock_info.get("regularMarketPreviousClose"))))
        except Exception as e:
            st.error(f"Could not find ticker. Error: {e}")
        # Volatility
        price_data = yf.download(inputted_ticker, period = "1y", 
            auto_adjust = False)["Close"]
        stock_log_returns = np.log(price_data / price_data.shift(1)).dropna()
        daily_sigma = stock_log_returns.std()
        st.session_state.sigma = float(daily_sigma * np.sqrt(252))
        # Calculate risk free rate of return based on treasury bills
        r: float = yf.Ticker("^IRX").history(period="5d").Close.iloc[-1]
        r = r / 100
        st.session_state.r = np.log1p(r)

if (st.session_state.stock_price != None and
    st.session_state.model in ("Binomial CRR", "Black Scholes")):
    st.write(f"Current Price: {st.session_state.stock_price}")
    K = st.slider("Strike Price (K)", min_value = st.session_state.stock_price 
        / 5, max_value = st.session_state.stock_price * 2, 
        value = st.session_state.stock_price, step = 0.1)
    T = st.slider("Time to Maturity (years)", min_value = 1/252, 
        max_value = 10.0, value=1.0, step = 1 / 252)
    if st.session_state.model != "Black Scholes":
        N = st.slider("Steps", min_value=1, max_value = 500, value=1, step = 1)
    call_or_put = st.selectbox("Option Type", ["Call", "Put"], index = 0)
    if st.session_state.model == "Binomial CRR":
        option_type = st.selectbox("Option Style", ["European", "American"], 
            index = 0)
    if st.session_state.model == "Binomial CRR":
        st.write(f"Option price: {binomial_price(st.session_state.stock_price, 
            K, T, N, st.session_state.sigma, st.session_state.r, 
            call_or_put, option_type):.4f}")
    if st.session_state.model == "Black Scholes":
        st.write(f"Option price: {Black_Scholes_price(
            st.session_state.stock_price, K, T, st.session_state.sigma, 
            st.session_state.r, call_or_put):.4f}")
    if st.button("Try a different stock or option type"):
        st.session_state.clear()
elif (st.session_state.stock_price != None and 
    st.session_state.model == "Monte Carlo"):
    st.write(f"Current Price: {st.session_state.stock_price}")
    with st.form(key = "Monte Carlo Option Pricer"):
        K = st.slider("Strike Price (K)", min_value = 
            st.session_state.stock_price 
            / 5, max_value = st.session_state.stock_price * 2, 
            value = st.session_state.stock_price, step = 0.1)
        T = st.slider("Time to Maturity (years)", min_value = 1/252, 
            max_value = 10.0, value=1.0, step = 1 / 252)
        N = st.slider("Steps", min_value=5, max_value = 500, value=5, step = 1)
        simulations = st.slider("Simulations", min_value=1, max_value = 10000, 
            value=1, step = 1)
        call_or_put = st.selectbox("Option Type", ["Call", "Put"], index = 0)
        option_type = st.selectbox("Option Style", ["European", "Lookback", 
                "Asian"], index = 0)
        submit = st.form_submit_button(label="Simulate Price")
    if submit:
        #if "MC_option_price" not in st.session_state:
        st.session_state.MC_option_price = Monte_Carlo_price(
            st.session_state.stock_price, 
            K, T, N, st.session_state.sigma, st.session_state.r, 
            simulations, call_or_put, option_type)
        st.write(f"Option price: {st.session_state.MC_option_price:.4f}")
    if st.button("Try a different stock or option type"):
        st.session_state.clear()
