import time
from datetime import date

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas
import pandas_datareader as dr
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from pandas_datareader._utils import RemoteDataError

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

twenty_years_ago = date.today()
twenty_years_ago = date(twenty_years_ago.year - 20, twenty_years_ago.month, twenty_years_ago.day)

dates = pandas.date_range(start='2020-01-01', end=date.today())
history = pandas.date_range(start=twenty_years_ago, end=date.today())

# Data
companies = pandas.read_csv("fortune_500.csv")
hq_states = companies.pivot_table(index=['Hqstate'], aggfunc='size')


# Update the graphs
@app.callback(
    [Output(component_id='close_graph', component_property='figure'),
     Output(component_id='change_graph', component_property='figure'),
     Output(component_id='close_title', component_property='children'),
     Output(component_id='change_title', component_property='children'),
     Output(component_id='historical_graph', component_property='figure'),
     Output(component_id='history_range', component_property='children'),
     Output(component_id='hq_location_graph', component_property='figure')],
    [Input(component_id='my_dropdown', component_property='value'),
     Input(component_id='date_slider', component_property='value')])
def update_graphs(dropdown_values, slider_value):
    selected_values = dropdown_values

    close_figure = go.Figure()
    change_figure = go.Figure()
    historical_figure = go.Figure()

    for value in selected_values:
        try:
            df = dr.DataReader(value, data_source='yahoo',
                               start=unix_to_datetime(slider_value[0]), end=unix_to_datetime(slider_value[1]))
            history_df = dr.DataReader(value, data_source='yahoo', start=history.min(), end=history.max())

            close_figure.add_trace(go.Scatter(x=df.index, y=df.Close, mode='lines', name=value))
            change_figure.add_trace(
                go.Scatter(x=df.index, y=df.Close - df.Open, mode='lines', name=value))
            historical_figure.add_trace(go.Scatter(x=history_df.index, y=history_df.Close, mode='lines', name=value))
        except KeyError:
            pass
        except RemoteDataError:
            pass

    date_range = str(unix_to_datetime(slider_value[0]).strftime('%b %d')) + " - " + str(
        unix_to_datetime(slider_value[1]).strftime('%b %d'))
    history_range = str(history.min().strftime('%b %d, %Y')) + " - " + str(history.max().strftime('%b %d, %Y'))

    fig = go.Figure(data=go.Choropleth(
        locations=hq_states.index,
        z=hq_states,
        locationmode='USA-states',
        colorscale='Cividis_r',
        colorbar_title="# of Company Headquarters"
    ))

    fig.update_layout(
        geo_scope='usa',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        dragmode=False
    )

    return close_figure, change_figure, date_range, date_range, historical_figure, history_range, fig


@app.callback(
    Output(component_id='my_dropdown', component_property='value'),
    [Input(component_id='sector_drop', component_property='value')],
    prevent_initial_call=True)
def update_graphs(sector):
    return companies[companies["Sector"] == sector]["Ticker"]


# Converts date into seconds
def unix_time_millis(dt):
    return int(time.mktime(dt.timetuple()))


# Converts seconds into the date
def unix_to_datetime(unix):
    return pandas.to_datetime(unix, unit='s')


# Creates the marks for the slider
def get_marks(count=5):
    result = {}
    for i, d in enumerate(dates):
        if i % int(len(dates) / count) == 0:
            result[unix_time_millis(d)] = str(d.strftime('%m/%d/%Y'))

    return result


app.layout = html.Div([
    html.H1('2020 Fortune 500 Stock Tracker', style={'padding': '20px', 'textAlign': 'center'}),
    dcc.Dropdown(
        id='my_dropdown',
        options=[{'label': company['Title'], 'value': company['Ticker']} for index, company in companies.iterrows()],
        value=[companies['Ticker'][0]],
        multi=True,
        style={'width': "90%", 'margin': '0 auto'}
    ),
    dcc.Dropdown(
        id='sector_drop',
        options=[{'label': sector, 'value': sector} for sector in companies['Sector'].unique()],
        placeholder="Select a Sector",
        style={'width': "40%", 'position': 'absolute', 'right': '6.75%', 'marginTop': '4px'}
    ),
    html.Div([
        html.Div([
            html.H4(children='Close Price', style={"margin": '20px 10px 0px', "position": 'relative', "zIndex": 10}),
            html.H6(id='close_title', style={"margin": '0px 10px 0px', "position": 'relative', "zIndex": 10}),
            dcc.Graph(id='close_graph', style={"margin-top": '-30px'}, config={'displayModeBar': False})
        ], style={"margin-top": '-20px', "padding-left": '20px'}),
        html.Div([
            html.H4(children='Price Change', style={"margin": '20px 10px 0px', "position": 'relative', "zIndex": 10}),
            html.H6(id='change_title', style={"margin": '0px 10px 0px', "position": 'relative', "zIndex": 10}),
            dcc.Graph(id='change_graph', style={"margin-top": '-30px'}, config={'displayModeBar': False})
        ], style={"padding-left": '20px'})
    ], style={"columnCount": 2, "padding-top": '20px', 'marginTop': '40px'}),
    html.Div([
        dcc.RangeSlider(
            id='date_slider',
            min=unix_time_millis(dates.min()),
            max=unix_time_millis(dates.max()),
            value=[unix_time_millis(dates.min()),
                   unix_time_millis(dates.max())],
            marks=get_marks(),
        )
    ], style={'width': "80%", 'margin': '0 auto'}),
    html.H4(children='Stock History (Last 20 years)',
            style={"margin": '50px 30px 0px', "position": 'relative', "zIndex": 10}),
    html.H6(id='history_range', style={"margin": '0px 30px 0px', "position": 'relative', "zIndex": 10}),
    dcc.Graph(id='historical_graph', config={'displayModeBar': False}, style={"margin-top": '-30px'}),
    html.H4(children='Company Headquarters', style={"margin": '50px 30px 30px', "position": 'relative', "zIndex": 10}),
    dcc.Graph(id='hq_location_graph', config={'displayModeBar': False}),
])

if __name__ == '__main__':
    app.run_server(debug=True)
