from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

app = Dash()

police_killings_df = pd.read_csv("PoliceKillingsUS.csv", encoding="cp1252")
race_share_df = pd.read_csv("ShareRaceByCity.csv", encoding="cp1252")
med_hh_income_df = pd.read_csv("MedianHouseholdIncome2015.csv", encoding="cp1252")
poverty_level_df = pd.read_csv(
    "PercentagePeopleBelowPovertyLevel.csv", encoding="cp1252"
)
high_school_df = pd.read_csv("PercentOver25CompletedHighSchool.csv", encoding="cp1252")

state_killings_df = police_killings_df.groupby("state").size().reset_index(name="count")

state_killings_fig = go.Figure(
    data=go.Choropleth(
        locations=state_killings_df["state"],
        z=state_killings_df["count"],
        locationmode="USA-states",
        colorscale=[[0, "#DEDAD6"], [1, "#AE0E1D"]],
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar_title="Number of Killings",
    )
)

state_killings_fig.update_layout(
    title_text="Police Killings by State",
    title_x=0.5,
    geo=dict(
        scope="usa",
        showlakes=True,
        lakecolor="rgb(173,216,230)",
        projection_scale=0.9,
    ),
    height=800,
    margin=dict(r=0, t=50, l=0, b=0),
    legend=dict(x=2.5, y=0.59),
)


app.layout = [
    html.Div(
        children=[
            "DATA101 Project",
            dcc.Graph(
                id="police-killings-map",
                figure=state_killings_fig,
                style={"height": "800px", "width": "100%"},
                config={"responsive": True},
            ),
        ]
    ),
]

if __name__ == "__main__":
    app.run(debug=True)
