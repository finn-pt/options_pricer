import numpy as np
import yfinance as yf
import math

def binomial_price(S0: float, K: float, T: float, N: int, 
    sigma: float, r: float, call_or_put: str, option_type: str) -> float:
    """
    Determines the price of an option using the Cox,
    Ross and Rubenstein binomial model.

    Parameters:
    S0 (float): inital price in dollars
    K (float): strike price in dollars
    T (float): time to expiry in years
    N (int): number of steps
    sigma (float): annual volatility
    r (float): annual risk free rate of return
    call_or_put (str): denotes call or put
    option_type (str): denotes the type of the option

    Returns:
    price (float): price of the option in dollars
    """

    # Payoff function
    def payoff(S: float) -> float:
        """
        Determines the payoff at a node

        Parameters:
        S (float): current price

        Returns:
        payoff (float): the payoff at that node in dollars
        """
        if call_or_put == "Call":
            return max(0.0, S - K)
        elif call_or_put == "Put":
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

def Black_Scholes_price(S0: float, K: float, T: float, sigma: float, 
    r: float, call_or_put: str) -> float:
    """
    Determines the price of an option using the Black Scholes model.

    Parameters:
    S0 (float): inital price in dollars
    K (float): strike price in dollars
    T (float): time to expiry in years
    sigma (float): annual volatility
    r (float): annual risk free rate of return
    call_or_put (str): denotes call or put

    Returns:
    price (float): price of the option in dollars
    """

    # Normal cdf function
    def cdf(d: float) -> float:
        """
        Determines the probability that a standard normal distribution variable
        will be under a certain threshold

        Parameters:
        d (float): the threshold

        Returns (float): the probability it will be under the threshold
        """ 
        return (1.0 + math.erf(d / math.sqrt(2))) / 2.0

    # Discount rate per interval
    discount_rate: float = np.exp(-r * T)

    # Stock return standard deviation
    sd: float = sigma * np.sqrt(T)

    # d1 and d2
    d1: float = (np.log(S0 / K) + T * (r + sigma ** 2 / 2)) / sd
    d2: float = d1 - sd

    if call_or_put == "Call":
        return S0 * cdf(d1) - K * discount_rate * cdf(d2)
    if call_or_put == "Put":
        return K * discount_rate * cdf(-d2) - S0 * cdf(-d1)