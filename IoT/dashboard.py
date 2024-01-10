from flask import Flask, render_template
import dash
from dash import html, dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
import sensor_reader  # Import the sensor reading module
import time
from markupsafe import Markup

sleep_quality_update_interval = 20 * 1000 

# Anpassung der Gewichtungen
LOUDNESS_WEIGHT = 0.3
LIGHT_WEIGHT = 0.3
TEMPERATURE_WEIGHT = 0.2
HUMIDITY_WEIGHT = 0.2

# Schwellenwerte und Zielbereiche
IDEAL_TEMPERATURE = 17  # in Celsius
IDEAL_HUMIDITY = 50     # in Prozent

# Create a Flask app
server = Flask(__name__)

# Initialize Dash app with Flask server
app = dash.Dash(__name__, 
                server=server, 
                url_base_pathname='/dash/',
                external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
)

# Enhanced styling
graph_style = {
    "backgroundColor": "#FFFFFF",
    "margin": "10px",
    "padding": "20px",
    "borderRadius": "8px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    "width": "40%",
}
title_style = {"textAlign": "center", "color": "#2C3E50"}
overview_style = {"fontSize": "1.2em", "marginBottom": "5px"}
overview_box_style = {
    "backgroundColor": "#EAECEE",
    "padding": "20px",
    "borderRadius": "8px",
    "marginBottom": "20px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
}

# App layout with separate graphs, intervals for each sensor
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Sleep Environment Dashboard", style=title_style),
                html.Div(id="overview-content", style=overview_box_style),
            ]
        ),
        html.Div(
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "space-between",
            },
            children=[
                html.Div(
                    [
                        html.H3("Loudness", style=title_style),
                        dcc.Graph(id="loudness-graph"),
                        dcc.Interval(
                            id="interval-loudness", interval=10 * 1000, n_intervals=0
                        ),
                    ],
                    style=graph_style,
                ),
                html.Div(
                    [
                        html.H3("Light", style=title_style),
                        dcc.Graph(id="light-graph"),
                        dcc.Interval(
                            id="interval-light", interval=10 * 1000, n_intervals=0
                        ),
                    ],
                    style=graph_style,
                ),
                html.Div(
                    [
                        html.H3("Temperature", style=title_style),
                        dcc.Graph(id="temperature-graph"),
                        dcc.Interval(
                            id="interval-temperature", interval=10 * 1000, n_intervals=0
                        ),
                    ],
                    style=graph_style,
                ),
                html.Div(
                    [
                        html.H3("Humidity", style=title_style),
                        dcc.Graph(id="humidity-graph"),
                        dcc.Interval(
                            id="interval-humidity", interval=10 * 1000, n_intervals=0
                        ),
                    ],
                    style=graph_style,
                ),
            ],
        ),
    ],
    style={
        "fontFamily": "Open Sans, sans-serif",
        "padding": "20px",
        "backgroundColor": "#ECF0F1",
        "maxWidth": "1600px",
        "margin": "0 auto",
    },
)   

# Initialize a history of data points
data_history = {
    'loudness': [],
    'light': [],
    'temperature': [],
    'humidity': [],
    'sleep_quality': []  # Neues Array für Schlafqualitätsdaten
}

# Function to update the data history
def update_data_history(sensor_type):
    with sensor_reader.data_lock:
        data_history[sensor_type].append(sensor_reader.calculate_average(sensor_reader.sensor_data[sensor_type]))
        sensor_reader.sensor_data[sensor_type].clear()

# Funktion zur Berechnung der Schlafqualität und Benachrichtigungen
def calculate_sleep_quality():
    loudness_data = data_history['loudness'][-3:]
    light_data = data_history['light'][-3:]
    temperature_data = data_history['temperature'][-3:]
    humidity_data = data_history['humidity'][-3:]

    # Verwenden Sie den Durchschnitt der letzten drei Werte
    avg_loudness = sum(loudness_data) / len(loudness_data) if loudness_data else 0
    avg_light = sum(light_data) / len(light_data) if light_data else 0
    avg_temperature = sum(temperature_data) / len(temperature_data) if temperature_data else 0
    avg_humidity = sum(humidity_data) / len(humidity_data) if humidity_data else 0

    # Anpassen der Berechnungslogik
    loudness_quality = 30 - avg_loudness if avg_loudness < 30 else 0
    light_quality = 10 - avg_light if avg_light < 10 else 0
    temperature_quality = 18 - abs(IDEAL_TEMPERATURE - avg_temperature) if abs(IDEAL_TEMPERATURE - avg_temperature) < 18 else 0
    humidity_quality = 10 - abs(IDEAL_HUMIDITY - avg_humidity) if abs(IDEAL_HUMIDITY - avg_humidity) < 10 else 0

    # Gewichtete Berechnung
    sleep_quality = max(0, (LOUDNESS_WEIGHT * loudness_quality + 
                            LIGHT_WEIGHT * light_quality +
                            TEMPERATURE_WEIGHT * temperature_quality + 
                            HUMIDITY_WEIGHT * humidity_quality) / (LOUDNESS_WEIGHT + LIGHT_WEIGHT + TEMPERATURE_WEIGHT + HUMIDITY_WEIGHT))


    # Liste zur Speicherung der Benachrichtigungen mit ihrer Dringlichkeit
    notifications = []
    if avg_loudness > 30:
        notifications.append(("high", f"Reduzieren Sie Lärm (aktuell: {avg_loudness:.1f} dB)"))
    
    if avg_light > 10:
        notifications.append(("high", f"Verdunkeln Sie den Raum (aktuelle Lichtstärke: {avg_light:.1f})"))
    
    if abs(IDEAL_TEMPERATURE - avg_temperature) > 2:
        notifications.append(("medium", f"Optimieren Sie die Raumtemperatur (aktuell: {avg_temperature:.1f}°C, ideal: {IDEAL_TEMPERATURE}°C)"))
    
    if abs(IDEAL_HUMIDITY - avg_humidity) > 10:
        notifications.append(("medium", f"Passen Sie die Luftfeuchtigkeit an (aktuell: {avg_humidity:.1f}%, ideal: {IDEAL_HUMIDITY}%)"))

    # Sortieren der Benachrichtigungen nach ihrer Dringlichkeit
    notifications.sort(key=lambda x: x[0], reverse=True)
    return sleep_quality, notifications

