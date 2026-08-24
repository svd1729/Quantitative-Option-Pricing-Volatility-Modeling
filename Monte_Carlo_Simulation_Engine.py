import numpy as np
import time
from typing import Optional

# We import the Option classes from Options_architecture.py
try:
    from Options_architecture import Option, EuropeanOption, AsianOption, BarrierOption, OptionType, BarrierType
except ImportError as exc:
    raise ImportError(
        "Could not import Option classes. Please ensure Options_architecture.py is in the same directory."
    ) from exc

class MonteCarloPricer:
    """
    A highly vectorized Monte Carlo simulation engine for pricing financial derivatives.
    """
    def __init__(self, spot: float, rate: float, volatility: float, dividend_yield: float = 0.0):
        self.S = spot             # S_0 : Initial spot price
        self.r = rate             # r : Risk-free interest rate
        self.sigma = volatility   # sigma : Implied volatility
        self.q = dividend_yield   # q : Continuous dividend yield

    def simulate_paths(self, maturity: float, num_paths: int, num_steps: int, antithetic: bool = False, seed: Optional[int] = None) -> np.ndarray:
        """
        Simulate asset price paths using the Geometric Brownian Motion model(GBM).

        Parameters:
        - maturity: Time to maturity(T) in years.
        - num_paths: Number of simulation paths(M).
        - num_steps: Number of time steps in each path(N).
        - antithetic: Whether to use antithetic variates for variance reduction.
        - seed: Optional random seed for reproducibility.

        Returns:
        - A 2D numpy array of simulated asset prices with shape (num_paths, num_steps + 1).
        """
        if seed is not None:
            np.random.seed(seed)

        if maturity <= 0.0:
            return np.full((num_paths, 1), self.S)  # Return initial spot price if maturity is zero or negative
        
        dt = maturity / num_steps
        # Precompute constants for efficiency
        drift = (self.r - self.q - 0.5 * self.sigma ** 2) * dt
        diffusion = self.sigma * np.sqrt(dt)

        # Generate random normal variables for the simulation
        if antithetic:
            Z = np.random.standard_normal((num_paths // 2, num_steps))
            Z = np.vstack([Z, -Z])

            if num_paths % 2 != 0:
                z_extra = np.random.standard_normal((1, num_steps))
                Z = np.vstack([Z, z_extra])  # Add an extra path if num
        else:
            Z = np.random.standard_normal((num_paths, num_steps))

        # Calculate the log returns for all paths and all time steps
        log_returns = drift + diffusion * Z

        # Cumulative sum of log returns to get the log of asset prices
        cumulative_log_returns = np.cumsum(log_returns, axis=1)
        zero_column = np.zeros((num_paths, 1))  # Initial log price (log(S_0))
        cumulative_log_returns = np.hstack((zero_column, cumulative_log_returns))  # Add initial log price to the beginning of each path

        # Calculate the actual price paths.
        price_paths = self.S * np.exp(cumulative_log_returns)

        return price_paths

    def price(self, option: Option, num_paths: int = 10000, num_steps: int = 252, antithetic: bool = False, seed: Optional[int] = None) -> float:
        """
        Price a given option contract using Monte Carlo simulation.
        """
        if option.maturity <= 0.0:
            # If the option has expired, return the intrinsic value
            return option.payoff(np.array([[self.S]]))[0]
        
        # start_time = time.time()

        # Simulate asset price paths
        price_paths = self.simulate_paths(option.maturity, num_paths, num_steps, antithetic=antithetic, seed=seed)

        # Calculate the payoff for each path
        payoffs = np.array([option.payoff(path) for path in price_paths])

        # Expected payoff
        expected_payoff = np.mean(payoffs)
        
        # Discount the average payoff back to present value
        discounted_payoff = np.exp(-self.r * option.maturity) * expected_payoff

        # end_time = time.time()
        # print(f"Monte Carlo simulation completed in {end_time - start_time:.4f} seconds.")

        return discounted_payoff



if __name__ == "__main__":
    print("--- Monte Carlo Simulation Engine ---")

    # Market Environment
    S0 = 100.0
    r = 0.05
    sigma = 0.20

    engine = MonteCarloPricer(spot=S0, rate=r, volatility=sigma)

    # Define some options
    maturity = 1.0
    strike = 105.0

    eur_call = EuropeanOption(strike, maturity, OptionType.CALL)
    asian_call = AsianOption(strike, maturity, OptionType.CALL)

    # Up-and-out barrier option: Knocked out if price hits 120
    barrier_call = BarrierOption(strike, maturity, OptionType.CALL, barrier=120.0, barrier_type=BarrierType.UP_AND_OUT)

    # Simulation Parameters
    num_paths = 50000 # Increase this for more accuracy, decrease for speed
    num_steps = 252   # Approximate number of trading days in a year
    antithetic = True  # Use antithetic variates for variance reduction

    print(f"\nMarket: Spot=${S0:.2f}, Rate={r*100}%, Volatility={sigma*100}%")
    print(f"Simulating {num_paths:,} paths with {num_steps} steps per path...")

    start_time = time.time()

    # Price the options
    price_eur = engine.price(eur_call, num_paths, num_steps, antithetic=antithetic)
    price_asian = engine.price(asian_call, num_paths, num_steps, antithetic=antithetic)
    price_barrier = engine.price(barrier_call, num_paths, num_steps, antithetic=antithetic)

    end_time = time.time()

    print(f"\n[ Pricing Results (Monte Carlo) ]")
    print(f"European Call:      ${price_eur:.4f}")
    print(f"Asian Call:         ${price_asian:.4f}")
    print(f"Barrier (U&O) Call: ${price_barrier:.4f}")
    print(f"\nSimulation Time: {end_time - start_time:.4f} seconds")

    # Compare with Analytical Black-Scholes
    try:
        from black_scholes import BlackScholesPricer
        bs_pricer = BlackScholesPricer(spot=S0, rate=r, volatility=sigma)
        bs_price = bs_pricer.price(eur_call)
        print(f"\n[ Validation ]")
        print(f"Analytical BS Price for European Call: ${bs_price:.4f}")
        print(f"Monte Carlo Error: ${abs(price_eur - bs_price):.6f}")
    except ImportError:
        print("Black-Scholes module not available for validation.")