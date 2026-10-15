from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "orders.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["order_date"])

# Basic validation
assert df["order_id"].notna().all(), "Missing order IDs found"
assert not df["order_id"].duplicated().any(), "Duplicate order IDs found"
assert df["quantity"].gt(0).all(), "Non-positive quantities found"
assert df["discount_pct"].between(0, 1).all(), "Discounts outside 0-100% found"

# Business rule: cancelled and returned orders do not contribute to recognized revenue.
completed = df.loc[df["status"].eq("Completed")].copy()
completed["month"] = completed["order_date"].dt.to_period("M").astype(str)

monthly = completed.groupby("month", as_index=False).agg(
    completed_orders=("order_id", "nunique"),
    unique_customers=("customer_id", "nunique"),
    revenue=("net_revenue", "sum"),
    estimated_profit=("estimated_profit", "sum"),
)
monthly["average_order_value"] = monthly["revenue"] / monthly["completed_orders"]
monthly.to_csv(OUT / "monthly_performance.csv", index=False)

category = completed.groupby("category", as_index=False).agg(
    completed_orders=("order_id", "nunique"),
    revenue=("net_revenue", "sum"),
    estimated_profit=("estimated_profit", "sum"),
).sort_values("revenue", ascending=False)
category.to_csv(OUT / "category_performance.csv", index=False)

region = completed.groupby("region", as_index=False).agg(
    completed_orders=("order_id", "nunique"),
    revenue=("net_revenue", "sum"),
    estimated_profit=("estimated_profit", "sum"),
).sort_values("revenue", ascending=False)
region.to_csv(OUT / "region_performance.csv", index=False)

plt.figure(figsize=(10, 5))
plt.plot(monthly["month"], monthly["revenue"], marker="o")
plt.xticks(rotation=45, ha="right")
plt.title("Monthly Recognized Revenue (Completed Orders)")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.tight_layout()
plt.savefig(OUT / "monthly_revenue.png", dpi=160)
plt.close()

print("Analysis complete. Results saved in the outputs/ folder.")
print(f"Completed orders: {completed['order_id'].nunique():,}")
print(f"Recognized revenue: ${completed['net_revenue'].sum():,.2f}")
print(f"Estimated profit: ${completed['estimated_profit'].sum():,.2f}")
print(f"Return/cancel rate: {(df['status'].ne('Completed').mean()):.1%}")
