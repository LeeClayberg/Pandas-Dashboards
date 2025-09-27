import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import requests
from datetime import datetime

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

server = app.server

categories_left = ["wind_speed", "precip", "humidity", "observation_time"]
categories_right = ["cloudcover", "uv_index", "visibility", "pressure"]
units_left = [" kph", " mm", "%", ""]
units_right = ["%", " of 10", " km", " mb"]
icons_left = [
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/wind.png",
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/precipitation.png",
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/humidity.png",
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/time.png"
]
icons_right = [
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/cloudCover.png",
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/uvIndex.png",
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/visibility.png",
    "https://storage.googleapis.com/lee-clayberg.firebasestorage.app/projects/weatherDashboard/icons/pressure.png"
]


def format_name(name):
    return name.replace("_", " ").replace("[", " ").replace("]", " ").replace("'", " ").title()


def update_weather():
    weather_requests = requests.get(
        "http://api.weatherstack.com/current?access_key=0b506817103c31948c4eec22fee9c155&query=Boston"
    )
    json_data = weather_requests.json()
    df = pd.DataFrame(json_data)
    print(df)
    return ([
        html.Div([" Weather Today in Boston, MA - " + datetime.now().strftime("%I:%M%p")],
                 style={'padding': '30px 20px 0px', 'textAlign': 'center', 'color': 'black', 'fontSize': 40,
                        'fontWeight': 'bold'}),
        html.Div([
            html.Div([
                html.Div([str(round(df['current']['temperature'] * (9 / 5) + 32, 1)) + "°"],
                         style={'fontWeight': 'bold'}),
                html.Div([format_name(str(df['current']['weather_descriptions']))],
                         style={'fontSize': 36, 'fontWeight': 'bold', 'marginTop': -40}),
                html.Img(
                    src=df['current']['weather_icons'][0],
                    width='80px',
                    style={'marginTop': -140, 'borderRadius': 10})
            ], style={'textAlign': 'center', 'fontSize': 140, 'height': 380, 'padding': '20px', 'color': 'white'})
        ]),
        html.Div([
            html.Table(
                className="table-weather",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.Div([
                                        html.Img(
                                            src=icon,
                                            width='10%'
                                        ),
                                        " " + format_name(name)
                                    ], style={'columnWidth': '85%'}),
                                    html.Div([
                                        str(data) + units
                                    ], style={'columnWidth': '15%', 'textAlign': 'right'})
                                ], style={"columnCount": 2, "padding": '5px 30px', 'width': '50%'}),
                            html.Td(
                                children=[
                                    html.Div([
                                        html.Img(
                                            src=icon2,
                                            width='10%'
                                        ),
                                        " " + format_name(name2)
                                    ], style={'columnWidth': '85%'}),
                                    html.Div([
                                        str(data2) + units2
                                    ], style={'columnWidth': '15%', 'textAlign': 'right'})
                                ], style={"columnCount": 2, "padding": '5px 30px', 'width': '50%'})
                        ]
                    )
                    for name, data, icon, units, name2, data2, icon2, units2
                    in zip(categories_left, df['current'][categories_left], icons_left, units_left,
                           categories_right, df['current'][categories_right], icons_right, units_right)
                ], style={'fontSize': 24, 'width': '80%', 'margin': 'auto', 'color': 'black',
                          'backgroundColor': 'white', 'borderRadius': '10px'})
        ])
    ])


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=300 * 1000,
        max_intervals=100,
    ),
    html.Div([
        html.Div(id="weather", children=update_weather())
    ])
], style={'backgroundColor': '#97B6E4', 'height': '100vh'})


@app.callback(Output("weather", "children"), [Input("my_interval", "n_intervals")])
def update_weather_div(n):
    return update_weather()


if __name__ == '__main__':
    app.run_server(debug=True)
