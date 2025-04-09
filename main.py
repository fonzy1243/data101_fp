import dash
from dash import Dash, html, dcc, Input, Output, State
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

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,opsz,wght@0,18..144,300..900;1,18..144,300..900&display=swap" rel="stylesheet"> {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #FEF7EB;
                color: #192A37;
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            
            main {
                flex: 1;
            }
            
            .dashboard-footer {
                background-color: #192A37;
                color: #FEF7EB;
                padding: 30px 0;
                margin-top: 40px;
                width: 100%;
            }
        </style>
    </head>
    <body>
        <main>
            {%app_entry%}
        </main>
        <footer class="dashboard-footer">
            <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
                <p style="margin: 0;">Data source: The Washington Post's database of fatal police shootings.</p>
            </div>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load and preprocess
police_killings_df = pd.read_csv("PoliceKillingsUS.csv", encoding="cp1252")
police_killings_df['date'] = pd.to_datetime(police_killings_df['date'])

# Load state population data
state_pop_df = pd.read_csv("state_pop_2015.csv")
state_pop_df = state_pop_df[['State', 'population']]
state_pop_df.columns = ['state', 'population']

race_labels = {'W': 'White', 'B': 'Black', 'A': 'Asian', 'H': 'Hispanic', 'N': 'Native American', 'O': 'Other', '': 'Unknown'}
police_killings_df['race_full'] = police_killings_df['race'].fillna('').map(race_labels)

state_name_map = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}

# Create a reverse mapping from full state names to state codes
reverse_state_map = {v: k for k, v in state_name_map.items()}

