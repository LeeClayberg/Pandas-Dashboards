import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas
import plotly.graph_objects as go
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

df = pandas.read_csv("pokemon.csv")
df.loc[df['Name'].str.contains('Mega|Primal'), 'Name'] = df['Name'].str.split("Mega|Primal").str[1]
# df.rename(columns={'SpAtk': 'Special Attack', 'SpDef': 'Special Defense'}, inplace=True)

colors = ['#A6B91A', '#705746', '#6F35FC', '#F7D02C', '#D685AD', '#C22E28', '#EE8130', '#A98FF3', '#735797', '#7AC74C',
          '#E2BF65', '#96D9D6', '#A8A77A', '#A33EA1', '#F95587', '#B6A136', '#B7B7CE', '#6390F0', ]

gen_colors = ['#3366cc', '#dc3912', '#ff9900', '#109618', '#990099', '#0099c6']


def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return int(minimum)
    if val > maximum:
        return int(maximum)
    return int(val)


def color_scale(hex_str, scale_factor):
    hex_str = hex_str.strip('#')

    if scale_factor < 0 or len(hex_str) != 6:
        return hex_str

    r, g, b = int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:], 16)

    r = clamp(r * scale_factor)
    g = clamp(g * scale_factor)
    b = clamp(b * scale_factor)

    return "#%02x%02x%02x" % (r, g, b)


gen_colors_2 = list(map(lambda x: color_scale(x, 0.8), gen_colors))
gen_colors_3 = list(map(lambda x: color_scale(x, 0.6), gen_colors))


@app.callback(
    [Output(component_id='hp_graph', component_property='figure'),
     Output(component_id='attack_graph', component_property='figure'),
     Output(component_id='defense_graph', component_property='figure'),
     Output(component_id='legendary_graph', component_property='figure')],
    [Input("my_interval", "n_intervals")])
def update_top_graph(n):
    hp_type1 = df.groupby(['Type1']).mean()['HP']
    hp_type2 = df.groupby(['Type2']).mean()['HP']
    hp_average = pandas.concat([hp_type1, hp_type2], axis=0).groupby(level=0).mean()
    attack_type1 = df.groupby(['Type1']).mean()['Attack']
    attack_type2 = df.groupby(['Type2']).mean()['Attack']
    attack_average = pandas.concat([attack_type1, attack_type2], axis=0).groupby(level=0).mean()
    defense_type1 = df.groupby(['Type1']).mean()['Defense']
    defense_type2 = df.groupby(['Type2']).mean()['Defense']
    defense_average = pandas.concat([defense_type1, defense_type2], axis=0).groupby(level=0).mean()

    legendary = df.loc[df['Legendary'] & ~df['Name'].str.contains('Mega|Primal', na=False)]
    legendary['Color1'] = df['Generation'].apply(lambda x: gen_colors[x - 1])
    legendary['Color2'] = df['Generation'].apply(lambda x: gen_colors_2[x - 1])
    legendary['Color3'] = df['Generation'].apply(lambda x: gen_colors_3[x - 1])

    hp_fig = go.Figure([go.Bar(x=hp_average.index, y=hp_average, marker_color=colors, hovertext=hp_average)])
    hp_fig.update_layout(title_text='HP Average', height=350)
    attack_fig = go.Figure(
        [go.Bar(x=attack_average.index, y=attack_average, marker_color=colors, hovertext=attack_average)])
    attack_fig.update_layout(title_text='Attack Average', height=350)
    defense_fig = go.Figure(
        [go.Bar(x=defense_average.index, y=defense_average, marker_color=colors, hovertext=defense_average)])
    defense_fig.update_layout(title_text='Defense Average', height=350)

    legendary_fig = go.Figure()
    legendary_fig.add_trace(go.Bar(x=legendary['Name'], y=legendary['HP'], name='HP', marker_color=legendary['Color1']))
    legendary_fig.add_trace(
        go.Bar(x=legendary['Name'], y=legendary['Attack'], name='Attack', marker_color=legendary['Color2']))
    legendary_fig.add_trace(
        go.Bar(x=legendary['Name'], y=legendary['Defense'], name='Defense', marker_color=legendary['Color3']))
    legendary_fig.update_layout(title_text='Regular Legendary Stats', height=450)

    return hp_fig, attack_fig, defense_fig, legendary_fig