# Callback zur Aktualisierung der Schlafqualität und Benachrichtigungen
@app.callback(
    [Output('sleep-quality', 'children'),
     Output('sleep-notification', 'children')],
    [Input('interval-sleep-quality', 'n_intervals')]
)

def update_sleep_quality(n):
    sleep_quality, notifications = calculate_sleep_quality()
    data_history['sleep_quality'].append(sleep_quality)

    return f'Schlafqualität: {sleep_quality:.2f}'

# Callbacks for each sensor graph update
@app.callback(
    Output("loudness-graph", "figure"), [Input("interval-loudness", "n_intervals")]
)
def update_loudness_graph(n):
    update_data_history("loudness")
    loudness_values = data_history["loudness"]

    # Assuming each data point is spaced evenly, for example, every minute
    interval = timedelta(minutes=1)
    now = datetime.now()
    timestamps = [
        now - interval * (len(loudness_values) - i) for i in range(len(loudness_values))
    ]

    # Find the min and max loudness values
    min_val = min(loudness_values)
    max_val = max(loudness_values)
    mean_val = sum(loudness_values) / len(loudness_values)

    # Create the base figure with annotations
    figure = {
        "data": [go.Scatter(x=timestamps, y=loudness_values, mode="lines+markers")],
        "layout": go.Layout(
            title="Loudness",
            xaxis=dict(type="date"),  # Ensure x-axis is treated as datetime
            annotations=[
                dict(
                    x=timestamps[loudness_values.index(min_val)],
                    y=min_val,
                    text=f"Min: {min_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
                dict(
                    x=timestamps[loudness_values.index(max_val)],
                    y=max_val,
                    text=f"Max: {max_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
            ],
            shapes=[
                dict(
                    type="line",
                    x0=timestamps[0],
                    y0=mean_val,
                    x1=timestamps[-1],
                    y1=mean_val,
                    line=dict(color="green", width=2.5, dash="dash"),
                )
            ],
        ),
    }

    return figure


@app.callback(Output("light-graph", "figure"), [Input("interval-light", "n_intervals")])
def update_light_graph(n):
    update_data_history("light")
    light_values = data_history["light"]

    # Assuming each data point is spaced evenly, for example, every minute
    interval = timedelta(minutes=1)
    now = datetime.now()
    timestamps = [
        now - interval * (len(light_values) - i) for i in range(len(light_values))
    ]

    # Find the min and max light values
    min_val = min(light_values)
    max_val = max(light_values)
    mean_val = sum(light_values) / len(light_values)

    # Create the base figure with annotations
    figure = {
        "data": [go.Scatter(x=timestamps, y=light_values, mode="lines+markers")],
        "layout": go.Layout(
            title="Light",
            xaxis=dict(type="date"),  # Ensure x-axis is treated as datetime
            annotations=[
                dict(
                    x=timestamps[light_values.index(min_val)],
                    y=min_val,
                    text=f"Min: {min_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
                dict(
                    x=timestamps[light_values.index(max_val)],
                    y=max_val,
                    text=f"Max: {max_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
            ],
            shapes=[
                dict(
                    type="line",
                    x0=timestamps[0],
                    y0=mean_val,
                    x1=timestamps[-1],
                    y1=mean_val,
                    line=dict(color="green", width=2.5, dash="dash"),
                )
            ],
        ),
    }

    return figure


@app.callback(
    Output("temperature-graph", "figure"),
    [Input("interval-temperature", "n_intervals")],
)
def update_temperature_graph(n):
    update_data_history("temperature")
    temperature_values = data_history["temperature"]

    # Assuming each data point is spaced evenly, for example, every minute
    interval = timedelta(minutes=1)
    now = datetime.now()
    timestamps = [
        now - interval * (len(temperature_values) - i)
        for i in range(len(temperature_values))
    ]

    # Find the min and max temperature values
    min_val = min(temperature_values)
    max_val = max(temperature_values)
    mean_val = sum(temperature_values) / len(temperature_values)

    # Create the base figure with annotations
    figure = {
        "data": [go.Scatter(x=timestamps, y=temperature_values, mode="lines+markers")],
        "layout": go.Layout(
            title="Temperature",
            xaxis=dict(type="date"),  # Ensure x-axis is treated as datetime
            annotations=[
                dict(
                    x=timestamps[temperature_values.index(min_val)],
                    y=min_val,
                    text=f"Min: {min_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
                dict(
                    x=timestamps[temperature_values.index(max_val)],
                    y=max_val,
                    text=f"Max: {max_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
            ],
            shapes=[
                dict(
                    type="line",
                    x0=timestamps[0],
                    y0=mean_val,
                    x1=timestamps[-1],
                    y1=mean_val,
                    line=dict(color="green", width=2.5, dash="dash"),
                )
            ],
        ),
    }

    return figure


@app.callback(
    Output("humidity-graph", "figure"), [Input("interval-humidity", "n_intervals")]
)
def update_humidity_graph(n):
    update_data_history("humidity")
    humidity_values = data_history["humidity"]

    # Assuming each data point is spaced evenly, for example, every minute
    interval = timedelta(minutes=1)
    now = datetime.now()
    timestamps = [
        now - interval * (len(humidity_values) - i) for i in range(len(humidity_values))
    ]

    # Find the min and max humidity values
    min_val = min(humidity_values)
    max_val = max(humidity_values)
    mean_val = sum(humidity_values) / len(humidity_values)

    # Create the base figure with annotations
    figure = {
        "data": [go.Scatter(x=timestamps, y=humidity_values, mode="lines+markers")],
        "layout": go.Layout(
            title="Humidity",
            xaxis=dict(type="date"),  # Ensure x-axis is treated as datetime
            annotations=[
                dict(
                    x=timestamps[humidity_values.index(min_val)],
                    y=min_val,
                    text=f"Min: {min_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
                dict(
                    x=timestamps[humidity_values.index(max_val)],
                    y=max_val,
                    text=f"Max: {max_val}",
                    showarrow=True,
                    arrowhead=1,
                ),
            ],
            shapes=[
                dict(
                    type="line",
                    x0=timestamps[0],
                    y0=mean_val,
                    x1=timestamps[-1],
                    y1=mean_val,
                    line=dict(color="green", width=2.5, dash="dash"),
                )
            ],
        ),
    }

    return figure
    update_data_history('humidity')
    humidity_values = data_history['humidity']
    
    # Assuming each data point is spaced evenly, for example, every minute
    interval = timedelta(minutes=1)
    now = datetime.now()
    timestamps = [now - interval * (len(humidity_values) - i) for i in range(len(humidity_values))]

    # Find the min and max humidity values
    min_val = min(humidity_values)
    max_val = max(humidity_values)
    mean_val = sum(humidity_values) / len(humidity_values)

    # Create the base figure with annotations
    figure = {
        'data': [go.Scatter(x=timestamps, y=humidity_values, mode='lines+markers')],
        'layout': go.Layout(
            title='Humidity',
            xaxis=dict(type='date'),  # Ensure x-axis is treated as datetime
            annotations=[
                dict(
                    x=timestamps[humidity_values.index(min_val)],
                    y=min_val,
                    text=f"Min: {min_val}",
                    showarrow=True,
                    arrowhead=1
                ),
                dict(
                    x=timestamps[humidity_values.index(max_val)],
                    y=max_val,
                    text=f"Max: {max_val}",
                    showarrow=True,
                    arrowhead=1
                )
            ],
            shapes=[
                dict(
                    type="line",
                    x0=timestamps[0],
                    y0=mean_val,
                    x1=timestamps[-1],
                    y1=mean_val,
                    line=dict(color="green", width=2.5, dash="dash"),
                )
            ]
        )
    }

    return figure

# Define additional Flask routes if needed
@server.route('/')
def index():
    return render_template('index.html')

@server.route('/quality')
def quality():
    sleep_quality_data, notifications = calculate_sleep_quality()

    # Process notifications for HTML display
    formatted_notifications = ""
    for priority, message in notifications:
        color = "red" if priority == "high" else "orange" if priority == "medium" else "green"
        formatted_notifications += f'<p style="color: {color};">{message}</p>'


    return render_template('quality.html', data=sleep_quality_data, notifications=Markup(formatted_notifications))

@server.route('/about')
def about():
    return render_template('about.html')

# Run the Flask app instead of Dash app
if __name__ == '__main__':
    sensor_reader.start_sensor_threads()  # Start sensor threads if needed
    server.run(debug=True)