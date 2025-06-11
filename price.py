import numpy as np
import yfinance as yf

def binomial_price(S0: float, K: float, T: float, N: int, 
    sigma: float, call_or_put: str, option_type: str) -> float:
    """
    Determines the price of an option using the Cox, 
    Ross and Rubenstein binomial model.

    Parameters:
    S0 (float): inital price in dollars
    K (float): strike price in dollars
    T (float): time to expiry in years
    N (int): number of steps
    sigma (float): annual volatility
    call_or_put (str): denotes call or put
    option_type (str): denotes the type of the option

    Returns:
    price (float): price of the option in dollars
    """
    # Calculate risk free rate of return based on treasury bills
    r: float = yf.Ticker("^IRX").history(period="5d").Close.iloc[-1]
    r = r / 100
    r = np.log1p(r)

    # Payoff function
    def payoff(S: float) -> float:
        """
        Determines the payoff at a node

        Parameters:
        S (float): current price

        Returns:
        payoff (float): the payoff at that node in dollars
        """
        if call_or_put == "call":
            return max(0.0, S - K)
        elif call_or_put == "put":
            return max(0.0, K - S)

    # Interval length in years
    interval_length: float = T / N

    # Discount rate per interval
    discount_rate: float = np.exp(-r * interval_length)

    # Up and down factors
    up: float = np.exp(sigma * np.sqrt(interval_length))
    down: float = 1 / up

    # Arbitrage free probability of moving up and down
    p_up: float = (np.exp(interval_length * r) - down) / (up - down)
    p_down: float = 1 - p_up

    # Building stock price tree
    stock_prices = [S0 * (up ** ups) * (down 
        ** (N - ups)) for ups in range(N + 1)]

    # Building payoffs array
    payoffs = np.array([payoff(S) for S in stock_prices], dtype = float)

    # Backwards induction
    for step in range(N - 1, -1, -1):
        payoffs = (p_up * payoffs[1:] + p_down * payoffs[:-1])* discount_rate
        if option_type == "American":
            step_stock_prices = [S0 * (up ** ups) * (down ** 
                (step - ups)) for ups in range(step + 1)]
            exercise_payoffs = np.array([payoff(S) for S in 
                step_stock_prices], dtype = float)
            payoffs = np.maximum(payoffs, exercise_payoffs)
    return float(payoffs[0])
