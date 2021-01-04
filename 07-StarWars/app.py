import math

import dash
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

starships = pandas.read_csv("star_wars_data/starships.csv", index_col=0,
                            dtype={'cost_in_credits': float, 'length': float, 'max_atmosphering_speed': float,
                                   'crew': float, 'passengers': float, 'cargo_capacity': float,
                                   'hyperdrive_rating': float})
vehicles = pandas.read_csv("star_wars_data/vehicles.csv", index_col=0,
                           dtype={'cost_in_credits': float, 'length': float, 'max_atmosphering_speed': float,
                                  'crew': float, 'passengers': float, 'cargo_capacity': float})
planets = pandas.read_csv("star_wars_data/planets.csv", index_col=0)
characters = pandas.read_csv("star_wars_data/characters.csv", index_col=0)

all = [starships, vehicles, planets, characters]
all_class = ["starship_class", "vehicle_class"]

categories_left = [["model", "manufacturer", "cost_in_credits", "length", "max_atmosphering_speed", "crew"],
                   ["model", "manufacturer", "cost_in_credits", "length", "max_atmosphering_speed"],
                   ["rotation_period", "orbital_period", "diameter", "climate"],
                   ["height", "mass", "hair_color", "skin_color"]]
categories_right = [["passengers", "cargo_capacity", "consumables", "hyperdrive_rating", "MGLT", "starship_class"],
                    ["crew", "passengers", "cargo_capacity", "consumables", "vehicle_class"],
                    ["gravity", "terrain", "surface_water", "population"],
                    ["eye_color", "birth_year", "homeworld", "species"]]
name_width_left = [[14, 25, 28, 14, 46, 12], [14, 25, 28, 14, 46], [30, 28, 20, 18], [16, 12, 20, 20]]
name_width_right = [[22, 28, 25, 33, 11, 26], [12, 22, 28, 25, 26], [16, 16, 28, 22], [20, 20, 22, 16]]

colors = ['#0066FF', '#FF0000', '#33D357', '#F7D02C', '#9966FF', '#FF9900']
highlighted = ['#003d99', '#990000', '#1e7e34', '#947c1a', '#5b3d99', '#995b00']


def format_name(name):
    return name.replace("_", " ").replace("[", " ").replace("]", " ").replace("'", " ").title()


def format_value(value):
    if pandas.isnull(value):
        return 'N/A'
    elif isinstance(value, float):
        return "{:,}".format(int(value))
    else:
        return value


@app.callback([Output(component_id='slct_ship', component_property='options'),
               Output(component_id='slct_ship', component_property='value')],
              [Input(component_id='slct_type', component_property='value')])
def update_options(type):
    return [{'label': ship, 'value': ship} for ship in all[type].index], all[type].index[0]


def pick_color(same, selected, index):
    return list(map(lambda name: colors[index] if name == selected else highlighted[index], same))


def pick_graph_colors(all, sub, num):
    terrains = sub.split(", ")
    return list(map(lambda name: colors[num] if name in terrains else highlighted[num], all))


def count_occurences(type, ):
    planets['terrain'].str.split(", ").dropna().sum()


@app.callback([Output("vehicle_info", "children"),
               Output(component_id='compare_graph', component_property='figure'),
               Output("planet_info", "children"),
               Output(component_id='terrain_graph', component_property='figure'),
               Output(component_id='climate_graph', component_property='figure'),
               Output("character_info", "children"),
               Output(component_id='hair_graph', component_property='figure'),
               Output(component_id='skin_graph', component_property='figure'),
               Output(component_id='eye_graph', component_property='figure'),
               Output(component_id='homeworld_graph', component_property='figure')],
              [Input("my_interval", "n_intervals"),
               Input(component_id='slct_type', component_property='value'),
               Input(component_id='slct_ship', component_property='value'),
               Input(component_id='slct_planet', component_property='value'),
               Input(component_id='slct_character', component_property='value')])
