import numpy as np
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

class OptionType(Enum):
    CALL = 1
    PUT = 2

class BarrierType(Enum):
    UP_AND_OUT = 1
    DOWN_AND_OUT = 2
    UP_AND_IN = 3
    DOWN_AND_IN = 4

# Parent Option class
class Option(ABC):
    def __init__(self, strike: float, maturity: float, option_type: OptionType):
        self.strike = strike
        self.maturity = maturity
        self.option_type = option_type

    @abstractmethod
    def payoff(self, price_path: np.ndarray) -> float:
        pass

# Child classes for specific option types
class EuropeanOption(Option):
    def payoff(self, price_path: np.ndarray) -> float:
        if len(price_path) == 0:
            raise ValueError("Price path cannot be empty.")

        final_price = price_path[-1]

        if self.option_type == OptionType.CALL:
            return max(final_price - self.strike, 0.0)
        elif self.option_type == OptionType.PUT:
            return max(self.strike - final_price, 0.0)
        else:
            raise ValueError("Invalid option type")

class AsianOption(Option):
    """
    Asian Option: Payoff is based on the average price over the path.
    """
    def payoff(self, price_path: np.ndarray) -> float:
        if len(price_path) == 0:
            raise ValueError("Price path cannot be empty.")

        average_price = np.mean(price_path)

        if self.option_type == OptionType.CALL:
            return max(average_price - self.strike, 0.0)
        elif self.option_type == OptionType.PUT:
            return max(self.strike - average_price, 0.0)
        else:
            raise ValueError("Invalid option type")

class BarrierOption(Option):
    """
    Barrier Option: Payoff depends on whether the underlying asset's price reaches a certain barrier level.
    """
    def __init__(self, strike: float, maturity: float, option_type: OptionType, barrier: float, barrier_type: BarrierType):
        super().__init__(strike, maturity, option_type)
        self.barrier = barrier
        self.barrier_type = barrier_type

    def payoff(self, price_path: np.ndarray) -> float:
        if len(price_path) == 0:
            raise ValueError("Price path cannot be empty.")

        if self.barrier_type == BarrierType.UP_AND_OUT:
            if np.any(price_path >= self.barrier):
                return 0.0
            
        elif self.barrier_type == BarrierType.DOWN_AND_OUT:
            if np.any(price_path <= self.barrier):
                return 0.0

        # If it survives the barrier, it pays out like a European Option
        final_price = price_path[-1]
        if self.option_type == OptionType.CALL:
            return max(final_price - self.strike, 0.0)

        elif self.option_type == OptionType.PUT:
            return max(self.strike - final_price, 0.0)

        else:
            raise ValueError("Invalid option type")


if __name__ == "__main__":
    print("--- Advanced Derivatives Pricing Library: Python OOP ---")
    
    # Portfolio of different options
    portfolio: List[Option] = [
        EuropeanOption(strike=100.0, maturity=1.0, option_type=OptionType.CALL),
        AsianOption(strike=100.0, maturity=1.0, option_type=OptionType.CALL),
        BarrierOption(strike=100.0, maturity=1.0, option_type=OptionType.CALL, barrier=120.0, barrier_type=BarrierType.UP_AND_OUT)
    ]

    # Simulated asset price path (e.g., generated via Monte Carlo)
    # NumPy arrays are standard for quantitative finance data
    simulated_path = np.array([95.0, 102.0, 108.0, 115.0, 105.0, 110.0])
    
    print(f"\nSimulated Price Path: {simulated_path}")
    print("\nCalculating Payoffs (Polymorphism in action):")
    
    for i, option in enumerate(portfolio):
        # We don't need to check the option type (European vs Asian). 
        # Python's dynamic dispatch calls the correct .payoff() method automatically.
        p = option.payoff(simulated_path)
        print(f"Option {i + 1} ({option.__class__.__name__}) Payoff: ${p:.2f}")