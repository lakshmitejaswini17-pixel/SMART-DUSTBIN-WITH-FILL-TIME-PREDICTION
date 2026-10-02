# 🗑️ Smart Dustbin Fill-Time Prediction System

Streamlit dashboard that monitors a dustbin's fill level, predicts when it
will reach 80% / 100%, raises an overflow alert and simulates an automatic lid.
No hardware needed for the demo.

## Files
| File | Purpose |
|------|---------|
| `app.py` | Streamlit dashboard (UI) |
| `prediction.py` | Status + accumulation-rate + time prediction |
| `sensor_simulator.py` | Sample data + distance → fill % conversion |
| `requirements.txt` | Python packages |

## Install
1. Install Python 3.9+ and open the `smart_dustbin` folder in VS Code.
2. Open the terminal (Ctrl + `) and (optionally) create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # macOS / Linux
   ```
3. Install packages:
   ```
   pip install -r requirements.txt
   ```

## Run
```
streamlit run app.py
```
The browser opens at http://localhost:8501.

## How prediction works
A straight line is fitted through the (time, fill %) readings. Its slope is the
rate in %/hour. Time to target = (target − current) ÷ rate.
With fewer than 2 valid readings (or a non-increasing trend) the app shows
"Not enough data for prediction."

## Demo tips
- Move the sidebar slider above 80% → overflow alert + LED/buzzer simulation.
- Click **User Detected** → lid opens, closes after 3 seconds.
- Edit the history table → chart and prediction update instantly.
- Choose "Ultrasonic distance" mode to show the HC-SR04 → % conversion.

## Future hardware (ESP32 + HC-SR04/ToF)
The ESP32 sends the measured distance in cm; `distance_to_fill_percent()` in
`sensor_simulator.py` converts it. Add a small API/CSV reader and feed the
result into `app.py` in place of the slider.
