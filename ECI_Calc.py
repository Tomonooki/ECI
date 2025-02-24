# ECI_3_streamlit.py

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# ----------------------------- #
#          Login Module          #
# ----------------------------- #

def login():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state.logged_in:
        st.title("Login")
        password_input = st.text_input("Enter Password:", type="password")
        if st.button("Login"):
            if password_input == "Bitcoin99!":
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Incorrect password!")
        st.stop()

# ----------------------------- #
#         Helper Functions       #
# ----------------------------- #

def fetch_btc_price():
    """
    Fetches the current BTC price in USD (using USDT as a proxy) from Binance.
    """
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            st.error("Failed to fetch BTC price. Please check your internet connection.")
            return None
        data = response.json()
        # Expected response: {"symbol": "BTCUSDT", "price": "xxxx.xx"}
        current_price = float(data.get("price", 0))
        if current_price == 0:
            st.error("Received invalid BTC price from Binance.")
            return None
        return current_price
    except Exception as e:
        st.error(f"Error fetching BTC price: {e}")
        return None

def calculate_annual_payment(loan_amount, annual_rate, years):
    """
    Calculates the fixed annual loan payment using the annuity formula.
    """
    payment = loan_amount * (annual_rate * (1 + annual_rate) ** years) / ((1 + annual_rate) ** years - 1)
    return payment

def generate_loan_schedule(loan_amount, annual_rate, annual_payment, years):
    """
    Generates the loan schedule showing interest, principal repayment, and remaining balance each year.
    """
    schedule = []
    remaining_balance = loan_amount
    for year in range(1, years + 1):
        interest = remaining_balance * annual_rate
        principal = annual_payment - interest
        remaining_balance -= principal
        schedule.append({
            'Year': year,
            'Payment': round(annual_payment, 2),
            'Interest': round(interest, 2),
            'Principal': round(principal, 2),
            'Remaining Balance': round(remaining_balance, 2)
        })
    return schedule

