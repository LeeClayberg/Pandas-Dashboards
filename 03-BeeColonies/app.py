import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

server = app.server

# Data
df = pd.read_csv("intro_bees.csv")
df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)

# Layout
app.layout = html.Div([
    html.Div(id='output_container',
             style={'textAlign': 'center', 'color': 'white', 'backgroundColor': '#111111',
                    'fontSize': 30, 'padding': '30px 0'}),
    dcc.Dropdown(
        id="slct_year",
        options=[
            {'label': '2015', 'value': 2015},
            {'label': '2016', 'value': 2016},
            {'label': '2017', 'value': 2017},
            {'label': '2018', 'value': 2018}
        ],
        multi=False,
        value=2015,
        style={'width': "30%", 'position': 'absolute', 'zIndex': 2,
               'top': 10, 'left': 10}
    ),
    dcc.Dropdown(
        id="slct_affect",
        options=[{'label': affect.replace("_", " ").title(), 'value': affect} for affect in df['Affected by'].unique()],
        multi=False,
        value='Varroa_mites',
        style={'width': "32%", 'position': 'absolute', 'zIndex': 1,
               'top': 10, 'left': 80}
    ),
    dcc.Graph(id='my_bee_map', config={'displayModeBar': False}),
    dcc.Graph(id='my_bee_state_chart', config={'displayModeBar': False}),
    dcc.Graph(id='my_bee_affect_chart', config={'displayModeBar': False})
])


# Connection to Plotly graphs
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure'),
     Output(component_id='my_bee_state_chart', component_property='figure'),
     Output(component_id='my_bee_affect_chart', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'),
     Input(component_id='slct_affect', component_property='value')])
def update_graph(year_slctd, affect_slctd):
    container = "Bee Colonies Impacted by {} ({})".format(affect_slctd.replace("_", " ").title(), year_slctd)

    dff = df.copy()
    dff = dff[dff["Year"] == year_slctd]
    dff = dff[dff["Affected by"] == affect_slctd]

    dff2 = df.copy()
    dff2 = dff2[dff2["Year"] == year_slctd]

    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope='usa',
        color='Pct of Colonies Impacted',
        hover_data=['State', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        template='plotly_dark'
    )

    fig.update_layout(
        dragmode=False
    )

    fig2 = px.bar(
        data_frame=dff.sort_values(by=['Pct of Colonies Impacted']),
        x='State',
        y='Pct of Colonies Impacted',
        color='Pct of Colonies Impacted',
        color_continuous_scale=px.colors.sequential.Blues,
        template='plotly_dark'
    )

    fig3 = px.bar(
        data_frame=dff2.groupby("Affected by", as_index=False).mean().sort_values(by=['Pct of Colonies Impacted']),
        x='Affected by',
        y='Pct of Colonies Impacted',
        color='Pct of Colonies Impacted',
        color_continuous_scale=px.colors.sequential.Blues,
        template='plotly_dark'
    )

    return container, fig, fig2, fig3


if __name__ == '__main__':
    app.run_server(debug=True)
