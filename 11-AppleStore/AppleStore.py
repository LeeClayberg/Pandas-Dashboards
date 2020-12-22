import dash
import math
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# https://www.kaggle.com/ramamet4/app-store-apple-data-set-10k-apps
df = pandas.read_csv("apple_store_data.csv", index_col=0)

under_million_reviews = df[df['rating_count_tot'] < 1000000]

most_exp = df.sort_values(by='price', ascending=False).head(10)[['track_name', 'price']]

largest_apps = df.sort_values(by='size_bytes', ascending=False).head(20)[['track_name', 'size_bytes']]

game_genres = df.groupby('prime_genre').count()['size_bytes'].reset_index()
print(largest_apps)


@app.callback([Output(component_id='rated_counts', component_property='figure'),
               Output(component_id='cost_graph', component_property='figure'),
               Output(component_id='size_graph', component_property='figure'),
               Output(component_id='genre_graph', component_property='figure')],
              [Input("my_interval", "n_intervals")])
def update(n):
    rated_fig = go.Figure(data=[
        go.Scatter(x=under_million_reviews['rating_count_tot'], y=under_million_reviews['user_rating'], mode='markers',
                   marker=dict(color='#FF3300', size=3))
    ])
    rated_fig.update_layout(title="Average Ratings for Apps (fewer than 1 million reviews)", template="plotly_dark",
                            yaxis_title="Average Rating", xaxis_title="Review Count")

    most_expensive_fig = go.Figure(data=[
        go.Bar(x=most_exp['track_name'], y=most_exp['price'], marker_color='#3399FF')
    ])
    most_expensive_fig.update_layout(title="Top 10 Most Expensive Apps", template="plotly_dark", yaxis_title="Cost(USD)")

    size_fig = go.Figure(data=[
        go.Bar(x=largest_apps['track_name'], y=largest_apps['size_bytes'], marker_color='#FF3300')
    ])
    size_fig.update_layout(title="Top 20 Largest Apps (in bytes)", template="plotly_dark", yaxis_title="Bytes")

    genre_fig = go.Figure(data=[
        go.Bar(x=game_genres['prime_genre'], y=game_genres['size_bytes'], marker_color='#3399FF')
    ])
    genre_fig.update_layout(title="Games in Each Genre", template="plotly_dark", yaxis_title="Count")

    return rated_fig, most_expensive_fig, size_fig, genre_fig


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=300 * 1000,
        max_intervals=100,
    ),
    html.H1('App Store Data', style={'paddingTop': '20px', 'textAlign': 'center', 'color': 'white',
                                          'fontSize': 30, 'font-family': 'Arial, Helvetica, sans-serif'}),
    dbc.Row([
        html.Div([
            dcc.Graph(id='rated_counts', config={'displayModeBar': False})
        ], style={"width": '60%'}),
        html.Div([
            dcc.Graph(id='cost_graph', config={'displayModeBar': False})
        ], style={"width": '40%'}),
    ]),
    dbc.Row([
        html.Div([
            dcc.Graph(id='genre_graph', config={'displayModeBar': False}),
            dcc.Graph(id='size_graph', config={'displayModeBar': False})
        ], style={"width": '40%'}),
        html.Div([

        ], style={"width": '60%', 'padding': '40px'}),
    ]),
], style={'backgroundColor': '#111111'})

if __name__ == '__main__':
    app.run_server(debug=True)
