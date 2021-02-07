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

# Initialise dataframe
df = pd.read_csv("Data/sortedData6M.csv")
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
df["Time"] = df["Time"].str[0:5]
print(df.loc[0,:])

# Number of texts sent per day per person
temp = df.groupby(["Date", "Name"]).size().reset_index(name="Count")
data.append(temp)
graphs["textsPerDay"] = px.line(data[0], x="Date", y="Count", color="Name")

# Number of texts sent per day (Total)
graphs["totalTextsPerDay"] = px.bar(data[0], x="Date", y="Count", color="Name", title="Chart")
# graphs["totalTextsPerDay"].show()


#temp = temp.set_index("Date")
temp = temp.pivot(index="Date", columns="Name", values="Count")
temp = temp.resample('M').mean()
print(temp)
data.append(temp)
graphs["textsPerMonth"] = px.bar(data[1], x=data[1].index, y=["Kristi", "Leon"])
graphs["textsPerMonth"].show()

# Time message was sent
temp = df.groupby(["Time"]).size().reset_index(name="Count")
data.append(temp)
graphs["timeOfText"] = px.bar(data[2], x="Time", y="Count")

# Percentages of messages sent
temp = df.groupby(["Name"]).size().reset_index(name="Count")
data.append(temp)
graphs["percentMessages"] = px.pie(data[3], values="Count", names="Name")

graphs["timeOfText"].update_layout(
   bargap=0
)

#graphs["timeOfText"].show()


app.layout = html.Div(children=[
   html.H1(children="it's a count :D "),

   html.H3(children="Number of messages per day"),

   dcc.Graph(
      id="graph",
      figure = graphs["textsPerDay"]
   ),

   html.H3(children="Total texts per day"),

   dcc.Graph(
      id="graph2",
      figure = graphs["totalTextsPerDay"]
   ),

   html.H3(children="Time message was sent"),

   dcc.Graph(
      id="graph3",
      figure = graphs["timeOfText"]
   ),
])

# if __name__ == "__main__":
#    app.run_server(debug=True)
