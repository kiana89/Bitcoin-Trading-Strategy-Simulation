import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Download Bitcoin data
df = yf.download("BTC-USD", start="2020-01-01", end="2024-12-31")

df["Date"] = df.index
df["WeekDay"] = df["Date"].dt.weekday

# Initial capital
initial_capital = 1000
capital = initial_capital
profit_loss_history = [initial_capital]

# Variables to track holdings
btc_held = 0
buy_price = 0

# Simulate the specific strategy (Buy on Tuesday, Sell on Thursday)
print("Simulating Buy on Tuesday (Weekday 2) and Sell on Thursday (Weekday 4) strategy...")
for index, row in df.iterrows():
    # Buy on Tuesday (Weekday 2) using Open price
    if row["WeekDay"].item() == 2 and btc_held == 0:
        if capital > 0:
            btc_held = capital / row["Open"].item()
            buy_price = row["Open"].item()
            # print(f"Bought {btc_held:.4f} BTC on {row['Date'].date()} at {buy_price:.2f}")
            capital = 0  # Capital is now invested

    # Sell on Thursday (Weekday 4) using Close price
    elif row["WeekDay"].item() == 4 and btc_held > 0:
        capital = btc_held * row["Close"].item()
        # print(f"Sold {btc_held:.4f} BTC on {row['Date'].date()} at {row['Close']:.2f}. Capital: {capital:.2f}")
        btc_held = 0  # BTC is now sold

    # If a position is open and the year ends, close the position at the last available close price
    if index == df.index[-1] and btc_held > 0:
        capital = btc_held * row["Close"].item()
        btc_held = 0
        # print(f"Closing open position on {row['Date'].date()} at year end. Capital: {capital:.2f}")

    profit_loss_history.append(capital if capital > 0 else (btc_held * row['Close'].item() if btc_held > 0 else profit_loss_history[-1]))


# Remove the initial duplicate capital value from the start of the history
profit_loss_history_cleaned = [initial_capital]
current_capital_value = initial_capital

# Reconstruct profit_loss_history to accurately reflect capital at each step
# This ensures that the capital reflects the current state (either cash or value of BTC held)
profit_loss_for_plotting = []
btc_held_for_plot = 0
buy_price_for_plot = 0
current_capital_for_plot = initial_capital

for index, row in df.iterrows():
    if row["WeekDay"].item() == 2 and btc_held_for_plot == 0:
        if current_capital_for_plot > 0:
            btc_held_for_plot = current_capital_for_plot / row["Open"].item()
            buy_price_for_plot = row["Open"].item()
            current_capital_for_plot = 0
    elif row["WeekDay"].item() == 4 and btc_held_for_plot > 0:
        current_capital_for_plot = btc_held_for_plot * row["Close"].item()
        btc_held_for_plot = 0

    # If BTC is held, its value contributes to current capital for plotting purposes
    if btc_held_for_plot > 0:
        profit_loss_for_plotting.append(btc_held_for_plot * row["Close"].item())
    else:
        profit_loss_for_plotting.append(current_capital_for_plot)

# Ensure the length of profit_loss_for_plotting matches the DataFrame
if len(profit_loss_for_plotting) < len(df):
    # This can happen if the last day is not a selling day.
    # We need to add the final capital or value of held BTC for the remaining days if any.
    last_capital = profit_loss_for_plotting[-1] if profit_loss_for_plotting else initial_capital
    while len(profit_loss_for_plotting) < len(df):
        profit_loss_for_plotting.append(last_capital)
elif len(profit_loss_for_plotting) > len(df):
    profit_loss_for_plotting = profit_loss_for_plotting[:len(df)]


# Final Capital for the specific strategy
print(f"\nFinal Capital (Buy Tue/Sell Thu): ${capital:.2f}")
print(f"Total Profit/Loss: ${(capital - initial_capital):.2f}")

# Plotting the profit/loss for the specific strategy
plt.figure(figsize=(12, 6))
plt.plot(df.index, profit_loss_for_plotting, label="Capital over time (Buy Tue/Sell Thu)")
plt.axhline(y=initial_capital, color='r', linestyle='--', label="Initial Capital")
plt.title("Capital Growth Simulation (Buy on Tuesday, Sell on Thursday)")
plt.xlabel("Date")
plt.ylabel("Capital ($)")
plt.legend()
plt.grid(True)
plt.show()

# Find optimal buy/sell days
print("\nFinding optimal buy and sell days...")
max_profit = -float('inf')
optimal_buy_day = -1
optimal_sell_day = -1

# Iterate through all possible buy days (0-6)
for buy_day in range(7):
    # Iterate through all possible sell days (0-6)
    for sell_day in range(7):
        if buy_day == sell_day:
            continue  # Cannot buy and sell on the same day

        temp_capital = initial_capital
        temp_btc_held = 0
        temp_buy_price = 0

        for index, row in df.iterrows():
            # Buy
            if row["WeekDay"].item() == buy_day and temp_btc_held == 0:
                if temp_capital > 0:
                    temp_btc_held = temp_capital / row["Open"].item()
                    temp_buy_price = row["Open"].item()
                    temp_capital = 0
            # Sell
            elif row["WeekDay"].item() == sell_day and temp_btc_held > 0:
                temp_capital = temp_btc_held * row["Close"].item()
                temp_btc_held = 0

            # If at the very end of the dataframe and holding BTC, liquidate
            if index == df.index[-1] and temp_btc_held > 0:
                temp_capital = temp_btc_held * row["Close"].item()
                temp_btc_held = 0


        profit = temp_capital - initial_capital

        if profit > max_profit:
            max_profit = profit
            optimal_buy_day = buy_day
            optimal_sell_day = sell_day

weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

print(f"\nOptimal Buy Day: {weekday_names[optimal_buy_day]} (Weekday {optimal_buy_day})")
print(f"Optimal Sell Day: {weekday_names[optimal_sell_day]} (Weekday {optimal_sell_day})")
print(f"Maximum Profit with Optimal Strategy: ${max_profit:.2f}")