"""prediction.py - simple maths for status and fill-time prediction (no ML)."""
import numpy as np
import pandas as pd


def get_status(fill):
    """Convert a fill percentage into a status label and an emoji."""
    if fill <= 30:
        return "Empty", "🟢"
    if fill <= 60:
        return "Half-full", "🟡"
    if fill <= 80:
        return "Nearly full", "🟠"
    return "Full", "🔴"


def clean_history(df):
    """Make the table safe to use: fix types, drop bad rows, sort by time."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["Time", "Fill %"])
    df = df.copy()
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df["Fill %"] = pd.to_numeric(df["Fill %"], errors="coerce")
    df = df.dropna(subset=["Time", "Fill %"])          # remove invalid rows
    df = df[(df["Fill %"] >= 0) & (df["Fill %"] <= 100)]
    return df.sort_values("Time").reset_index(drop=True)


def calculate_rate(df):
    """Return waste accumulation rate in % per hour, or None if not possible.

    We fit a straight line through all readings (percent vs hours).
    The slope of that line is the average rate.
    """
    df = clean_history(df)
    if len(df) < 2:
        return None
    hours = (df["Time"] - df["Time"].iloc[0]).dt.total_seconds() / 3600
    if hours.iloc[-1] <= 0:                              # all same timestamp
        return None
    slope, _ = np.polyfit(hours, df["Fill %"], 1)
    return float(slope)


def hours_to_target(current, target, rate):
    """Hours until `target` % is reached. None if impossible to predict."""
    if current >= target:
        return 0.0
    if rate is None or rate <= 0:                        # not filling up
        return None
    return (target - current) / rate


def format_duration(hours):
    """Turn 7.5 into '7 hours 30 min'."""
    if hours is None:
        return "Not enough data for prediction."
    if hours == 0:
        return "Already reached"
    total_min = int(round(hours * 60))
    h, m = divmod(total_min, 60)
    if h == 0:
        return f"{m} min"
    return f"{h} hours" + (f" {m} min" if m else "")
