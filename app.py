from flask import Flask, render_template, request
import requests, datetime, json, pygal
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    chart_url = None
    if request.method == "POST":
        symbol = request.form.get("symbol")
        chart_type = request.form.get("chart_type")
        time_series = request.form.get("time_series")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        apiKey = "WZYK9TQ3C96A9WXT"

        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        chart_data = get_data(symbol, apiKey, time_series, start_dt, end_dt)
        if chart_data:
            generate_chart(chart_type, chart_data, start_date, end_date, symbol)
            chart_url = "/static/chart.svg"

    return render_template("index.html", chart_url=chart_url)

def get_data(symbol, apiKey, timeSeries, start_date, end_date):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_{timeSeries}&symbol={symbol}&outputsize=compact&apikey={apiKey}&datatype=json"
    response = requests.get(url)
    data = response.json()

    key = None
    for k in data.keys():
        if "Time Series" in k:
            key = k
            break

    if not key:
        return None

    filtered_data = {}
    for date, values in data[key].items():
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        if start_date <= dt <= end_date:
            filtered_data[date] = values

    return dict(sorted(filtered_data.items()))

def generate_chart(chartType, data, startDate, endDate, symbol):
    if not os.path.exists("static"):
        os.makedirs("static")

    dates = list(data.keys())[::-1]
    opens, highs, lows, closes = [], [], [], []

    for date in dates:
        values = data[date]
        opens.append(float(values['1. open']))
        highs.append(float(values['2. high']))
        lows.append(float(values['3. low']))
        closes.append(float(values['4. close']))

    if chartType == "LINE":
        chart = pygal.Line()
    else:
        chart = pygal.Bar()

    chart.title = f"{symbol} {chartType} Chart from {startDate} to {endDate}"
    chart.x_labels = dates
    chart.add("Open", opens)
    chart.add("High", highs)
    chart.add("Low", lows)
    chart.add("Close", closes)
    chart.render_to_file("static/chart.svg")