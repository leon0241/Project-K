import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os

graphs = {}
data = []

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv("Data/sortedData6M.csv")

df["Date"] = pd.to_datetime(df["Date"], dayfirst="True")
df["Time"] = df["Time"].str[0:5]
#df["Time"] = pd.to_datetime(("21/12/2016 " + df["Time"]), format="%d/%m/%Y %H:%M:%S")


temp = df.groupby(["Date", "Name"]).size().reset_index(name="Count")
data.append(temp)
#graph1 = px.line(data1, x="Date", y="Count", color="Name")
graphs["textsPerDay"] = px.line(data[0], x="Date", y="Count", color="Name")

temp = df


temp = df.groupby(["Time"]).size().reset_index(name="Count")
data.append(temp)

graphs["timeOfText"] = px.bar(data[1], x="Time", y="Count")

graphs["timeOfText"].update_layout(
   bargap=0
)

graphs["timeOfText"].show()


app.layout = html.Div(children=[
   html.H1(children="it's a count :D "),

   html.H3(children="Number of messages per day"),

   dcc.Graph(
      id="graph",
      figure = graphs["textsPerDay"]
   ),

   html.H3(children="Time message was sent"),

   dcc.Graph(
      id="graph2",
      figure = graphs["timeOfText"]
   ),
])

# if __name__ == "__main__":
#    app.run_server(debug=True)