@app.callback(
    [Output(component_id='compare_graph', component_property='figure'),
     Output(component_id='compare_pie', component_property='figure')],
    [Input(component_id='gen_selector', component_property='value'),
     Input(component_id='type_selector', component_property='value'),
     Input(component_id='stat_selector', component_property='value')])
def update_top_graph(gens, types, stats):
    compare_graph = df.copy()

    compare_fig = go.Figure(layout={'title_text': 'Compare Pokemon'})
    if (gens is None) or (types is None) or (stats is None):
        return compare_fig

    compare_graph = compare_graph.loc[compare_graph['Generation'].isin(gens)]
    compare_graph = compare_graph.loc[compare_graph['Type1'].isin(types) | compare_graph['Type2'].isin(types)]

    for index, stat in enumerate(stats):
        compare_fig.add_trace(go.Bar(x=compare_graph['Name'], y=compare_graph[stat], name=stat,
                                     marker_color=gen_colors[index]))

    compare_gen = compare_graph.groupby(['Generation']).mean()
    compare_pie_fig = go.Figure(layout={'title_text': 'Compare by Generation'})
    if len(stats) != 0:
        interval = 1 / len(stats)
    else:
        interval = 1
    domains = [{'x': [round(n / len(stats), 2) + 0.02, round(n / len(stats) + interval, 2) - 0.02], 'y': [0.0, 1.0]} for
               n, stat in enumerate(stats)]
    print(compare_gen)
    for index, stat in enumerate(stats):
        compare_pie_fig.add_trace(go.Pie(labels=compare_gen.index.map('Generation {}'.format), values=compare_gen[stat],
                                         domain=domains[index], name=stat, title=stat, hole=.4))

    compare_pie_fig.update_traces(hoverinfo='label+percent', textfont_size=16, marker=dict(colors=gen_colors))

    return compare_fig, compare_pie_fig


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=300 * 1000,
        max_intervals=100,
    ),
    html.H1('Pokémon Stats', style={'padding': '20px', 'textAlign': 'center'}),
    html.Div([
        html.Div([
            dcc.Graph(id='hp_graph', config={'displayModeBar': False})
        ]),
        html.Div([
            dcc.Graph(id='attack_graph', config={'displayModeBar': False})
        ]),
        html.Div([
            dcc.Graph(id='defense_graph', config={'displayModeBar': False})
        ])
    ], style={"columnCount": 3, 'marginTop': '-30px'}),
    html.Div([
        dcc.Graph(id='legendary_graph', config={'displayModeBar': False})
    ]),
    html.Div([
        html.Table(
            className="table-pokemon",
            children=[
                html.Tr(
                    children=[
                        html.Td(
                            children=[
                                dcc.Dropdown(
                                    id='gen_selector',
                                    options=[{'label': "Gen " + str(gen), 'value': gen} for gen in
                                             df['Generation'].unique()],
                                    placeholder="Select a Generation(s)",
                                    value=[1, 2, 3],
                                    multi=True
                                )
                            ], style={'width': '300px', "padding": '5px 30px'}
                        ),
                        html.Td(
                            children=[
                                dcc.Dropdown(
                                    id='type_selector',
                                    options=[{'label': p_type, 'value': p_type} for p_type in df['Type1'].unique()],
                                    placeholder="Select a Type(s)",
                                    value=['Flying'],
                                    multi=True
                                )
                            ], style={'width': '300px', "padding": '5px 30px'}
                        ),
                        html.Td(
                            children=[
                                dcc.Dropdown(
                                    id='stat_selector',
                                    options=[{'label': p_type, 'value': p_type} for p_type in list(df.columns)[4:10]],
                                    placeholder="Select a Stat(s)",
                                    value=['HP', 'Attack', 'Defense'],
                                    multi=True
                                )
                            ], style={'width': '300px', "padding": '5px 30px'}
                        )
                    ], style={"columnCount": 3, 'width': '100%'})
            ], style={'width': '80%', 'margin': 'auto', 'color': 'black', 'paddingTop': '30px',
                      'backgroundColor': 'white', 'borderRadius': '10px', 'marginTop': '20px'})
    ]),
    html.Div([
        dcc.Graph(id='compare_graph', config={'displayModeBar': False})
    ]),
    html.Div([
        dcc.Graph(id='compare_pie', config={'displayModeBar': False})
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)
