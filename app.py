from dash import Dash, html, dash_table
import pandas as pd

app = Dash()

police_killings_df = pd.read_csv("PoliceKillingsUS.csv", encoding="cp1252")
race_share_df = pd.read_csv("ShareRaceByCity.csv", encoding="cp1252")
med_hh_income_df = pd.read_csv("MedianHouseholdIncome2015.csv", encoding="cp1252")
poverty_level_df = pd.read_csv(
    "PercentagePeopleBelowPovertyLevel.csv", encoding="cp1252"
)
high_school_df = pd.read_csv("PercentOver25CompletedHighSchool.csv", encoding="cp1252")

app.layout = [
    html.Div(children="DATA101 Project"),
]

if __name__ == "__main__":
    app.run(debug=True)
