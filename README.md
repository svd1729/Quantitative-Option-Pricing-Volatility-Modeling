# Quantitative Option Pricing & Volatility Modeling

A Python-based quantitative finance project implementing analytical and numerical methods for European option pricing, implied volatility estimation, and market validation.

## Overview

This project develops an option pricing framework using:

- Black-Scholes-Merton analytical pricing
- Monte Carlo simulation using Geometric Brownian Motion
- Newton-Raphson implied volatility estimation
- Option Greeks
- Monte Carlo convergence analysis
- Real-market validation using SPY option data
- Historical vs. implied volatility analysis

The project focuses on understanding both the mathematical foundations and numerical implementation of option pricing models.

---

## Features

### 1. Black-Scholes-Merton Pricing

Implemented the Black-Scholes-Merton model for European call and put options.

The framework calculates:

- Option price
- Delta
- Gamma
- Vega
- Theta

For a European call:

$$
C = S_0e^{-qT}N(d_1)-Ke^{-rT}N(d_2)
$$

where

$$
d_1 =
\frac{
\ln(S_0/K)+(r-q+\sigma^2/2)T
}{
\sigma\sqrt{T}
}
$$

and

$$
d_2=d_1-\sigma\sqrt{T}
$$

---

### 2. Monte Carlo Pricing

Implemented Monte Carlo pricing using Geometric Brownian Motion:

$$
dS_t = rS_tdt+\sigma S_tdW_t
$$

The simulated terminal price is used to estimate the discounted expected payoff:

$$
V=e^{-rT}\mathbb{E}[\text{Payoff}]
$$

The Monte Carlo engine supports:

- Configurable number of simulation paths
- Configurable time steps
- Random seed control
- Antithetic variates
- European, Asian and Barrier option structures

---

### 3. Monte Carlo Convergence Analysis

Monte Carlo prices were evaluated across increasing numbers of simulation paths:

- 1,000
- 2,500
- 5,000
- 10,000
- 25,000
- 50,000
- 100,000
- 250,000

The simulated price converges toward the analytical Black-Scholes benchmark as the number of paths increases.

The analysis also examines:

- Absolute pricing error
- Relative pricing error
- Computational runtime

The theoretical Monte Carlo standard error decreases at approximately:

$$
O\left(\frac{1}{\sqrt{N}}\right)
$$

where $N$ is the number of simulation paths.

---

### 4. Implied Volatility

Implemented an implied volatility solver using the Newton-Raphson method.

The algorithm solves:

$$
BS(S,K,T,r,q,\sigma)=P_{market}
$$

using the iterative update.

The calculated volatility is validated by substituting it back into the Black-Scholes model and verifying that the resulting option price matches the market price.

---

### 5. Real-Market Validation

The pricing framework was tested using real SPY option data.

For the selected option:

1. Historical SPY prices were used to estimate annualized historical volatility.
2. The observed option bid and ask were used to calculate the market midpoint.
3. Black-Scholes and Monte Carlo prices were calculated using historical volatility.
4. The model prices were compared against the observed market price.
5. Market implied volatility was calculated using the Newton-Raphson solver.
6. Historical and implied volatility were compared.

The results demonstrate that both Black-Scholes and Monte Carlo produce similar theoretical prices when supplied with the same volatility input, while differences from the observed market price arise from model assumptions and the use of historical rather than market-implied volatility.
