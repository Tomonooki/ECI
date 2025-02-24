import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

###############################
#       HELPER FUNCTIONS      #
###############################

@st.cache_data  # <-- Use st.cache_data here
def fetch_btc_price():
    """
    Fetches the current BTC price in USD. First tries Binance, then falls back to yfinance if Binance fails.
    The result is cached so we don't hit the API on every rerun.
    """
    # Try Binance first
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_price = float(data.get("price", 0))
            if current_price != 0:
                return current_price
            else:
                st.warning("Binance returned an invalid BTC price. Trying yfinance...")
        else:
            st.warning(f"Binance API returned non-200 status: {response.status_code}. Trying yfinance...")
    except Exception as e:
        st.warning(f"Binance API failed with error: {e}. Trying yfinance...")

    # Fallback to yfinance
    try:
        btc = yf.Ticker("BTC-USD")
        data = btc.history(period="1d")
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            return float(current_price)
        else:
            st.error("yfinance returned empty data.")
    except Exception as e:
        st.error(f"Error fetching BTC price from yfinance: {e}")

    return None

###############################
#       STREAMLIT APP         #
###############################

def main():
    st.title("BTC Price Example")

    if st.button("Get BTC Price"):
        btc_price = fetch_btc_price()
        if btc_price is not None:
            st.write(f"Current BTC Price: ${btc_price:,.2f}")
        else:
            st.error("Could not fetch BTC price.")

if __name__ == "__main__":
    main()
