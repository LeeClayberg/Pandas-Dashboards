from dash import Dash, html, dcc
import math
import dash_bootstrap_components as dbc
import pandas
import plotly.graph_objects as go
from dash.dependencies import Input, Output

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

server = app.server

colors = ['#3399FF', '#FF3300']
weight_class_order = [6, 13, 7, 5, 12, 11, 8, 10, 9, 3, 4, 2, 1]

# https://www.kaggle.com/mdabbert/ultimate-ufc-dataset?select=ufc-master.csv
df = pandas.read_csv("ufc-master.csv")
df['Winner_Name'] = df[['R_fighter', 'B_fighter', 'Winner']].apply(
    lambda row: row['R_fighter'] if row['Winner'] == 'Red' else row['B_fighter'], axis=1)
df['Loser_Name'] = df[['R_fighter', 'B_fighter', 'Winner']].apply(
    lambda row: row['B_fighter'] if row['Winner'] == 'Red' else row['R_fighter'], axis=1)
df['date'] = pandas.to_datetime(df['date'], format='%m/%d/%Y')
df['year'] = pandas.DatetimeIndex(df['date']).year
df['month'] = pandas.DatetimeIndex(df['date']).month
df['day'] = 1

# Top fighters
top20men = df.loc[df['gender'] == 'MALE'].groupby('Winner_Name').count()['location']\
    .sort_values().tail(20).reset_index()
top20women = df.loc[df['gender'] == 'FEMALE'].groupby('Winner_Name').count()['location']\
    .sort_values().tail(20).reset_index()

# Fight time
fight_times = df.loc[df['total_fight_time_secs'].notna()]
fight_times['time_range'] = fight_times['total_fight_time_secs'].apply(lambda x: math.ceil(x / 10) * 10)
fight_times = fight_times.groupby('time_range').count()['location'].reset_index().sort_values(by='time_range')
fight_times = fight_times.loc[fight_times['time_range'] < 900]

# Favored wins
favored_red_wins = df.loc[df['R_odds'] < 0].groupby('Winner').count()['location'].reset_index().assign(Winner=['Lost', 'Won'])
favored_blue_wins = df.loc[df['B_odds'] < 0].groupby('Winner').count()['location'].reset_index().assign(Winner=['Won', 'Lost'])

# Weight class breakdown
weight_classes = df.groupby('weight_class').count()['location'].reset_index()
weight_classes['order'] = weight_class_order
weight_classes = weight_classes.sort_values(by='order')
weight_classes['color'] = weight_classes['weight_class'].apply(lambda word: colors[1] if 'Women' in word else colors[0])

# Win & lose streaks
red_streaks = df[['R_fighter', 'R_current_win_streak', 'R_current_lose_streak']].\
    rename(columns={"R_fighter": "fighter", "R_current_win_streak": "wins", "R_current_lose_streak": "losses"})
blue_streaks = df[['B_fighter', 'B_current_win_streak', 'B_current_lose_streak']].\
    rename(columns={"B_fighter": "fighter", "B_current_win_streak": "wins", "B_current_lose_streak": "losses"})
streaks = pandas.concat([red_streaks, blue_streaks])
highest_win_streak = streaks[['fighter', 'wins']].groupby('fighter').max().sort_values(by='wins').tail(5).reset_index()
highest_lose_streak = streaks[['fighter', 'losses']].groupby('fighter').max().sort_values(by='losses').tail(5).reset_index()

# Month Fight Data
fights_per_day = df.groupby(['year', 'month']).count()['location'].reset_index()
fights_per_day['day'] = 1
fights_per_day['label'] = pandas.to_datetime(fights_per_day[['year', 'month', 'day']]).apply(lambda x: x.strftime('%b %Y'))

# Highest win average
wins = df.groupby('Winner_Name').count()['location'].reset_index().rename(columns={"Winner_Name": "name", "location": "Wins"})
losses = df.groupby('Loser_Name').count()['location'].reset_index().rename(columns={"Loser_Name": "name", "location": "Losses"})
total = wins.merge(losses, on='name', how='outer')
total['Win_Average'] = total[['Wins', 'Losses']].apply(lambda row: round(row['Wins']/(row['Wins']+row['Losses']), 2), axis=1)
total = total.sort_values(by='Win_Average', ascending=False).head(100).sort_values(by='Wins')
print(total)


@app.callback([Output(component_id='top_20_men', component_property='figure'),
               Output(component_id='top_20_women', component_property='figure'),
               Output(component_id='favored_red', component_property='figure'),
               Output(component_id='favored_blue', component_property='figure'),
               Output(component_id='fight_time', component_property='figure'),
               Output(component_id='weight_class', component_property='figure'),
               Output(component_id='highest_win_streak', component_property='figure'),
               Output(component_id='highest_lose_streak', component_property='figure'),
               Output(component_id='date_graph', component_property='figure'),
               Output(component_id='average_graph', component_property='figure')],
              [Input("my_interval", "n_intervals")])
