from dash import Dash, html, dcc
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
                color: "#192A37";
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
race_share_df = pd.read_csv("ShareRaceByCity.csv", encoding="cp1252")
med_hh_income_df = pd.read_csv("MedianHouseholdIncome2015.csv", encoding="cp1252")
poverty_level_df = pd.read_csv("PercentagePeopleBelowPovertyLevel.csv", encoding="cp1252")
high_school_df = pd.read_csv("PercentOver25CompletedHighSchool.csv", encoding="cp1252")

state_killings_df = police_killings_df.groupby("state").size().reset_index(name="count")

# Create choropleth map
state_killings_fig = go.Figure(
    data=go.Choropleth(
        locations=state_killings_df["state"],
        z=state_killings_df["count"],
        locationmode="USA-states",
colorscale=[[0, "#FBE8D3"], [1, "#943232"]],
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar=dict(
            thickness=12,
            len=0.8,
            orientation="h",
            y=-0.2
        )
)
)

state_killings_fig.update_layout(
    title_text="Shootings by State",
    title_x=0.5,
    geo=dict(
        scope="usa",
        projection=dict(type="albers usa"),
        showland=True,
        landcolor="#FEF7EB",
        showocean=False,
        showlakes=False,
        bgcolor="#FEF7EB",
    ),
    height=800,
    margin=dict(r=0, t=50, l=0, b=0),
    legend=dict(x=1.5, y=0.59),
    paper_bgcolor="#FEF7EB",
    plot_bgcolor="#FEF7EB",
    font=dict(
        family="Inter, sans-serif",
        weight="bold",
        color="#192A37"
    )
)

# Layout
app.layout = html.Div(
    children=[
        html.H1(
            "Police Shootings USA",
            style={
                "paddingLeft": "10vw",
            }
        ),
        html.Div(
            children=[
                dcc.Graph(
                    id="police-killings-map",
                    figure=state_killings_fig,
                    style={
                        "height": "400px",
                        "width": "100%",
                        "borderRadius": "16px",
                        "border": "1px solid #D6D4CC",
                        "padding": "10px",
                    },
                    config={
                        "responsive": True,
                        "displayModeBar": False,
                    },
                ),
                html.P(
                    "This visualization is based on data from Kaggle’s “Fatal Police Shootings in the US” dataset, "
                    "which compiles incidents of individuals fatally shot by police officers in the United States. "
                    "The dataset includes details such as the victim’s race, age, armed status, and the circumstances "
                    "of the encounter. Since 2015, thousands of such incidents have been recorded, with states like "
                    "California and Texas consistently reporting the highest numbers. The data sheds light on regional "
                    "disparities and raises questions about systemic patterns in law enforcement encounters.",
                    style={
                        "textAlign": "justify",
                        "marginTop": "20px",
                        "fontSize": "16px",
                        "lineHeight": "1.6",
                    },
                )
            ],
            style={
                "width": "40vw",
                "paddingLeft": "10vw",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center"
            }
        )
    ],
    style={
        "fontFamily": "'Inter', sans-serif",
        "backgroundColor": "#FEF7EB",
        "paddingTop": "30px"
    }
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=True, port=port, host="127.0.0.1")
