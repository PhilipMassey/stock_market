# Performance Metrics Overview

This document provides an overview of the key performance metrics calculated in the `performance` module (specifically in `perc_for_sector_industry.py`), how to interpret them, and their value when analyzing stock or portfolio performance.

## How it Defaults in the Tables
Right now, the Percent Mean & Std Rank dashboard drops in automatically sorted by Risk Reward Rank ascending (1 being the best).
If you specifically want to filter your list globally by Kelly instead, all you have to do is click the arrow above the Kelly Rank column in the browser table to sort it ascending (Top to Bottom). The number 1 should sit at the very top, revealing the single most heavily reinforced asset under the Kelly sizing criterion!

## 1. Overall Percentage Change (`over_pc`)

- **What it is:** The gross percentage return from the very first valid price to the very last valid price in the selected timeframe.
- **How to interpret:** A positive number indicates the asset grew over the period; a negative number indicates a decline.
- **Value:** This is the bottom-line performance. It tells you the actual return generated over the entire period, ignoring the fluctuations that happened in between.

## 2. Average Period Change (`pc_mean`)

- **What it is:** The arithmetic average of the period-to-period percentage changes (e.g., the average of all daily, weekly, or monthly returns).
- **How to interpret:** A high positive `pc_mean` suggests general upward momentum per interval.
- **Value:** While `over_pc` gives the total return, `pc_mean` helps you understand the consistency of growth. A stock can have a high `over_pc` due to a single massive price spike, but a solid `pc_mean` indicates more consistent compounding over time.

## 3. Volatility / Standard Deviation (`pc_std`)

- **What it is:** The standard deviation of the period-to-period percentage changes.
- **How to interpret:** 
  - **High `pc_std`:** The asset experiences large, unpredictable price swings.
  - **Low `pc_std`:** The asset's returns are relatively stable and predictable.
- **Value:** Represents the **risk** or volatility of the asset. Investors generally prefer lower volatility for a given level of return, as it indicates a smoother ride and less unpredictable risk.

## 4. Risk-Reward Ratio (`risk_reward`)

- **What it is:** A simplified proxy for risk-adjusted return, calculated as `pc_mean` divided by `pc_std`.
- **How to interpret:** It indicates how many units of return you receive per unit of risk (volatility). A higher number is better.
- **Value:** This is extremely valuable for comparing two assets with similar returns. If Stock A and Stock B both average a 1% return per week, but Stock A has half the volatility of Stock B, Stock A will have double the risk-reward ratio, making it the statistically superior choice.

## 5. Annualized Sharpe Ratio (`sharpe_ratio`)

- **What it is:** A standardized metric that evaluates the *excess return* (the return above a risk-free rate, such as Treasury yields) divided by the asset's volatility (`pc_std`), which is then annualized based on the periods per year.
- **How to interpret:** 
  - **> 1.0:** Good risk-adjusted return.
  - **> 2.0:** Great risk-adjusted return.
  - **> 3.0:** Excellent risk-adjusted return.
- **Value:** This is the industry gold standard for risk-adjusted performance. It answers the critical question: *"Is the extra volatility of holding this stock adequately compensating me compared to holding a 100% safe, risk-free asset?"*

## 6. Relative Industry Strength (`rel_strength_ind`)

- **What it is:** The stock's overall performance (`over_pc`) minus the average overall performance of its specific industry (`ind_mean_pc`). 
- **How to interpret:** A positive number means the stock is outperforming its industry peers; a negative number means it is lagging.
- **Value:** Helps isolate true "Alpha" and identifies Sector Leaders. Even if a stock went up 10%, if its entire industry went up 20%, it is actually a relatively weak stock. Finding stocks with high `rel_strength_ind` alongside a good risk profile helps identify the strongest, most resilient names in a sector.

## 7. Probability Of Positive Day (`prob_green_day_%`)

- **What it is:** The statistical probability that a stock will close positively (a "green" period), computed by modeling its historical returns as a normal distribution using `pc_mean` and `pc_std`.
- **How to interpret:** Gives a percentage chance (e.g., 55.4%) that the next trading period will close positive.
- **Value:** Translates abstract metrics into an intuitive, real-world probability of success. It's highly useful for day-to-day swing trades or options strategies to determine the baseline statistical edge of opening a long position.

## 8. Stretch Score / Mean Reversion (`stretch_score`)

- **What it is:** The overall performance (`over_pc`) divided by the standard deviation (`pc_std`). 
- **How to interpret:** 
  - **High Positive Score:** The stock is over-extended to the upside.
  - **High Negative Score:** The stock is oversold or capitulated to the downside.
- **Value:** Acts as a rubber band indicator. When a stock's overall performance drastically exceeds what is considered statistically normal based on its historical volatility, it is over-extended and vulnerable to a sharp mean reversion (a snapback or pullback).

## 9. Kelly Fraction (`kelly_fraction`)

- **What it is:** An output based on the Kelly Criterion optimal bet sizing formula. Specifically, this is the continuous simplified fraction calculated as `pc_mean` divided by Variance (`pc_std` squared).
- **How to interpret:** Acts as an extreme "aggressiveness score" that heavily penalizes volatility in its position sizing recommendation.
- **Value:** Ideal for deciding portfolio sizing and allocation limits. Because the calculation squares the volatility, it mathematically punishes and filters out highly volatile meme-stocks (even if they have high average returns) and zeroes in exclusively on the most mathematically optimal, consistent compounders.

- in the codebase, your Pandas rank
 calculation is currently set entirely up to reward the mathematically highest Kelly scores:

python
df_all['kelly_fraction'].rank(ascending=False, method='min')
Because it uses ascending=False, the symbols with the absolute highest pure Kelly Fractions are assigned Rank 1. Lower fractions, zeros, or negatives filter mathematically downward toward the bottom ranks.
