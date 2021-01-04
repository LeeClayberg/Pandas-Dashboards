import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

dateparse = lambda x: datetime.strptime(x, '%m/%d/%Y')
df = pandas.read_csv("superbowl_data.csv", parse_dates=['Date'], date_parser=dateparse)

colors = ['#FFFFFF', '#4F99C8']
colors2 = ['#E0ECF7', '#BBD6EA', '#8DC0DC', '#559ECA', '#2F7BB8', '#13579D']


@app.callback(
    [Output(component_id='location_graph', component_property='figure'),
     Output(component_id='points_graph', component_property='figure'),
     Output(component_id='team_wins_graph', component_property='figure'),
     Output(component_id='mvp_graph', component_property='figure')],
    [Input("my_interval", "n_intervals")])
def update_top_graph(n):
    map_data = df.groupby(['Abbreviation']).count()['State']

    points = df.sort_values(by=['Date'])

    team_wins = df.groupby(['Winner']).count()['State'].sort_values(ascending=True)
    win_colors = team_wins.apply(lambda x: colors2[x - 1])

    mvp_wins = df.groupby(['MVP']).count()['State'].sort_values(ascending=True)
    mvp_colors = mvp_wins.apply(lambda x: colors2[x - 1])

    points_fig = go.Figure()
    points_fig.add_trace(go.Bar(x=points['Date'], y=points['Winner Pts'], hovertext=points['Winner'],
                                name='Winner', marker_color=colors[0]))
    points_fig.add_trace(go.Bar(x=points['Date'], y=points['Loser Pts'], hovertext=points['Loser'],
                                name='Loser', marker_color=colors[1]))
    points_fig.update_layout(title_text='Ending Points', template="plotly_dark")

    wins_fig = go.Figure(go.Bar(x=team_wins.index, y=team_wins, marker_color=win_colors))
    wins_fig.update_layout(title_text='Total Team Wins', template="plotly_dark")

    mvp_fig = go.Figure(go.Bar(x=mvp_wins.index, y=mvp_wins, marker_color=mvp_colors))
    mvp_fig.update_layout(title_text='MVP Wins', template="plotly_dark")

    fig = go.Figure(data=go.Choropleth(
        locations=map_data.index,
        z=map_data,
        locationmode='USA-states',
        colorbar_title="# of Times",
        colorscale=px.colors.sequential.Blues
    ))

    fig.update_layout(
        geo_scope='usa',
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title_text='Superbowl Locations',
        template="plotly_dark",
        dragmode=False
    )

    return fig, points_fig, wins_fig, mvp_fig


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=300 * 1000,
        max_intervals=100,
    ),
    html.H1('Superbowls', style={'padding': '20px', 'textAlign': 'center', 'color': 'white', 'fontSize': 40}),
    html.Div([
        html.Img(src='https://i.pinimg.com/originals/7f/45/c4/7f45c4af3a9aff4df87a4b6539c7466c.png',
                 style={'-webkit-filter': 'invert(100%)', 'width': 20, "position": 'relative',
                        'zIndex': 10, 'margin': "0px 5px"}),
        html.Img(src='https://i.pinimg.com/originals/7f/45/c4/7f45c4af3a9aff4df87a4b6539c7466c.png',
                 style={'-webkit-filter': 'invert(100%)', 'width': 20, "position": 'relative',
                        'zIndex': 10, 'margin': "0px 5px"}),
        html.Img(src='https://i.pinimg.com/originals/7f/45/c4/7f45c4af3a9aff4df87a4b6539c7466c.png',
                 style={'-webkit-filter': 'invert(100%)', 'width': 20, "position": 'relative',
                        'zIndex': 10, 'margin': "0px 5px"}),
    ], style={'textAlign': 'center', 'margin': "-25px 0px 10px"}),
    dbc.Row([
        html.Div([
            dcc.Graph(id='points_graph', config={'displayModeBar': False}),
        ], style={"width": '65%'}),
        html.Div([
            dcc.Graph(id='team_wins_graph', style={'height': 500}, config={'displayModeBar': False}),
        ], style={"width": '34%'})
    ], style={'marginTop': '-30px'}),
    dbc.Row([
        html.Div([
            dcc.Graph(id='mvp_graph', config={'displayModeBar': False})
        ], style={"width": '40%'}),
        html.Div([
            dcc.Graph(id='location_graph', config={'displayModeBar': False})
        ], style={"width": '55%'})
    ], style={'marginTop': '-30px'})
], style={'backgroundColor': '#111111'})

if __name__ == '__main__':
    app.run_server(debug=True)