def update_weather_div(n, type, ship, planet, character):
    type_class = all[type].loc[ship, all_class[type]]
    same_class = all[type][all[type][all_class[type]] == type_class]

    compare_fig = make_subplots(rows=2, cols=3, vertical_spacing=0.3)

    labels = ["cost_in_credits", "length", "max_atmosphering_speed", "cargo_capacity", "crew", "passengers"]
    for index, label in enumerate(labels):
        chart_colors = pick_color(same_class.index, ship, index)
        compare_fig.add_trace(go.Bar(x=same_class.index, y=same_class[label],
                                     hovertext=same_class[label], marker_color=chart_colors,
                                     name=label.replace("_", " ").title()), row=int(index / 3) + 1, col=index % 3 + 1)
    compare_fig.update_layout(title_text='Compare within Same Class', template="plotly_dark", height=800)

    # Terrain
    terrains = planets['terrain'].str.split(", ").dropna()
    types = pandas.Series(terrains.sum(), name='Type').to_frame()
    types['Count'] = 1
    types = types.groupby(by='Type').sum()['Count'].reset_index()
    terrain_colors = pick_graph_colors(types['Type'], str(planets.loc[planet, 'terrain']), 0)
    types['Type'] = types['Type'].apply(lambda name: name.title())

    terrain_fig = go.Figure(
        [go.Bar(x=types['Type'], y=types['Count'], hovertext=types['Type'], marker_color=terrain_colors)])
    terrain_fig.update_layout(title_text='Terrains', template="plotly_dark")

    # Climate
    climates = planets['climate'].str.split(", ").dropna()
    types = pandas.Series(climates.sum(), name='Type').to_frame()
    types['Count'] = 1
    types = types.groupby(by='Type').sum()['Count'].reset_index()
    climate_colors = pick_graph_colors(types['Type'], str(planets.loc[planet, 'climate']), 1)
    types['Type'] = types['Type'].apply(lambda name: name.title())

    climate_fig = go.Figure(
        [go.Bar(x=types['Type'], y=types['Count'], hovertext=types['Type'], marker_color=climate_colors)])
    climate_fig.update_layout(title_text='Climates', template="plotly_dark")

    # Hair Color
    hair = characters['hair_color'].str.split(", ").dropna()
    types = pandas.Series(hair.sum(), name='Type').to_frame()
    types['Count'] = 1
    types = types.groupby(by='Type').sum()['Count'].reset_index()
    hair_colors = pick_graph_colors(types['Type'], str(characters.loc[character, 'hair_color']), 2)
    types['Type'] = types['Type'].apply(lambda name: name.title())

    hair_fig = go.Figure(
        [go.Bar(x=types['Type'], y=types['Count'], hovertext=types['Type'], marker_color=hair_colors)])
    hair_fig.update_layout(title_text='Hair Color', template="plotly_dark")

    # Skin Color
    skin = characters['skin_color'].str.split(", ").dropna()
    types = pandas.Series(skin.sum(), name='Type').to_frame()
    types['Count'] = 1
    types = types.groupby(by='Type').sum()['Count'].reset_index()
    skin_colors = pick_graph_colors(types['Type'], str(characters.loc[character, 'skin_color']), 3)
    types['Type'] = types['Type'].apply(lambda name: name.title())

    skin_fig = go.Figure(
        [go.Bar(x=types['Type'], y=types['Count'], hovertext=types['Type'], marker_color=skin_colors)])
    skin_fig.update_layout(title_text='Skin Color', template="plotly_dark")

    # Eye Color
    eyes = characters['eye_color'].str.split(", ").dropna()
    types = pandas.Series(eyes.sum(), name='Type').to_frame()
    types['Count'] = 1
    types = types.groupby(by='Type').sum()['Count'].reset_index()
    eye_colors = pick_graph_colors(types['Type'], str(characters.loc[character, 'eye_color']), 4)
    types['Type'] = types['Type'].apply(lambda name: name.title())

    eye_fig = go.Figure(
        [go.Bar(x=types['Type'], y=types['Count'], hovertext=types['Type'], marker_color=eye_colors)])
    eye_fig.update_layout(title_text='Eye Color', template="plotly_dark")

    # Homeworld
    homeworld = characters['homeworld'].str.split(", ").dropna()
    types = pandas.Series(homeworld.sum(), name='Type').to_frame()
    types['Count'] = 1
    types = types.groupby(by='Type').sum()['Count'].reset_index()
    home_colors = pick_graph_colors(types['Type'], str(characters.loc[character, 'homeworld']), 5)
    types['Type'] = types['Type'].apply(lambda name: name.title())

    homeworld_fig = go.Figure(
        [go.Bar(x=types['Type'], y=types['Count'], hovertext=types['Type'], marker_color=home_colors)])
    homeworld_fig.update_layout(title_text='Homeworld', template="plotly_dark")

    return update_table(n, type, ship), compare_fig, update_table(n, 2, planet), terrain_fig, \
           climate_fig, update_table(n, 3, character), hair_fig, skin_fig, eye_fig, homeworld_fig


