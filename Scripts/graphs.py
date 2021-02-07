import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv("../Data/sortedData6M.csv")

df["Date"] = pd.to_datetime(df["Date"], dayfirst="True")
df["Time"] = pd.to_timedelta(df["Time"])


data1 = df.groupby(["Date", "Name"]).size().reset_index(name="Count")

fig = px.line(data1, x="Date", y="Count", color="Name")
#fig.show()

app.layout = html.Div(children=[
   html.H1(children="it's a count :D "),

   html.H3(children="Number of messages per day"),

   dcc.Graph(
      id="graph",
      figure = fig
   )
])

if __name__ == "__main__":
   app.run_server(debug=True)