def plot_loan_schedule(schedule_df):
    """
    Plots the loan payment breakdown over the years using Plotly.
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=schedule_df['Year'],
        y=schedule_df['Interest'],
        name='Interest',
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=schedule_df['Year'],
        y=schedule_df['Principal'],
        name='Principal',
        marker_color='lightsalmon'
    ))
    fig.update_layout(
        barmode='stack',
        title='Loan Payment Breakdown by Year',
        xaxis_title='Year',
        yaxis_title='Amount (USD)',
        legend_title='Components',
        template='plotly_white'
    )
    return fig

def plot_ecis_profit(profit_percentage):
    """
    Plots ECi's profit as a single bar using Plotly.
    """
    fig = go.Figure(go.Bar(
        x=['ECi Profit'],
        y=[profit_percentage],
        marker_color='green' if profit_percentage > 0 else 'red'
    ))
    fig.update_layout(
        title="ECi's Profit Percentage",
        yaxis_title='Profit (%)',
        xaxis=dict(showticklabels=False),
        showlegend=False,
        template='plotly_white',
        height=400
    )
    fig.update_traces(text=[f"{profit_percentage}%" if profit_percentage > 0 else f"{profit_percentage}%"], textposition='auto')
    return fig

def plot_investors_net_benefit(years, net_benefit):
    """
    Plots the investor's net benefit over time using Plotly.
    """
    fig = go.Figure(go.Scatter(
        x=years,
        y=net_benefit,
        mode='lines+markers',
        name='Net Benefit',
        line=dict(color='purple', width=2)
    ))
    fig.update_layout(
        title="Investor's Net Benefit Over Time",
        xaxis_title='Year',
        yaxis_title='Net Benefit (USD)',
        template='plotly_white',
        height=500
    )
    return fig

# ----------------------------- #
#          Streamlit App         #
# ----------------------------- #

def main():
    # Run the login check before displaying the app
    login()

    st.set_page_config(page_title="ECi Condo Loan Calculator", layout="centered")
    st.title("🏢 ECi Condo Loan Calculator 🏦")
    st.markdown("""
        This application helps you determine whether purchasing a condo using your BTC holdings is financially viable. 
        If accepted, it provides a detailed loan schedule, ECi's profit, and your net benefits from the deal.
    """)

    # Fetch current BTC price from Binance
    btc_price = fetch_btc_price()
    if btc_price:
        st.sidebar.header("Current BTC Price")
        st.sidebar.metric(label="BTC Price (USD)", value=f"${btc_price:,.2f}")

    # User Inputs
    st.header("🔍 Input Parameters")
    btc_amount = st.number_input("Enter the number of BTC you hold:", min_value=0.0, value=50.0, step=0.01)
    condo_price = st.number_input("Enter the price of the condo in USD:", min_value=0.0, value=1000000.0, step=1000.0)

    # Calculate initial BTC value
    V0 = btc_amount * btc_price if btc_price else 0.0

    # Define constraint
    max_condo_cost = 0.25 * V0

    # Button to evaluate
    if st.button("Evaluate Deal"):
        if btc_price is None or btc_price == 0.0:
            st.error("BTC price not available. Please check your internet connection.")
            return

        # Validation
        if condo_price <= max_condo_cost:
            st.success("✅ **Deal Accepted:**")
            
            # Loan Details
            DP = 0.25 * condo_price  # Down Payment
            L = 0.75 * condo_price   # Loan Amount
            annual_interest_rate = 0.10  # 10%
            loan_term_years = 4  # 4 years
            CAGR = 0.281  # 28.1% annual growth rate for BTC

            # Calculate annual loan payment
            A = calculate_annual_payment(L, annual_interest_rate, loan_term_years)
            A = round(A, 2)

            # Display Loan Details
            st.subheader("💼 Loan Details")
            loan_details = {
                "Down Payment (25% of Condo Price)": f"${DP:,.2f}",
                "Loan Amount (75% of Condo Price)": f"${L:,.2f}",
                "Annual Interest Rate": f"{annual_interest_rate*100:.2f}%",
                "Loan Term (Years)": loan_term_years,
                "Annual Loan Payment": f"${A:,.2f}"
            }
            loan_details_df = pd.DataFrame.from_dict(loan_details, orient='index', columns=['Value'])
            st.table(loan_details_df)

            # Generate and Display Loan Schedule
            schedule = generate_loan_schedule(L, annual_interest_rate, A, loan_term_years)
            schedule_df = pd.DataFrame(schedule)
            st.subheader("📅 Loan Schedule")
            st.plotly_chart(plot_loan_schedule(schedule_df), use_container_width=True)
            st.dataframe(schedule_df.style.format({"Payment": "${:,.2f}", "Interest": "${:,.2f}", 
                                                   "Principal": "${:,.2f}", "Remaining Balance": "${:,.2f}"}))
            
            # Calculate ECi's Profit
            total_payments = DP + (A * loan_term_years)
            profit = total_payments - condo_price
            profit_percentage = (profit / condo_price) * 100
            profit_percentage = round(profit_percentage, 2)

            # Display ECi's Profit
            st.subheader("📈 ECi's Profit")
            st.plotly_chart(plot_ecis_profit(profit_percentage), use_container_width=True)
            st.write(f"**Total Payments to ECi:** ${total_payments:,.2f}")
            st.write(f"**ECi's Profit:** ${profit:,.2f} ({profit_percentage}%)")

            # Calculate Investor's Net Benefit
            final_btc_value = V0 * (1 + CAGR) ** loan_term_years
            final_condo_value = condo_price * (1 + 0.04) ** loan_term_years  # Assuming 4% annual appreciation
            investors_net_benefit = final_btc_value + final_condo_value

            # Prepare Net Benefit Over Time
            years = list(range(0, loan_term_years + 1))
            btc_values = [V0 * (1 + CAGR) ** year for year in years]
            condo_values = [condo_price * (1 + 0.04) ** year for year in years]
            net_benefit = [btc + condo for btc, condo in zip(btc_values, condo_values)]

            # Display Investor's Net Benefit
            st.subheader("💰 Investor's Net Benefit")
            st.plotly_chart(plot_investors_net_benefit(years, net_benefit), use_container_width=True)
            st.write(f"**Final BTC Value (after {loan_term_years} years):** ${final_btc_value:,.2f}")
            st.write(f"**Final Condo Value (after {loan_term_years} years at 4% appreciation):** ${final_condo_value:,.2f}")
            st.write(f"**Total Net Benefit:** ${investors_net_benefit:,.2f}")

        else:
            st.error("❌ **Deal Not Accepted:** constraint.")
            st.write(f"**Maximum Allowed Condo Cost vs BTC Holdings' Value:** ${max_condo_cost:,.2f}")
            st.write(f"**Your Condo Price:** ${condo_price:,.2f}")
            st.write("**Please adjust your condo price to meet the investment constraints and try again.**")

if __name__ == "__main__":
    main()