def update_table(n, type, selected):
    return ([
        html.Div([
            html.Table(
                className="table-info",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.Div([
                                        html.Div([
                                            format_name(name)
                                        ], style={'width': f'{width}%', 'fontWeight': 'bold'}),
                                        html.Div([
                                            format_value(data)
                                        ], style={'width': f'{100 - width}%', 'textAlign': 'right', 'fontSize': 18})
                                    ], className='row')
                                ], style={"padding": '6px 30px', 'width': '50%'}),
                            html.Td(
                                children=[
                                    html.Div([
                                        html.Div([
                                            format_name(name2)
                                        ], style={'width': f'{width2}%', 'fontWeight': 'bold'}),
                                        html.Div([
                                            format_value(data2)
                                        ], style={'width': f'{100 - width2}%', 'textAlign': 'right', 'fontSize': 18})
                                    ], className='row')
                                ], style={"padding": '6px 30px', 'width': '50%'})
                        ]
                    )
                    for name, data, width, name2, data2, width2
                    in zip(categories_left[type], all[type].loc[selected, categories_left[type]], name_width_left[type],
                           categories_right[type], all[type].loc[selected, categories_right[type]],
                           name_width_right[type])
                ], style={'fontSize': 20, 'width': '90%', 'margin': 'auto', 'color': 'white',
                          'backgroundColor': '#222222', 'borderRadius': '10px'})
        ], style={'marginTop': 30})
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
    ], style={'height': 20}),
    dbc.Row([
        html.Div([
            html.Img(
                src='https://static.wixstatic.com/media/f94624_7cd22cb4e9b343b99b0b182dfd2ca815~mv2.png',
                style={'width': 300, "position": 'relative', 'zIndex': 10, 'margin': "0px 5px"}),
        ], style={'textAlign': 'right', 'margin': "48px 0px 10px", "width": '40%'}),
        html.Div([
            html.Img(
                src='https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Star_wars2.svg/1200px-Star_wars2.svg.png',
                style={'-webkit-filter': 'invert(100%)', 'width': 250, "position": 'relative',
                       'zIndex': 10, 'margin': "0px 5px"}),
        ], style={'textAlign': 'center', 'margin': "0px 0px 10px", "width": '20%'}),
        html.Div([
            html.Img(
                src='https://static.wixstatic.com/media/f94624_0d521d1e904d4e32adca369f4a172e12~mv2.png',
                style={'width': 300, "position": 'relative', 'zIndex': 10, 'margin': "0px 5px"}),
        ], style={'textAlign': 'left', 'margin': "48px 0px 10px", "width": '40%'})
    ]),
    html.H2("Transportation Info", style={"color": 'white', "margin": '40px 30px 10px'}),
    html.Div([
        html.Table(
            className="table-pokemon",
            children=[
                html.Tr(
                    children=[
                        html.Td(
                            children=[
                                dcc.Dropdown(
                                    id="slct_type",
                                    options=[{'label': type.title(), 'value': index} for index, type in
                                             enumerate(['starship', 'vehicle'])],
                                    multi=False,
                                    value=0,
                                    clearable=False
                                )], style={'width': '50px', "padding": '5px 10px'}
                        ),
                        html.Td(
                            children=[
                                dcc.Dropdown(
                                    id="slct_ship",
                                    options=[{'label': ship, 'value': ship} for ship in starships.index],
                                    multi=False,
                                    value='V-wing',
                                    clearable=False
                                )], style={'width': '100px', "padding": '5px 10px'})
                    ], style={"columnCount": 2, 'width': '100%'})
            ], style={'width': '35%', 'margin': 'auto', 'marginTop': '20px'})
    ]),
    html.Div([
        html.Div(id="vehicle_info", children="")
    ]),
    dcc.Graph(id='compare_graph', config={'displayModeBar': False}),
    html.H2("Planet Info", style={"color": 'white', "margin": '20px 30px 10px'}),
    html.Div([
        dcc.Dropdown(
            id="slct_planet",
            options=[{'label': planet, 'value': planet} for planet in planets.index],
            multi=False,
            value='Alderaan',
            clearable=False)
    ], style={'width': '30%', 'margin': 'auto', 'marginTop': 30}),
    html.Div([
        html.Div(id="planet_info", children="")
    ]),
    dbc.Row([
        html.Div([
            dcc.Graph(id='terrain_graph', config={'displayModeBar': False}),
            html.Div(style={'height': 24})
        ], style={"width": '72.375%'}),
        dcc.Graph(id='climate_graph', config={'displayModeBar': False},
                  style={"width": '27.625%', 'marginLeft': '-60px'})
    ], style={'marginLeft': '40px'}),
    html.H2("Character Info", style={"color": 'white', "margin": '20px 30px 10px'}),
    html.Div([
        dcc.Dropdown(
            id="slct_character",
            options=[{'label': character, 'value': character} for character in characters.index],
            multi=False,
            value='Luke Skywalker',
            clearable=False)
    ], style={'width': '30%', 'margin': 'auto', 'marginTop': 30}),
    html.Div([
        html.Div(id="character_info", children="")
    ]),
    dbc.Row([
        html.Div([
            dcc.Graph(id='hair_graph', config={'displayModeBar': False}),
            html.Div(style={'height': 32})
        ], style={"width": '50%'}),
        dcc.Graph(id='skin_graph', config={'displayModeBar': False}, style={"width": '50%'}),
    ]),
    dbc.Row([
        html.Div([
            dcc.Graph(id='eye_graph', config={'displayModeBar': False}),
            html.Div(style={'height': 42})
        ], style={"width": '40%'}),
        dcc.Graph(id='homeworld_graph', config={'displayModeBar': False}, style={"width": '60%'}),
    ])
], style={'backgroundColor': '#111111'})

if __name__ == '__main__':
    app.run_server(debug=True)
