# Astronaut Health Monitor

NASA Space Apps Challenge project.

A web dashboard that tracks astronaut health vitals and raises
warning and critical alerts when a reading goes outside its limits.

**Live app:** https://astronaut-health-monitor-9dwrhjhc4kmpynzp5lkpqr.streamlit.app/

## What it does
- Shows each crew member's latest readings with a status label
  (Normal, Warning, Critical)
- Draws a history chart for each vital with the limit lines
- Lists alert events with start time, end time and peak value
- Lets you upload your own CSV and download the alerts as CSV

## Vitals tracked
Heart rate, blood oxygen, carbon dioxide, cabin pressure,
radiation and body temperature.

## Important note
The demo data is synthetic, and the limit values are placeholders.
They are meant to be replaced with limits from NASA sources.

## Run it on your computer
    python3 -m pip install -r requirements.txt
    python3 -m streamlit run astronaut_dashboard.py

## Built with
Python, Streamlit, pandas, numpy, matplotlib
