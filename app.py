from dash import Dash, html, dash_table
import pandas as pd

app = Dash()

app.layout = [
    html.Div(children="DATA101 Project"),
]

if __name__ == "__main__":
    app.run(debug=True)