def update(n):
    top_men_fig = go.Figure(data=[
        go.Bar(x=top20men['Winner_Name'], y=top20men['location'], marker_color=colors[0])
    ])
    top_men_fig.update_layout(title="Top 20 Men", template="plotly_dark", yaxis_title="Wins")

    top_women_fig = go.Figure(data=[
        go.Bar(x=top20women['Winner_Name'], y=top20women['location'], marker_color=colors[1])
    ])
    top_women_fig.update_layout(title="Top 20 Women", template="plotly_dark", yaxis_title="Wins")

    favored_red_fig = go.Figure(
        data=[go.Pie(labels=favored_red_wins['Winner'], values=favored_red_wins['location'],
                     title="Favored Red", marker=dict(colors=colors))])
    favored_red_fig.update_layout(template="plotly_dark")

    favored_blue_fig = go.Figure(
        data=[go.Pie(labels=favored_blue_wins['Winner'], values=favored_blue_wins['location'],
                     title="Favored Blue", marker=dict(colors=colors))])
    favored_blue_fig.update_layout(template="plotly_dark")

    fight_time_fig = go.Figure(data=[
        go.Bar(x=fight_times['time_range'], y=fight_times['location'], marker_color=colors[0],
               name="Time(seconds)")
    ])
    fight_time_fig.add_trace(go.Scatter(
        x=[305, 605],
        y=[55, 55],
        text=["Round 1",
              "Round 2"],
        mode="text",
    ))
    fight_time_fig.update_traces(hovertemplate=None)
    fight_time_fig.update_layout(title="Fight Times Under the 15min Maximum", template="plotly_dark", showlegend=False,
                                 xaxis_title="Time(Seconds)", yaxis_title="# of Fights",
                                 shapes=[
                                    dict(type='line', yref='paper', y0=0, y1=0.925, xref='x', x0=305, x1=305),
                                    dict(type='line', yref='paper', y0=0, y1=0.925, xref='x', x0=605, x1=605)
                                 ])

    weight_class_fig = go.Figure(data=[
        go.Bar(x=weight_classes['weight_class'], y=weight_classes['location'], marker_color=weight_classes['color'])
    ])
    weight_class_fig.update_layout(title="Weight Class", template="plotly_dark", yaxis_title="# of Fights", xaxis_title="Weight Class")

    highest_win_streak_fig = go.Figure(data=[
        go.Bar(x=highest_win_streak['fighter'], y=highest_win_streak['wins'], marker_color=colors[1])
    ])
    highest_win_streak_fig.update_layout(title="Highest Win Streak", template="plotly_dark", yaxis_title="Win Streak", xaxis_title="Fighter")

    highest_lose_streak_fig = go.Figure(data=[
        go.Bar(x=highest_lose_streak['fighter'], y=highest_lose_streak['losses'], marker_color=colors[0])
    ])
    highest_lose_streak_fig.update_layout(title="Highest Lose Streak", template="plotly_dark", yaxis_title="Lose Streak", xaxis_title="Fighter")

    date_fig = go.Figure(data=[
        go.Bar(x=fights_per_day['label'], y=fights_per_day['location'], marker_color=colors[1])
    ])
    date_fig.update_layout(title="Fight Dates (by month)", template="plotly_dark", yaxis_title="# of Fights", xaxis_title="Date", xaxis=dict(nticks=12))

    average_fig = go.Figure(data=[
        go.Bar(name='Wins', x=total['name'], y=total['Wins'], marker_color=colors[0], hovertext=total['Win_Average']),
        go.Bar(name='Losses', x=total['name'], y=total['Losses'], marker_color='white')
    ])
    average_fig.update_layout(barmode='stack', title='Top 50 Highest Win Averages', template="plotly_dark")

    return top_men_fig, top_women_fig, favored_red_fig, favored_blue_fig, fight_time_fig, weight_class_fig, \
           highest_win_streak_fig, highest_lose_streak_fig, date_fig, average_fig


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=300 * 1000,
        max_intervals=100,
    ),
    dbc.Row([
        html.Div(style={"width": '40%'}),
        html.Div([
            html.Img(
                src='https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/UFC_logo.svg/640px-UFC_logo.svg.png',
                style={'-webkit-filter': 'invert(100%)', 'width': 200, "position": 'relative',
                       'zIndex': 10, 'margin': "15px 0px 5px"}),
        ], style={'textAlign': 'center', 'margin': "0px 0px 10px", "width": '20%'}),
        html.Div(style={"width": '40%'})
    ]),
    html.H4('MAR 2010 - Present', style={'marginTop': '-10px', 'textAlign': 'center', 'color': 'white',
                                         'fontSize': 20, 'font-family': 'Arial, Helvetica, sans-serif',
                                         'backgroundColor': '#111111'}),
    dbc.Row([
        html.Div([
            dcc.Graph(id='top_20_men', config={'displayModeBar': False})
        ], style={"width": '50%'}),
        html.Div([
            dcc.Graph(id='top_20_women', config={'displayModeBar': False})
        ], style={"width": '50%'}),
    ]),
    dbc.Row([
        html.Div([
            dcc.Graph(id='favored_red', config={'displayModeBar': False})
        ], style={"width": '27%'}),
        html.Div([
            dcc.Graph(id='favored_blue', config={'displayModeBar': False})
        ], style={"width": '27%'}),
        html.Div([
            dcc.Graph(id='fight_time', config={'displayModeBar': False})
        ], style={"width": '46%'}),
    ]),
    dbc.Row([
        html.Div([
            dcc.Graph(id='weight_class', config={'displayModeBar': False})
        ], style={"width": '33.3%'}),
        html.Div([
            dcc.Graph(id='highest_win_streak', config={'displayModeBar': False})
        ], style={"width": '33.4%'}),
        html.Div([
            dcc.Graph(id='highest_lose_streak', config={'displayModeBar': False})
        ], style={"width": '33.3%'}),
    ]),
    dcc.Graph(id='date_graph', config={'displayModeBar': False}),
    dcc.Graph(id='average_graph', config={'displayModeBar': False}),
    html.Div(style={'height': 100})
], style={'backgroundColor': '#111111'})

if __name__ == '__main__':
    app.run_server(debug=True)