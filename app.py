import dash
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.graph_objs as go
import os

app = Dash(
    external_stylesheets=[],
    suppress_callback_exceptions=True,
)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #FEF7EB;
                color: #192A37;
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load data
police_killings_df = pd.read_csv("PoliceKillingsUS.csv", encoding="cp1252")
police_killings_df['date'] = pd.to_datetime(police_killings_df['date'])

race_labels = {
    'W': 'White',
    'B': 'Black',
    'A': 'Asian',
    'H': 'Hispanic',
    'N': 'Native American',
    'O': 'Other',
    '': 'Unknown'
}
police_killings_df['race_full'] = police_killings_df['race'].map(race_labels)

# App Layout
app.layout = html.Div([
    dcc.Store(id='filtered-data', data=police_killings_df.to_json(date_format='iso', orient='split')),

    html.H1("Police Shootings USA", style={"paddingLeft": "10vw"}),

    # Filter bar with dropdowns and reset
    html.Div([
        dcc.Dropdown(
            id='weapon-dropdown',
            options=[{'label': w, 'value': w} for w in sorted(police_killings_df['armed'].dropna().unique())],
            placeholder="Select weapon",
            style={"width": "200px", "marginRight": "10px"}
        ),
        dcc.Dropdown(
            id='gender-dropdown',
            options=[{'label': g, 'value': g} for g in sorted(police_killings_df['gender'].dropna().unique())],
            placeholder="Select gender",
            style={"width": "150px", "marginRight": "10px"}
        ),
        dcc.Dropdown(
            id='manner-dropdown',
            options=[{'label': m, 'value': m} for m in sorted(police_killings_df['manner_of_death'].dropna().unique())],
            placeholder="Select manner of death",
            style={"width": "250px", "marginRight": "10px"}
        ),
        html.Button("Reset Filters", id="reset-button", n_clicks=0, style={
            "fontSize": "16px", "padding": "10px 20px",
            "borderRadius": "8px", "border": "1px solid #943232",
            "backgroundColor": "#943232", "color": "white",
            "cursor": "pointer"
        })
    ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "margin": "20px"}),

    # Charts Section
    html.Div([
        html.Div([
            dcc.Graph(id="police-killings-map", style={"height": "600px"}),
            html.P(
                "This dashboard visualizes data from Kaggle’s “Fatal Police Shootings in the US” dataset, which compiles information on individuals fatally shot by police officers in the United States since January 1, 2015. The data originates from The Washington Post's ongoing database of fatal police shootings. The dataset includes details such as the individual's name, age, gender, race, the date and location of the incident, whether the individual was armed, and the manner of death. By interacting with this dashboard, you can explore patterns and trends across different demographics and regions, aiming to foster a deeper understanding of these incidents and support informed discussions on law enforcement practices and policies.",
                style={"textAlign": "justify", "marginTop": "20px", "fontSize": "16px", "lineHeight": "1.6"}
            ),
        ], style={"width": "40vw", "padding": "0 5vw", "display": "flex", "flexDirection": "column", "alignItems": "center"}),

        html.Div([
            dcc.Graph(id="victim-race-pie"),
            dcc.Graph(id="shootings-over-time", style={"marginTop": "30px"})
        ], style={"width": "40vw", "padding": "0 5vw", "display": "flex", "flexDirection": "column", "alignItems": "center"})
    ], style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between"})
], style={"fontFamily": "'Inter', sans-serif", "backgroundColor": "#FEF7EB", "paddingTop": "30px"})


# Callback to filter data based on user interaction
@app.callback(
    Output('filtered-data', 'data'),
    Input('police-killings-map', 'clickData'),
    Input('victim-race-pie', 'clickData'),
    Input('weapon-dropdown', 'value'),
    Input('gender-dropdown', 'value'),
    Input('manner-dropdown', 'value'),
    Input('reset-button', 'n_clicks')
)
def filter_data(map_click, pie_click, weapon, gender, manner, reset_clicks):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if triggered == 'reset-button':
        return police_killings_df.to_json(date_format='iso', orient='split')

    df = police_killings_df.copy()

    if map_click and map_click['points']:
        state = map_click['points'][0]['location']
        df = df[df['state'] == state]

    if pie_click and pie_click['points']:
        race = pie_click['points'][0]['label']
        df = df[df['race_full'] == race]

    if weapon:
        df = df[df['armed'] == weapon]

    if gender:
        df = df[df['gender'] == gender]

    if manner:
        df = df[df['manner_of_death'] == manner]

    return df.to_json(date_format='iso', orient='split')


# Update the choropleth map
@app.callback(
    Output('police-killings-map', 'figure'),
    Input('filtered-data', 'data')
)
def update_map(json_data):
    df = pd.read_json(json_data, orient='split') if json_data else police_killings_df
    state_killings_df = df.groupby("state").size().reset_index(name="count")
    fig = go.Figure(go.Choropleth(
        locations=state_killings_df["state"],
        z=state_killings_df["count"],
        locationmode="USA-states",
        colorscale=[[0, "#FBE8D3"], [1, "#943232"]],
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar=dict(thickness=12, len=0.8, orientation="h", y=-0.2)
    ))
    fig.update_layout(
        title_text="Shootings by State", title_x=0.5,
        geo=dict(scope="usa", projection=dict(type="albers usa"), showland=True, landcolor="#FEF7EB", bgcolor="#FEF7EB"),
        height=600, margin=dict(r=0, t=50, l=0, b=0),
        paper_bgcolor="#FEF7EB", plot_bgcolor="#FEF7EB",
        font=dict(family="Inter, sans-serif", color="#192A37")
    )
    return fig


# Update the pie chart
@app.callback(
    Output('victim-race-pie', 'figure'),
    Input('filtered-data', 'data')
)
def update_pie(json_data):
    df = pd.read_json(json_data, orient='split') if json_data else police_killings_df
    race_counts = df['race_full'].value_counts().reset_index()
    race_counts.columns = ['race', 'count']
    fig = go.Figure(go.Pie(
        labels=race_counts['race'],
        values=race_counts['count'],
        hole=0.4,
        marker=dict(line=dict(color="#fff", width=2))
    ))
    fig.update_layout(
        title_text="Victim Race Distribution", title_x=0.5,
        paper_bgcolor="#FEF7EB", plot_bgcolor="#FEF7EB",
        font=dict(family="Inter, sans-serif", color="#192A37")
    )
    return fig


# Update the line chart
@app.callback(
    Output('shootings-over-time', 'figure'),
    Input('filtered-data', 'data')
)
def update_line(json_data):
    df = pd.read_json(json_data, orient='split') if json_data else police_killings_df
    shootings_over_time = df.groupby(df['date'].dt.to_period('M')).size()
    shootings_over_time.index = shootings_over_time.index.to_timestamp()
    min_point = shootings_over_time.idxmin()
    max_point = shootings_over_time.idxmax()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=shootings_over_time.index, y=shootings_over_time.values,
                             mode='lines+markers', line=dict(color='#943232')))
    fig.add_trace(go.Scatter(x=[min_point], y=[shootings_over_time[min_point]],
                             mode='markers+text', text=[f"Min: {shootings_over_time[min_point]}"],
                             textposition="bottom right", marker=dict(color='blue', size=10), showlegend=False))
    fig.add_trace(go.Scatter(x=[max_point], y=[shootings_over_time[max_point]],
                             mode='markers+text', text=[f"Max: {shootings_over_time[max_point]}"],
                             textposition="top left", marker=dict(color='red', size=10), showlegend=False))
    fig.update_layout(
        title_text="Shootings Over Time", title_x=0.5,
        xaxis_title="Date", yaxis_title="Number of Shootings",
        paper_bgcolor="#FEF7EB", plot_bgcolor="#FEF7EB",
        font=dict(family="Inter, sans-serif", color="#192A37")
    )
    return fig


# Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=True, port=port, host="127.0.0.1")
