from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import pandas
import math
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px

# https://www.kaggle.com/ahsen1330/us-police-shootings

# colors = ['#2E9D80','#1A877F','#50B37C','#1A6E76','#AADA6E','#7BC875','#E8EC69']
colors = ['#50B37C', '#1A877F', '#2E9D80', '#1A6E76', '#7BC875', '#AADA6E', '#E8EC69']

external_stylesheets = [dbc.themes.LUX]
app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

df = pandas.read_csv("police_shootings_data.csv", index_col=0)
df['date'] = pandas.to_datetime(df['date'])
df['year'] = pandas.DatetimeIndex(df['date']).year
df['month'] = pandas.DatetimeIndex(df['date']).month

# Month data
month_data = df.groupby(['year', 'month']).count()['name'].reset_index()
month_data['day'] = 1
month_data['label'] = pandas.to_datetime(month_data[['year', 'month', 'day']]).apply(lambda x: x.strftime('%b %Y'))

# States
state_data = df.groupby('state').count()['name'].reset_index()

# Armed
armed_data = df.groupby('armed').count()['name'].reset_index()
over_three = armed_data.loc[armed_data['name'] > 100]
under_three = armed_data.loc[armed_data['name'] <= 100]
under_three['armed'] = 'other'
under_three = under_three.groupby('armed').count()['name'].reset_index()
armed_data = pandas.concat([over_three, under_three])

# Mental
mental_data = df.groupby('signs_of_mental_illness').count()['name'].reset_index()
mental_data['signs_of_mental_illness'] = mental_data['signs_of_mental_illness'].astype(str)

# Cities
city_data = df.groupby('city').count()['name'].reset_index().sort_values(by='name').tail(20).sort_values(by='city')

# Race
race_data = df.groupby('race').count()['name'].reset_index()

# Age
df['age range'] = df['age'].apply(lambda age: f"{math.floor(age / 10) * 10}'s")
age_data = df.groupby('age range').count()['name'].reset_index()

# Gender
gender_data = df.groupby('gender').count()['name'].reset_index()
gender_data['gender'] = gender_data['gender'].apply(lambda x: 'Female' if x == 'F' else 'Male')
print(gender_data)


@app.callback([Output(component_id='date_graph', component_property='figure'),
               Output(component_id='us_map', component_property='figure'),
               Output(component_id='armed_graph', component_property='figure'),
               Output(component_id='mental_illness_chart', component_property='figure'),
               Output(component_id='city_graph', component_property='figure'),
               Output(component_id='race_graph', component_property='figure'),
               Output(component_id='age_graph', component_property='figure'),
               Output(component_id='gender_graph', component_property='figure')],
              [Input("my_interval", "n_intervals")])
def update(n):
    month_fig = go.Figure(data=[
        go.Bar(x=month_data['label'], y=month_data['name'], marker_color=colors[5])
    ])
    month_fig.update_layout(height=370, title="Month Breakdown", template="plotly_dark")

    state_fig = go.Figure(data=go.Choropleth(
        locations=state_data['state'],
        z=state_data['name'],
        locationmode='USA-states',
        colorscale=px.colors.sequential.Aggrnyl,
        showscale=False,
    ))
    state_fig.update_layout(title_text='State Breakdown', geo_scope='usa', dragmode=False, template="plotly_dark",
                            margin={"r": 0, "t": 0, "l": 0, "b": 0})

    armed_fig = go.Figure(data=[go.Pie(labels=armed_data['armed'].str.title(), values=armed_data['name'],
                                       title="Armed", marker=dict(colors=colors))])
    armed_fig.update_layout(template="plotly_dark")

    mental_fig = go.Figure(
        data=[go.Pie(labels=mental_data['signs_of_mental_illness'].str.title(), values=mental_data['name'],
                     title="Mental Illness", marker=dict(colors=colors))])
    mental_fig.update_layout(template="plotly_dark")

    city_fig = go.Figure(data=[
        go.Bar(x=city_data['city'], y=city_data['name'], marker_color=colors[6])
    ])
    city_fig.update_layout(title="Top 20 Most Impacted Cities", template="plotly_dark")

    race_fig = go.Figure(data=[
        go.Bar(x=race_data['race'], y=race_data['name'], marker_color=colors[3])
    ])
    race_fig.update_layout(title="Race", height=310, template="plotly_dark")

    age_fig = go.Figure(data=[
        go.Bar(x=age_data['age range'], y=age_data['name'], marker_color=colors[2])
    ])
    age_fig.update_layout(title="Age", height=310, template="plotly_dark")

    gender_fig = go.Figure(data=[
        go.Bar(x=gender_data['gender'], y=gender_data['name'], marker_color=colors[4])
    ])
    gender_fig.update_layout(title="Gender", height=310, template="plotly_dark")

    return month_fig, state_fig, armed_fig, mental_fig, city_fig, race_fig, age_fig, gender_fig


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=300 * 1000,
        max_intervals=100,
    ),
    html.H1('US Police Shootings', style={'paddingTop': '20px', 'textAlign': 'center', 'color': 'white',
                                          'fontSize': 40, 'font-family': 'Arial, Helvetica, sans-serif'}),
    html.H4('JAN 2015 - Present', style={'marginTop': '-10px', 'textAlign': 'center', 'color': '#7BC875',
                                         'fontSize': 20, 'font-family': 'Arial, Helvetica, sans-serif',
                                         'backgroundColor': '#111111'}),
    dbc.Row([
        html.Div([
            html.Div([
                dcc.Graph(id='date_graph', config={'displayModeBar': False})
            ]),
            dbc.Row([
                html.Div([
                    dcc.Graph(id='armed_graph', config={'displayModeBar': False})
                ], style={"width": '50%'}),
                html.Div([
                    dcc.Graph(id='mental_illness_chart', config={'displayModeBar': False})
                ], style={"width": '50%'}),
            ], style={'marginTop': -10}),
            html.Div([
                dcc.Graph(id='city_graph', config={'displayModeBar': False})
            ], style={'marginTop': -60})
        ], style={"width": '65%'}),
        html.Div([
            html.Div([
                html.Div(style={'width': "32%", 'height': 20, 'position': 'absolute', 'zIndex': 4,
                                'backgroundColor': '#111111'}),
                dcc.Graph(id='us_map', config={'displayModeBar': False})
            ]),
            html.Div([
                html.Div([
                    dcc.Graph(id='race_graph', config={'displayModeBar': False})
                ]),
                html.Div([
                    dcc.Graph(id='age_graph', config={'displayModeBar': False})
                ], style={'marginTop': -60}),
                html.Div([
                    dcc.Graph(id='gender_graph', config={'displayModeBar': False})
                ], style={'marginTop': -60})
            ], style={'marginTop': -60})
        ], style={"width": '34%', 'marginTop': -10})
    ], style={'marginTop': -10}),
], style={'backgroundColor': '#111111'})

if __name__ == '__main__':
    app.run_server(debug=True)