# Layout
app.layout = html.Div([
    dcc.Store(id='filtered-data', data=police_killings_df.to_json(date_format='iso', orient='split')),
    dcc.Store(id='state-population-data', data=state_pop_df.to_json(orient='split')),
    dcc.Store(id='highlighted-state', data=None),

    html.Div([
        html.H1("2015 Police Shootings Dashboard USA", style={"marginBottom": "20px"}),

        html.Div([
            dcc.Dropdown(
                id='weapon-dropdown',
                options=[{'label': w, 'value': w} for w in sorted(police_killings_df['armed'].dropna().unique())],
                placeholder="Select victim weapon",
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
            dcc.Dropdown(
                id='income-sort',
                options=[
                    {'label': 'Lowest Income States', 'value': 'lowest'},
                    {'label': 'Highest Income States', 'value': 'highest'}
                ],
                value='lowest',
                clearable=False,
                style={"width": "230px", "marginRight": "10px"}
            ),
            html.Button("Reset Filters", id="reset-button", n_clicks=0, style={
                "fontFamily": "Inter",
                "fontSize": "12px", "padding": "10px 20px",
                "borderRadius": "8px", "border": "1px solid #7e2b2b",
                "fontWeight": "bold",
                "backgroundColor": "#7e2b2b", "color": "white",
                "cursor": "pointer"
            })
        ], style={"display": "flex", "background": "#943232", "borderRadius":"7px", "padding": "10px", "flexWrap": "wrap", "alignItems": "center", "marginBottom": "20px"})
    ], style={"maxWidth": "1200px", "margin": "0 auto", "padding": "0 20px"}),

    html.Div([
        html.Div([
            dcc.Graph(id="police-killings-map", style={"height": "600px"}),
            html.P(
                "This dashboard visualizes data from Kaggle's \"Fatal Police Shootings in the US\" dataset, which compiles information "
                "on individuals fatally shot by police officers in the United States since January 1, 2015. The data originates from "
                "The Washington Post's ongoing database of fatal police shootings. The dataset includes details such as the individual's "
                "name, age, gender, race, the date and location of the incident, whether the individual was armed, and the manner of death. "
                "By interacting with this dashboard, you can explore patterns and trends across different demographics and regions, aiming "
                "to foster a deeper understanding of these incidents and support informed discussions on law enforcement practices and policies.",
                style={"textAlign": "justify", "marginTop": "20px", "fontSize": "16px", "lineHeight": "1.6"}
            ),
        ], style={"width": "48%", "paddingRight": "2%"}),

        html.Div([
            dcc.Graph(id="victim-race-pie"),
            html.Div([
                dcc.Graph(id="income-bar-chart", style={"marginTop": "30px"}),
                html.Div([
                    html.Button("Previous", id="prev-page", n_clicks=0, style={
                        "fontFamily": "Inter",
                        "fontSize": "14px", "padding": "8px 16px",
                        "borderRadius": "4px", "border": "1px solid #943232",
                        "backgroundColor": "#943232", "color": "white",
                        "cursor": "pointer", "marginRight": "10px"
                    }),
                    html.Span(id="page-display", style={
                        "fontSize": "14px", "padding": "8px 16px",
                    }),
                    html.Button("Next", id="next-page", n_clicks=0, style={
                        "fontFamily": "Inter",
                        "fontSize": "14px", "padding": "8px 16px",
                        "borderRadius": "4px", "border": "1px solid #943232",
                        "backgroundColor": "#943232", "color": "white",
                        "cursor": "pointer", "marginLeft": "10px"
                    }),
                ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "marginTop": "15px"})
            ]),
            dcc.Store(id='income-data', data={}),
            dcc.Store(id='current-page', data=1)
        ], style={"width": "48%"})
    ], style={"maxWidth": "1200px", "margin": "0 auto", "display": "flex", "gap": "4%", "padding": "0 20px"})
], style={"fontFamily": "'Merriweather', sans-serif", "backgroundColor": "#FEF7EB", "paddingTop": "30px", "paddingBottom": "40px"})


# Callbacks
@app.callback(
    Output('highlighted-state', 'data'),
    [Input('police-killings-map', 'clickData'),
     Input('income-bar-chart', 'clickData'),
     Input('reset-button', 'n_clicks')]
)
def update_highlighted_state(map_click, bar_click, reset_clicks):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if triggered == 'reset-button':
        return None
    
    if triggered == 'police-killings-map' and map_click and map_click['points']:
        return map_click['points'][0]['location']
    
    if triggered == 'income-bar-chart' and bar_click and bar_click['points']:
        state_full = bar_click['points'][0]['label']
        # Convert full state name to state code
        return reverse_state_map.get(state_full)
    
    return dash.no_update


@app.callback(
    Output('filtered-data', 'data'),
    [Input('police-killings-map', 'clickData'),
     Input('victim-race-pie', 'clickData'),
     Input('weapon-dropdown', 'value'),
     Input('gender-dropdown', 'value'),
     Input('manner-dropdown', 'value'),
     Input('reset-button', 'n_clicks')]
)
def filter_data(map_click, pie_click, weapon, gender, manner, reset_clicks):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if triggered == 'reset-button':
        return police_killings_df.to_json(date_format='iso', orient='split')

    df = police_killings_df.copy()

    # Only filter by actual map clicks for data filtering (not for highlighting)
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


@app.callback(
    Output('police-killings-map', 'figure'),
    [Input('filtered-data', 'data'),
     Input('state-population-data', 'data'),
     Input('highlighted-state', 'data')]
)
def update_map(json_data, state_pop_json, highlighted_state):
    df = pd.read_json(json_data, orient='split')
    state_pop_df = pd.read_json(state_pop_json, orient='split')
    
    # Count incidents by state
    state_killings_df = df.groupby("state").size().reset_index(name="count")
    
    # Merge with population data
    state_data = pd.merge(state_killings_df, state_pop_df, on="state", how="right")
    
    # Fill NaN counts with 0
    state_data['count'] = state_data['count'].fillna(0)
    
    # Calculate rate per 100,000 population
    state_data['rate_per_100k'] = (state_data['count'] / state_data['population']) * 100000
    state_data['rate_per_100k'] = state_data['rate_per_100k'].round(2)
    
    # Add full state names for hover information
    state_data['state_full'] = state_data['state'].map(state_name_map)
    
    # Create choropleth with rates
    fig = go.Figure(go.Choropleth(
        locations=state_data["state"],
        z=state_data["rate_per_100k"],
        locationmode="USA-states",
        colorscale=[[0, "#FBE8D3"], [1, "#943232"]],
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar=dict(
            thickness=12, 
            len=0.8, 
            orientation="h", 
            y=-0.2,
            title="Rate per 100,000 population"
        ),
        hovertemplate='<b>%{customdata[1]}</b><br>Rate: %{z:.2f} per 100,000<br>Total: %{customdata[0]}<extra></extra>',
        customdata=state_data[['count', 'state_full']].values
    ))
    
    # If a state is highlighted, add a highlight layer
    if highlighted_state:
        # Create all states list
        all_states = list(state_name_map.keys())
        
        # Add a trace that highlights only the selected state
        fig.add_trace(go.Choropleth(
            locations=all_states,
            z=[1] * len(all_states),  # Dummy z values
            locationmode="USA-states",
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],  # Transparent
            marker_line_color="#000",
            marker_line_width=[3 if state == highlighted_state else 0.5 for state in all_states],
            showscale=False,
            hoverinfo="skip"
        ))
    
    fig.update_layout(
        title_text="Police Shootings by State (per 100,000 population)", 
        title_x=0.5,
        geo=dict(
            scope="usa", 
            projection=dict(type="albers usa"),
            showland=True, 
            landcolor="#FEF7EB", 
            bgcolor="#FEF7EB"
        ),
        height=600, 
        margin=dict(r=0, t=50, l=0, b=0),
        paper_bgcolor="#FEF7EB", 
        plot_bgcolor="#FEF7EB",
        font=dict(family="Inter, sans-serif", color="#192A37")
    )
    return fig


