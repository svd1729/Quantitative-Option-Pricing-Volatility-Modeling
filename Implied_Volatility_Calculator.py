from typing import Optional
import time

try:
    from black_scholes import BlackScholesPricer, EuropeanOption, OptionType
except ImportError:
    print("Warning: black_scholes.py not found. Ensure it is in the same directory.")
    pass

class ImpliedVolatilityCalculator:
    """
    Calculates the implied volatility of a European option given its market price
    using the Newton-Raphson root-finding method.
    """
    def __init__(self, spot: float, rate: float, dividend_yield: float = 0.0):
        self.S = spot
        self.r = rate
        self.q = dividend_yield

    def newton_raphson(self, 
                       option: EuropeanOption, 
                       market_price: float, 
                       initial_guess: float = 0.2, 
                       tolerance: float = 1e-6, 
                       max_iter: int = 100) -> Optional[float]:
        """
        Uses the Newton-Raphson method to find the implied volatility.

        Formula: sigma_{n+1} = sigma_n - (BS_Price(sigma_n) - Market_Price) / Vega(sigma_n)
        """
        # Ensure Market price is logically sound
        intrinsic_value = max(0, self.S - option.strike) if option.option_type == OptionType.CALL else max(0, option.strike - self.S)
        if market_price < intrinsic_value:
            print("Market price is below intrinsic value. Implied volatility may not be meaningful.")
            return None

        sigma = initial_guess

        for i in range(max_iter):
            pricer = BlackScholesPricer(spot=self.S, rate=self.r, volatility=sigma, dividend_yield=self.q)
            price = pricer.price(option)
            vega = pricer.vega(option)

            if abs(vega) < 1e-8:
                print(f"Warning: Vega approaching zero at iteration {i}. Newton-Raphson stalled.")
                return None

            price_diff = price - market_price
            if abs(price_diff) < tolerance:
                return sigma

            sigma -= price_diff / vega

            # Ensure sigma remains positive
            if sigma <= 0:
                print("Sigma became non-positive. Stopping iteration.")
                return None

        print("Max iterations reached without convergence.")
        return None


if __name__ == "__main__":
    print("--- Implied Volatility Calculator ---")

    s0 = 150.0
    r = 0.05
    call_option = EuropeanOption(strike=155.0, maturity=0.5, option_type=OptionType.CALL)
    market_price = 8.5

    print(f"\n[ Market Data ]")
    print(f"Spot: ${s0} | Strike: ${call_option.strike} | Expiry: {call_option.maturity}yr | Rate: {r*100}%")
    print(f"Observed Market Price: ${market_price}")

    # Initialize the implied volatility calculator
    iv_calc = ImpliedVolatilityCalculator(spot=s0, rate=r)

    # Calculate implied volatility
    start_time = time.time()
    implied_vol = iv_calc.newton_raphson(option=call_option, market_price=market_price)
    end_time = time.time()

    if implied_vol is not None:
        print(f"\n[ Result ]")
        print(f"Calculated Implied Volatility: {implied_vol * 100:.2f}%")
        print(f"Calculation Time: {(end_time - start_time) * 1000:.2f} milliseconds")
        
        # Verify it works by plugging it back into the pricer
        verify_pricer = BlackScholesPricer(spot=s0, rate=r, volatility=implied_vol)
        verify_price = verify_pricer.price(call_option)
        print(f"\n[ Verification ]")
        print(f"Plugging {implied_vol * 100:.2f}% Vol back into Black-Scholes yields: ${verify_price:.4f}")
        print(f"Error vs Market Price: ${abs(verify_price - market_price):.6f}")
    else:
        print("Failed to calculate implied volatility.")