import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
import numpy as np
import emoji as em
graphs = {}
data = []

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Initialise dataframe
def initialise_dataframe():
   df = pd.read_csv("Data/sortedData6M.csv")
   df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
   df["Time"] = pd.to_timedelta(df["Time"])
   #df["Time"] = df["Time"].str[0:5]
   return df

# Number of texts sent per day per person
def texts_over_date(df):
   ndf = df.groupby(["Date", "Name"]).size().reset_index(name="Count")
   ndf = ndf.pivot(index="Date", columns="Name", values="Count")
   ndf["Total"] = ndf["Kristi"] + ndf["Leon"]
   data.append(ndf)
   texts_per_day()
   texts_per_month(ndf)

# Number of texts sent per month
def texts_per_month(df):
   df = df.resample('M').mean()
   data.append(df)

# Day message sent
def texts_day_of_week(df):
   # If you don't do this, df will get reassigned with the values of temp
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})

   ndf["Date"] = ndf["Date"].dt.day_name()
   ndf = ndf.groupby(["Date"]).size().reset_index(name="Count")
   ndf["Date"] = pd.Categorical(ndf["Date"], categories=["Monday","Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)
   data.append(ndf)

def ind_day_of_week(df):
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})

   ndf["Date"] = ndf["Date"].dt.day_name()
   ndf = ndf.groupby(["Date", "Name"]).size().reset_index(name="Count")

   ndf["Date"] = pd.Categorical(ndf["Date"], categories=["Monday","Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)
   data.append(ndf)
   ndf = ndf.pivot(index="Date", columns="Name", values="Count")

# Time message was sent
def texts_per_hour(df):
   ndf = df.groupby(["Time"]).size().reset_index(name="Count")
   ndf = ndf.set_index("Time")
   ndf = ndf.resample('H').sum()
   data.append(ndf)

# Time in minutes message was sent
def texts_per_time(df):
   ndf = df.groupby(["Time"]).size().reset_index(name="Count")
   ndf = ndf.set_index("Time")
   data.append(ndf)

# Percentages of messages sent
def text_ratio(df):
   ndf = df.groupby(["Name"]).size().reset_index(name="Count")
   data.append(ndf)

# Count words sent
def stat_functions(df):
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})

   ndf_d = data[0]
   ndf["Count"] = df["Contents"].str.split().str.len()
   messageCount = ndf.size
   wordCount = ndf["Count"].sum()
   pictureCount = ndf["Attachments"].count()

   mostWords = ndf_d["Total"].max()
   mostWordsDate = ndf_d["Total"].idxmax()
   avgMsgs = ndf_d["Total"].mean()
   avgMsgsLen = ndf["Count"].mean()

   print(messageCount, wordCount, pictureCount, mostWords, mostWordsDate, avgMsgs, avgMsgsLen)

def word_occurances(df):
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})
   ndf_l, ndf_k = [x for _, x in ndf.groupby(ndf["Name"] == "Leon")]

   ndf_k = ndf_k.reset_index()
   ndf_l = ndf_l.reset_index()
   arr = [ndf_k, ndf_l]
   for i in range(2):
      ndf_t = arr[i]

      words = ndf_t["Contents"].str.split(expand=True).stack().value_counts()
      ndf_wt = words.to_frame()
      ndf_wt = ndf_wt.reset_index()
      ndf_wt = ndf_wt.rename(columns = {"index":"Word", 0:"Count"})

      wordArray = ndf_wt.values.tolist()

   #    if i == 0:
   #       ndf_wk = ndf_wt
   #    else:
   #       ndf_wl = ndf_wt
   
   # ndf_wk.to_csv("Data/wordsL.csv")
   # ndf_wl.to_csv("Data/wordsK.csv")

def graphs():

   graphs["textsPerDay"] = px.line(data[0], x=data[0].index, y=["Kristi", "Leon"])
   graphs["textsPerDayTrend"] = px.scatter(data[0], x=data[0].index, y=["Kristi", "Leon"], trendline="lowess")

   graphs["totalTextsPerDay"] = px.bar(data[0], x=data[0].index, y=["Kristi", "Leon"], title="Chart")

   graphs["textsPerMonth"] = px.bar(data[1], x=data[1].index, y=["Kristi", "Leon"], barmode="group")

   graphs["weekDaySent"] = px.bar(data[2], x="Date", y="Count", barmode="group")

   graphs["weekDaySent"] = px.bar(data[2], x=data[2].index, y=["Kristi", "Leon"], barmode="group")

   graphs["timeOfText"] = px.bar(data[3], x=data[3].index, y="Count")

   graphs["timeOfText"] = px.bar(data[3], x=data[3].index, y="Count")

   graphs["percentMessages"] = px.pie(data[4], values="Count", names="Name")





def layout():
   app.layout = html.Div(children=[
      html.H1(children="it's a count :D "),

      html.H2(children="Percentage of messages sent by each person"),

      dcc.Graph(
         id="graph4",
         figure = graphs["percentMessages"]
      ),

      html.H2(children="Number of messages per day"),

      dcc.Graph(
         id="graph",
         figure = graphs["textsPerDay"]
      ),

      dcc.Graph(
         id="graph7",
         figure = graphs["textsPerDayTrend"]
      ),

      html.H2(children="Total texts per day"),

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
         id="graph5",
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
   texts_per_hour(dataframe)
   text_ratio(dataframe)
   stat_functions(dataframe)
   word_occurances(dataframe)
   layout()

if __name__ == "__main__":
   main()
   app.run_server(debug=True)


# print(loc[0,:])