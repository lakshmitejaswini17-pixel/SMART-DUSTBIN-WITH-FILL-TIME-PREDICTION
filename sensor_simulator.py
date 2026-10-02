"""sensor_simulator.py - simulated data + hardware helper.

The demo uses Streamlit inputs. When you add real hardware, the ESP32
sends a distance (cm) and `distance_to_fill_percent` converts it.
"""
from datetime import datetime, timedelta
import pandas as pd


def distance_to_fill_percent(distance_cm, bin_height_cm=50.0, min_distance_cm=3.0):
    """Convert HC-SR04 / ToF distance (sensor to garbage) into fill %.

    Sensor sits under the lid, so a large distance = empty bin.
    distance == bin_height -> 0 %,  distance <= min_distance -> 100 %
    """
    usable = bin_height_cm - min_distance_cm
    if usable <= 0:
        return 0.0
    fill = (bin_height_cm - distance_cm) / usable * 100
    return max(0.0, min(100.0, fill))            # keep between 0 and 100


def sample_history():
    """Sample readings (today, 10 AM to 4 PM) so the app works instantly."""
    start = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    levels = [30, 40, 52, 62]
    times = [start + timedelta(hours=2 * i) for i in range(len(levels))]
    return pd.DataFrame({"Time": times, "Fill %": levels})


# --- Future hardware idea (kept separate from the main app) ---------------
# ESP32 could POST {"distance_cm": 21.5} to a small Flask/FastAPI server,
# or write it to a CSV. The app would then call:
#     fill = distance_to_fill_percent(21.5, bin_height_cm=50)
