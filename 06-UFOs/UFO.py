import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

df = pandas.read_csv("ufo_data.csv", dtype={'datetime': str, 'city': str, 'state': str,
                                            'shape': str, 'duration (seconds)': str, 'duration (hours/min)': str,
                                            'comments': str, 'date posted': str, 'latitude': str, 'longitude': str})
df['datetime'] = df['datetime'].str.replace('24:00', '0:00')
df['datetime'] = pandas.to_datetime(df['datetime'], format='%m/%d/%Y %H:%M')
df['date posted'] = pandas.to_datetime(df['date posted'], format='%m/%d/%Y')
df['year'] = pandas.DatetimeIndex(df['datetime']).year

di = {"au": "AUS", "ca": "CAN", "de": "DEU", "gb": "GBR", "us": "USA"}
df.replace({"country": di}, inplace=True)


@app.callback(
    [Output(component_id='world_graph', component_property='figure'),
     Output(component_id='us_graph', component_property='figure'),
     Output(component_id='us_year_chart', component_property='figure')],
    [Input("my_interval", "n_intervals"),
     Input(component_id='date_slider', component_property='value')])
def update_top_graph(n, year):
    usa_data = df.copy()
    usa_data = usa_data[usa_data["year"].between(df["year"].min(), year, inclusive=True)]
    usa_data = usa_data.groupby(['state']).count()['datetime']

    world_data = df.copy()
    world_data = world_data[world_data["year"].between(df["year"].min(), year, inclusive=True)]
    world_data = world_data.groupby(['country']).count()['datetime']

    usa_by_year = df.copy()
    usa_by_year = usa_by_year[usa_by_year["country"] == "USA"]
    usa_by_year = usa_by_year.groupby(['year']).count()[['datetime','country']]
    usa_by_year['sightings'] = usa_by_year['datetime']
    print(usa_by_year)

    fig = go.Figure(data=go.Choropleth(
        locations=usa_data.index.str.upper(),
        z=usa_data,
        locationmode='USA-states',
        colorbar_title="# of Encounters",
        colorscale=px.colors.sequential.Cividis_r
    ))

    fig.update_layout(
        geo_scope='usa',
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title_text='Encounter Locations (USA)',
        dragmode=False
    )

    fig2 = go.Figure(data=go.Choropleth(
        locations=world_data.index,
        z=world_data,
        colorbar_title="# of Encounters",
        colorscale=px.colors.sequential.Cividis_r
    ))

    fig2.update_layout(
        geo_scope='world',
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title_text='Encounter Locations (World)',
        dragmode=False
    )

    fig3 = px.bar(usa_by_year, x=usa_by_year.index, y=usa_by_year['sightings'], color=usa_by_year['sightings'],
                  title='Sightings in the USA by year', color_continuous_scale=px.colors.sequential.Cividis_r)

    return fig, fig2, fig3


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=300 * 1000,
        max_intervals=100,
    ),
    html.H1('UFO Sightings', style={'padding': '20px', 'textAlign': 'center', 'color': 'black', 'fontSize': 40}),
    html.Div([
        html.Img(src='https://static.wixstatic.com/media/f94624_2bbdaaf1395e4965859f9e9944bb8f60~mv2.png',
                 style={'width': 100})
    ], style={'textAlign': 'center', 'margin': "-25px 0px 40px"}),
    dbc.Row([
        html.Div([
            dcc.Graph(id='world_graph', config={'displayModeBar': False}),
        ], style={"width": '50%'}),
        html.Div([
            dcc.Graph(id='us_graph', config={'displayModeBar': False}),
        ], style={"width": '50%'})
    ], style={'marginTop': '-10px'}),
    html.Div([
        dcc.Slider(
            id='date_slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].max(),
            marks={str(year): str(year) for year in range(df['year'].min(), df['year'].max(), 5)},
            updatemode='drag'
        )
    ], style={'width': "80%", 'margin': '0 auto', 'background-color': ''}),
    dcc.Graph(id='us_year_chart', config={'displayModeBar': False}),
])

if __name__ == '__main__':
    app.run_server(debug=True)