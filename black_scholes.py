import numpy as np
from scipy.stats import norm
import math
from Options_architecture import EuropeanOption, OptionType

class BlackScholesPricer:
    """
    Analytical pricing engine for European Options using the Black-Scholes-Merton model.
    """
    def __init__(self, spot: float, rate: float, volatility: float, dividend_yield: float = 0.0):
        self.S = spot             # S_0 : Initial spot price
        self.r = rate             # r : Risk-free interest rate
        self.sigma = volatility   # sigma : Implied volatility
        self.q = dividend_yield   # q : Continuous dividend yield

    def _d1(self, k: float, T: float) -> float:
        if T <= 0.0:
            raise ValueError("Time to maturity must be positive for d1 calculation.")

        numerator = math.log(self.S / k) + (self.r - self.q + 0.5 * self.sigma ** 2) * T
        denominator = self.sigma * math.sqrt(T)
        
        return numerator / denominator

    def _d2(self, k: float, T: float) -> float:
        if T <= 0.0:
            raise ValueError("Time to maturity must be positive for d2 calculation.")

        numerator = math.log(self.S / k) + (self.r - self.q - 0.5 * self.sigma ** 2) * T
        denominator = self.sigma * math.sqrt(T)

        return numerator / denominator

    def price(self, option: EuropeanOption) -> float:
        """
        Calculates the theoretical fair value of the European option.
        """
        k = option.strike
        T = option.maturity

        # Handle expired options (Intrinsic value only)
        if T <= 0.0:
            if option.option_type == OptionType.CALL:
                return max(self.S - k, 0.0)
            else:
                return max(k - self.S, 0.0)

        d1 = self._d1(k, T)
        d2 = self._d2(k, T)

        if option.option_type == OptionType.CALL:
            price = self.S * math.exp(-self.q * T) * norm.cdf(d1) - k * math.exp(-self.r * T) * norm.cdf(d2)
        else:
            price = k * math.exp(-self.r * T) * norm.cdf(-d2) - self.S * math.exp(-self.q * T) * norm.cdf(-d1)

        return price

    def delta(self, option: EuropeanOption) -> float:
        """
        Rate of change of the option price with respect to changes in the underlying asset's price.
        """
        k = option.strike
        T = option.maturity

        if T <= 0.0:
            if option.option_type == OptionType.CALL:
                return 1.0 if self.S > k else 0.0
            else:
                return -1.0 if self.S < k else 0.0

        d1 = self._d1(k, T)

        if option.option_type == OptionType.CALL:
            return math.exp(-self.q * T) * norm.cdf(d1)
        else:
            return math.exp(-self.q * T) * (norm.cdf(d1) - 1)

    def gamma(self, option: EuropeanOption) -> float:
        """
        Rate of change of delta with respect to changes in the underlying asset's price.
        """
        k = option.strike
        T = option.maturity

        if T <= 0.0:
            return 0.0  # Gamma is undefined for expired options

        d1 = self._d1(k, T)
        return (math.exp(-self.q * T) * norm.pdf(d1)) / (self.S * self.sigma * math.sqrt(T))

    def vega(self, option: EuropeanOption) -> float:
        """
        Rate of change of the option price with respect to changes in volatility.
        """
        k = option.strike
        T = option.maturity

        if T <= 0.0:
            return 0.0  # Vega is undefined for expired options

        d1 = self._d1(k, T)
        return self.S * math.exp(-self.q * T) * norm.pdf(d1) * math.sqrt(T)

    def theta(self, option: EuropeanOption) -> float:
        """
        Rate of change of the option price with respect to time (time decay).
        """
        k = option.strike
        T = option.maturity

        if T <= 0.0:
            return 0.0  # Theta is undefined for expired options

        d1 = self._d1(k, T)
        d2 = self._d2(k, T)

        if option.option_type == OptionType.CALL:
            theta = (-self.S * norm.pdf(d1) * self.sigma * math.exp(-self.q * T) / (2 * math.sqrt(T))
                     - self.r * k * math.exp(-self.r * T) * norm.cdf(d2)
                     + self.q * self.S * math.exp(-self.q * T) * norm.cdf(d1))
        else:
            theta = (-self.S * norm.pdf(d1) * self.sigma * math.exp(-self.q * T) / (2 * math.sqrt(T))
                     + self.r * k * math.exp(-self.r * T) * norm.cdf(-d2)
                     - self.q * self.S * math.exp(-self.q * T) * norm.cdf(-d1))

        return theta

if __name__ == "__main__":
    print("--- Black-Scholes Pricer & Greeks Engine ---")
    
    # Let's price a 1-year European Call option
    # Underlying Spot = $100, Strike = $105, Maturity = 1 Year
    call_option = EuropeanOption(strike=105.0, maturity=1.0, option_type=OptionType.CALL)
    put_option = EuropeanOption(strike=105.0, maturity=1.0, option_type=OptionType.PUT)
    
    # Market Conditions: Spot=$100, Risk-Free Rate=5%, Volatility=20%
    pricer = BlackScholesPricer(spot=100.0, rate=0.05, volatility=0.20)
    
    print("\n[ Market Conditions ]")
    print(f"Spot Price (S): ${pricer.S:.2f} | Risk-Free Rate (r): {pricer.r*100}% | Volatility (sigma): {pricer.sigma*100}%")
    
    print("\n[ Option Specifics ]")
    print(f"Strike (K): ${call_option.strike:.2f} | Time to Maturity (T): {call_option.maturity} Year(s)")
    
    print("\n" + "="*45)
    print(f"{'Metric':<15} | {'Call Option':<12} | {'Put Option':<12}")
    print("="*45)
    
    # Print Price
    c_price, p_price = pricer.price(call_option), pricer.price(put_option)
    print(f"{'Fair Value':<15} | ${c_price:<11.4f} | ${p_price:<11.4f}")

    # Print Greeks
    c_delta, p_delta = pricer.delta(call_option), pricer.delta(put_option)
    c_gamma, p_gamma = pricer.gamma(call_option), pricer.gamma(put_option)
    c_vega, p_vega = pricer.vega(call_option), pricer.vega(put_option)
    c_theta, p_theta = pricer.theta(call_option), pricer.theta(put_option)
    print(f"{'Delta':<15} | ${c_delta:<11.4f} | ${p_delta:<11.4f}")
    print(f"{'Gamma':<15} | ${c_gamma:<11.4f} | ${p_gamma:<11.4f}")
    print(f"{'Vega':<15} | ${c_vega:<11.4f} | ${p_vega:<11.4f}")
    print(f"{'Theta':<15} | ${c_theta:<11.4f} | ${p_theta:<11.4f}")