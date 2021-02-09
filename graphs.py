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
def initialise_dataframe():
   df = pd.read_csv("Data/sortedData6M.csv")
   df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
   df["Time"] = df["Time"].str[0:5]
   return df

# Number of texts sent per day per person
def texts_over_date(df):
   temp = df.groupby(["Date", "Name"]).size().reset_index(name="Count")
   temp = temp.pivot(index="Date", columns="Name", values="Count")
   temp["Total"] = temp["Kristi"] + temp["Leon"]
   data.append(temp)
   texts_per_day()
   texts_per_month(temp)

# Number of texts sent per day (Total)
def texts_per_day():
   df = data[0]
   graphs["textsPerDay"] = px.line(df, x=df.index, y=["Kristi", "Leon"])

   graphs["totalTextsPerDay"] = px.bar(df, x=df.index, y=["Kristi", "Leon"], title="Chart")

# Number of texts sent per month
def texts_per_month(temp):
   temp = temp.resample('M').mean()
   data.append(temp)
   graphs["textsPerMonth"] = px.bar(data[1], x=data[1].index, y=["Kristi", "Leon"], barmode="group")

# Day message sent
def texts_day_of_week(df):
   temp = df
   print(df)
   temp["Date"] = temp["Date"].dt.day_name()
   print(df)
   temp = temp.groupby(["Date", "Name"]).size().reset_index(name="Count")
   temp["Date"] = pd.Categorical(temp["Date"], categories=["Monday","Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)
   temp = temp.pivot(index="Date", columns="Name", values="Count")
   data.append(temp)
   graphs["weekDaySent"] = px.bar(data[2], x=data[2].index, y=["Kristi", "Leon"], barmode="group")
   print(df)

# Time message was sent
def texts_per_time(df):
   temp = df.groupby(["Time"]).size().reset_index(name="Count")
   data.append(temp)
   graphs["timeOfText"] = px.bar(data[3], x="Time", y="Count")

# Percentages of messages sent
def text_ratio(df):
   temp = df.groupby(["Name"]).size().reset_index(name="Count")
   data.append(temp)
   graphs["percentMessages"] = px.pie(data[4], values="Count", names="Name")

# Count words sent
def count_words_sent(df):
   temp = df
   temp_day = data[0]
   temp["Count"] = df["Contents"].str.split().str.len()
   wordCount = temp["Count"].sum()
   mostWords = temp_day["Total"].max()
   avgMsgsK = temp_day["Kristi"].mean()
   avgMsgsL = temp_day["Leon"].mean()
   # print(df)
   # print(temp_day)
   # print(wordCount, mostWords, avgMsgsK, avgMsgsL)

def layout():
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

def main():
   dataframe = initialise_dataframe()
   texts_over_date(dataframe)
   texts_day_of_week(dataframe)
   texts_per_time(dataframe)
   text_ratio(dataframe)
   count_words_sent(dataframe)
   #print(dataframe.loc[2,:])
   layout()

if __name__ == "__main__":
   main()
   #app.run_server(debug=True)


# print(loc[0,:])