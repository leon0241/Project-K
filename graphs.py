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

# Number of texts sent per day per person
temp = df.groupby(["Date", "Name"]).size().reset_index(name="Count")
data.append(temp)
graphs["textsPerDay"] = px.line(data[0], x="Date", y="Count", color="Name")

# Number of texts sent per day (Total)
graphs["totalTextsPerDay"] = px.bar(data[0], x="Date", y="Count", color="Name", title="Chart")

# Number of texts sent per month
temp = temp.pivot(index="Date", columns="Name", values="Count")
temp = temp.resample('M').mean()
data.append(temp)
graphs["textsPerMonth"] = px.bar(data[1], x=data[1].index, y=["Kristi", "Leon"], barmode="group")

# Time message was sent
temp = df.groupby(["Time"]).size().reset_index(name="Count")
data.append(temp)
graphs["timeOfText"] = px.bar(data[2], x="Time", y="Count")

# Percentages of messages sent
temp = df.groupby(["Name"]).size().reset_index(name="Count")
data.append(temp)
graphs["percentMessages"] = px.pie(data[3], values="Count", names="Name")

#Day message sent
temp = df
temp["Date"] = temp["Date"].dt.day_name()
temp = temp.groupby(["Date", "Name"]).size().reset_index(name="Count")
temp["Date"] = pd.Categorical(temp["Date"], categories=["Monday","Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)
temp = temp.pivot(index="Date", columns="Name", values="Count")
data.append(temp)
graphs["weekDaySent"] = px.bar(data[4], x=data[4].index, y=["Kristi", "Leon"], barmode="group")


graphs["timeOfText"].update_layout(
   bargap=0
)

#graphs["timeOfText"].show()


app.layout = html.Div(children=[
   html.H1(children="it's a count :D "),

   html.H3(children="Percentage of messages sent by each person"),

   dcc.Graph(
      id="graph5",
      figure = graphs["percentMessages"]
   ),

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

   html.H3(children="Average texts per month"),

   dcc.Graph(
      id="graph3",
      figure = graphs["textsPerMonth"]
   ),

   html.H3(children="Time message was sent"),

   dcc.Graph(
      id="graph4",
      figure = graphs["timeOfText"]
   ),

   html.H3(children="Time message was sent"),

   dcc.Graph(
      id="graph6",
      figure = graphs["weekDaySent"]
   ),
])

if __name__ == "__main__":
   app.run_server(debug=True)


# print(loc[0,:])