@app.callback(
    Output('victim-race-pie', 'figure'),
    Input('filtered-data', 'data')
)
def update_pie(json_data):
    df = pd.read_json(json_data, orient='split')
    race_counts = df['race_full'].value_counts().reset_index()
    race_counts.columns = ['race', 'count']

    fig = go.Figure(go.Pie(
        labels=race_counts['race'],
        values=race_counts['count'],
        hole=0.4,
        marker=dict(
        colors=[
            "#92C84F",  
            "#F1BE32",  
            "#F7943D",  
            "#5C4433",  
            "#C85C2E",
            "#3F7D4E",  
        "#C0C0C0"   
        ],
        line=dict(color="#fff", width=2)

        )
    ))
    fig.update_layout(
        title_text="Victim Race Distribution", title_x=0.5,
        paper_bgcolor="#FEF7EB", plot_bgcolor="#FEF7EB",
        font=dict(family="Inter, sans-serif", color="#192A37")
    )
    return fig


@app.callback(
    Output('income-data', 'data'),
    Input('income-sort', 'value')
)
def prepare_income_data(sort_value):
    income_df = pd.read_csv("MedianHouseholdIncome2015.csv", encoding="cp1252")
    income_df.rename(columns={"Geographic Area": "state", "Median Income": "median_income"}, inplace=True)

    income_df["median_income"] = (
        income_df["median_income"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r'(\d+)', expand=False)
        .astype(float)
    )

    grouped = income_df.groupby("state")["median_income"].mean().reset_index()
    grouped["state_full"] = grouped["state"].map(state_name_map)
    
    # Sort all states
    if sort_value == "lowest":
        grouped = grouped.sort_values("median_income")
    else:
        grouped = grouped.sort_values("median_income", ascending=False)
    
    return grouped.to_json(orient='split')

@app.callback(
    [Output('current-page', 'data'),
     Output('page-display', 'children')],
    [Input('prev-page', 'n_clicks'),
     Input('next-page', 'n_clicks'),
     Input('income-sort', 'value'),
     Input('highlighted-state', 'data')],
    [State('current-page', 'data'),
     State('income-data', 'data')]
)
def update_page(prev_clicks, next_clicks, sort_value, highlighted_state, current_page, json_data):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if not json_data:
        return current_page, f"Page {current_page}"

    df = pd.read_json(json_data, orient='split')
    total_pages = (len(df) + 7) // 8

    if triggered == 'income-sort':
        current_page = 1
    elif triggered == 'prev-page' and current_page > 1:
        current_page -= 1
    elif triggered == 'next-page' and current_page < total_pages:
        current_page += 1
    elif triggered == 'highlighted-state' and highlighted_state:
        # Convert state code (like 'CA') to full name (like 'California')
        state_full = state_name_map.get(highlighted_state)
        if state_full:
            df = df.reset_index(drop=True)
            if state_full in df['state_full'].values:
                idx = df[df['state_full'] == state_full].index[0]
                current_page = (idx // 8) + 1

    page_display = f"Page {current_page} of {total_pages}"
    return current_page, page_display



@app.callback(
    Output('income-bar-chart', 'figure'),
    [Input('income-data', 'data'),
     Input('current-page', 'data'),
     Input('income-sort', 'value'),
     Input('highlighted-state', 'data')]
)
def update_income_chart(json_data, page, sort_value, highlighted_state):
    if not json_data:
        return go.Figure()
    
    grouped = pd.read_json(json_data, orient='split')
    
    # Pagination: select 8 states for the current page
    start_idx = (page - 1) * 8
    end_idx = start_idx + 8
    page_data = grouped.iloc[start_idx:end_idx]
    
    # Set title based on sort selection
    if sort_value == "lowest":
        title = f"States with Lowest Median Household Income (Page {page})"
    else:
        title = f"States with Highest Median Household Income (Page {page})"

    # Create colors array to highlight selected state
    colors = ["#C97D60"] * len(page_data)
    
    if highlighted_state:
        for i, state_full in enumerate(page_data["state_full"]):
            state_code = reverse_state_map.get(state_full)
            if state_code == highlighted_state:
                colors[i] = "#943232"  # Darker red for highlighted state
    
    fig = go.Figure(go.Bar(
        x=page_data["median_income"],
        y=page_data["state_full"],
        orientation="h",
        marker_color=colors,
        hovertemplate='<b>%{y}</b><br>Median Income: $%{x:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title_text=title,
        xaxis_title="Median Household Income (USD)",
        yaxis_title="State",
        paper_bgcolor="#FEF7EB",
        plot_bgcolor="#FEF7EB",
        font=dict(family="Inter, sans-serif", color="#192A37"),
        margin=dict(t=50, l=10, r=30, b=40),  
        yaxis=dict(automargin=True)
    )

    return fig


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=True, port=port, host="127.0.0.1")
