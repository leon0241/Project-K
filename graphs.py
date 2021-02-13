import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
import numpy as np
import emoji
data = [0] * 10

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
   # Group by name, with new column Count
   ndf = df.groupby(["Date", "Name"]).size().reset_index(name="Count")

   # Pivot to wide format
   ndf = ndf.pivot(index="Date", columns="Name", values="Count")

   # Kristi + Leon is total
   ndf["Total"] = ndf["Kristi"] + ndf["Leon"]
   data[0] = ndf

   # Number of texts sent per month per person
   ndf = ndf.resample('M').mean()
   data[1] = ndf

# Total messages sent - weekday
def texts_day_of_week(df):
   # If you don't do this, df will get reassigned with the values of temp
   ndf = reassign_df(df)

   # Rename date to weekday name
   ndf["Date"] = ndf["Date"].dt.day_name()

   # Group by day with new column Count
   ndf = ndf.groupby(["Date"]).size().reset_index(name="Count")

   # Recategorise date to be in chronological order
   ndf["Date"] = pd.Categorical(ndf["Date"], categories=["Monday","Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)
   ndf = ndf.sort_values("Date")
   ndf = ndf.set_index("Date")
   data[2] = ndf

# Individual messages sent - weekday
def ind_day_of_week(df):
   # If you don't do this, df will get reassigned with the values of temp
   ndf = reassign_df(df)

   # Rename date to weekday name
   ndf["Date"] = ndf["Date"].dt.day_name()
   
   #Group by day > name with new column Count
   ndf = ndf.groupby(["Date", "Name"]).size().reset_index(name="Count")

   # Recategorise data
   ndf["Date"] = pd.Categorical(ndf["Date"], categories=["Monday","Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ordered=True)

   # Pivot to wide format
   ndf = ndf.pivot(index="Date", columns="Name", values="Count")
   data[3] = ndf

# Time message was sent
def texts_per_hour(df):
   # Group by time with new column Count
   ndf = df.groupby(["Time"]).size().reset_index(name="Count")
   
   # Set index to time
   ndf = ndf.set_index("Time")

   # Regroup with hour and find sum
   ndf = ndf.resample('H').sum()
   data[4] = ndf

# Time in minutes message was sent
def texts_per_time(df):
   # Group by time with new column Count
   ndf = df.groupby(["Time"]).size().reset_index(name="Count")

   # Set index to time
   ndf = ndf.set_index("Time")
   data[5] = ndf

# Percentages of messages sent
def text_ratio(df):
   # Group by name with new column Count
   ndf = df.groupby(["Name"]).size().reset_index(name="Count")
   data[6] = ndf

# Word occurances aka just emoji occurances
def word_occurances(df):
   ndf = reassign_df(df)

   ndf_l, ndf_k = [x for _, x in ndf.groupby(ndf["Name"] == "Leon")]

   ndf_k = ndf_k.reset_index()
   ndf_l = ndf_l.reset_index()
   arr = [ndf_k, ndf_l]
   
   # Separately for each person
   for i in range(2):

      ndf_t = arr[i]

      # Split for every word
      words = ndf_t["Contents"].str.split(expand=True).stack().value_counts()
      # Converts to dataframe? idk tbh
      ndf_w = words.to_frame()
      ndf_w = ndf_w.reset_index()
      ndf_w = ndf_w.rename(columns = {"index":"Word", 0:"Count"})

      # Converts array into 2d list.. idk how to do this purely using pandas
      wordArray = ndf_w.values.tolist()
      emojiArray = emoji_filter(wordArray)
      
      # Convert back into dataframe
      ndf_e = pd.DataFrame(emojiArray, columns =["Emoji", "Count"])

      # Group by name and get total count
      ndf_e = ndf_e.groupby("Emoji").sum()

      if i == 0:
         ndf_e.insert(0, "Name", "Leon")
         ndf_l = ndf_e
         #ndf_e.to_csv("Data/emojisl.csv")
      else:
         ndf_e.insert(0, "Name", "Kristi")
         ndf_k = ndf_e
         #ndf_e.to_csv("Data/emojisk.csv")
   # Combine the 2 arrays
   ndf = pd.concat([ndf_k, ndf_l])
   # Sort by count

   
   #ndf = ndf.reset_index()
   # Emojize the demojized emojis
   ndf = ndf.reset_index()
   ndf["Emoji"] = ndf["Emoji"].apply(emoji.emojize)
   ndf = ndf.sort_values(by=["Count"], ascending=False)
   ndf = ndf.set_index("Emoji")
   #print(ndf)
   # Grab top 20 emojis
   data[7] = ndf

   ndf_w = ndf.pivot(columns="Name", values="Count")
   ndf_w["Total"] = ndf_w.sum(axis=1)
   ndf_w = ndf_w.sort_values(by=["Total"], ascending=False)
   data[8] = ndf_w

   # Group by name
   ndf = ndf.groupby("Name").sum()
   data[9] = ndf

def emoji_filter(wordArray):
   emojiArray = []
   # Emoji filtering
   for value in wordArray:
      # Set word
      word = value[0]
      # Demojize (👀 -> :eyes:)
      demoji = emoji.demojize(word)
      # Check if word is a demojized word or not
      if demoji.startswith(":") and demoji.endswith(":"):
         # Check if word has more than one emoji (e.g 👀👀/:eyes::eyes:)
         if demoji.rfind("::") != -1:
            # Split by ::
            demojiArray = demoji.split("::")
            # Repeats each item in array to convert to pure emoji (:eyes:)
            for item in demojiArray:
               # If is in format ":eyes"
               if item.startswith(":") == True and item.endswith(":") == False:
                  item = item + ":"
               # If in format "eyes:"
               elif item.startswith(":") == False and item.endswith(":") == True:
                  item = ":" + item
               # Only other format is "eyes"
               else:
                  item = ":" + item + ":"
               # Append item, count
               emojiArray.append([item, value[1]])
         # If word only has one emoji
         else:                  
            # Append item, count
            emojiArray.append([demoji, value[1]])
   return emojiArray

# Count words sent
def stat_functions(df):
   ndf = reassign_df(df)

   stats = {}

   ndf_d = data[0]
   ndf_wd = data[2]
   ndf_t = data[4]
   ndf_e = data[7]
   ndf_ew = data[8]
   ndf["Count"] = df["Contents"].str.split().str.len()
   stats["messageCount"] = ndf.size
   stats["wordCount"] = ndf["Count"].sum()
   stats["pictureCount"] = ndf["Attachments"].count()
   stats["emojiCount"] = ndf_e["Count"].sum() # pylint: disable=unsubscriptable-object


   stats["mostWords"] = ndf_d["Total"].max() # pylint: disable=unsubscriptable-object
   stats["mostWordsDate"] = ndf_d["Total"].idxmax() # pylint: disable=unsubscriptable-object
   stats["avgMsgs"] = ndf_d["Total"].mean() # pylint: disable=unsubscriptable-object
   stats["avgMsgsLen"] = ndf["Count"].mean()
   stats["mostUsedEmoji"] = ndf_ew["Total"].idxmax() # pylint: disable=unsubscriptable-object
   stats["activeHour"] = ndf_t["Count"].idxmax() # pylint: disable=unsubscriptable-object
   stats["activeDay"] = ndf_wd["Count"].idxmax() # pylint: disable=unsubscriptable-object
   return stats

   #print(messageCount, wordCount, pictureCount, mostWords, mostWordsDate, avgMsgs, avgMsgsLen)
   #462156 400031.0 1192 1403 2020-09-21 00:00:00 472.55214723926383 5.235939320165967 13326

def reassign_df(df):
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})
   return ndf

def graph_functions():
   graphs = {}
   graphs["textsPerDay"] = px.line(data[0], x=data[0].index, y=["Kristi", "Leon"]) # pylint: disable=maybe-no-member
   graphs["textsPerDayTrend"] = px.scatter(data[0], x=data[0].index, y=["Kristi", "Leon"], trendline="lowess") # pylint: disable=maybe-no-member
   graphs["totalTextsPerDay"] = px.bar(data[0], x=data[0].index, y=["Kristi", "Leon"], title="Chart") # pylint: disable=maybe-no-member

   graphs["textsPerMonth"] = px.bar(data[1], x=data[1].index, y=["Kristi", "Leon"], barmode="group") # pylint: disable=maybe-no-member

   graphs["weekDaySent"] = px.bar(data[2], x="Count", y=data[2].index, orientation='h') # pylint: disable=maybe-no-member

   graphs["indWeekDaySent"] = px.bar(data[3], x=data[3].index, y=["Kristi", "Leon"], barmode="group") # pylint: disable=maybe-no-member

   graphs["hourOfText"] = px.bar(data[4], x=data[4].index, y="Count") # pylint: disable=maybe-no-member

   graphs["timeOfText"] = px.bar(data[5], x=data[5].index, y="Count") # pylint: disable=maybe-no-member

   graphs["percentMessages"] = px.pie(data[6], values="Count", names="Name")

   tt = data[7].head(20) # pylint: disable=maybe-no-member
   graphs["emojiPie"] = px.pie(tt, values="Count", names=tt.index)
   graphs["emojiFrequency"] = px.bar(data[9], x=["Kristi", "Leon"] , y="Count") # pylint: disable=maybe-no-member
   return graphs


# stats["messageCount"] = ndf.size
#    stats["wordCount"] = ndf["Count"].sum()
#    stats["pictureCount"] = ndf["Attachments"].count()
#    stats["emojiCount"] = ndf_e["Count"].sum() # pylint: disable=unsubscriptable-object


#    stats["mostWords"] = ndf_d["Total"].max() # pylint: disable=unsubscriptable-object
#    stats["mostWordsDate"] = ndf_d["Total"].idxmax() # pylint: disable=unsubscriptable-object
#    stats["avgMsgs"] = ndf_d["Total"].mean() # pylint: disable=unsubscriptable-object
#    stats["avgMsgsLen"] = ndf["Count"].mean()
#    stats["mostUsedEmoji"] = ndf_ew["Total"].idxmax()

def layout(graphs, stats):
   app.layout = html.Div(id="pageDiv", children=[
      html.Div(id="header", className="outerDiv", children=[
         html.H1("Kristi Count"),
         html.H2("Percentage of messages sent by each person")
      ]),

      html.Div(id="generalStats", className="outerDiv", children=[
         html.Div(className="innerDiv graphDiv", children=[
            html.H2("Percentage of messages sent"),
            dcc.Graph(
               id="graph_1",
               figure = graphs["percentMessages"]
            )
         ]),
         
         html.Div(className="innerDiv", children=[
            html.H2("Stats"),
            html.Div(className="divElement statContainer", children=[
               html.Div(className="divElement generalStat", children=[
               html.H3(stats["messageCount"])
               ]),
               html.Div(className="divElement generalStat", children=[
                  html.H3(stats["wordCount"])
               ]),
               html.Div(className="divElement generalStat", children=[
                  html.H3(stats["pictureCount"])
               ]),
               html.Div(className="divElement generalStat", children=[
                  html.H3(stats["emojiCount"])
               ])
            ])
         ])
      ]),

      html.Div(className="outerDiv", children=[
         html.H2("Number of messages per day"),

         dcc.Graph(
            id="graph_2",
            figure = graphs["textsPerDay"]
         ),

         html.H3(stats["avgMsgs"]),

         dcc.Graph(
            id="graph_3",
            figure = graphs["totalTextsPerDay"]
         )
      ]),

      html.Div(className="outerDiv", children=[
         html.Div(className="innerDiv", children=[
            html.Div(className="divElement", children=[
               html.H3(stats["activeHour"])
            ]),

            dcc.Graph(
               id="graph3",
               figure = graphs["hourOfText"]
            )
         ]),
         
         html.Div(className="innerDiv", children=[
            html.Div(className="divElement", children=[
               html.H3(stats["activeDay"])
            ]),

            dcc.Graph(
               id="graph5",
               figure = graphs["weekDaySent"]
            )
         ])
      ]),

      html.Div(className="outerDiv", children=[
         html.Div(className="separatorDiv", children=[
            html.Div(className="innerDiv", children=[
               dcc.Graph(
                  id="graph8",
                  figure = graphs["emojiPie"]
               )
            ]),

            html.Div(children=[
               html.H2("Top emojis"),
               html.Div(children=[
                  html.H2(stats["mostUsedEmoji"])
               ])
            ])
         ]),

         html.Div(className="separatorDiv", children=[
            html.H2("w.e"),
            dcc.Graph(
               id="graph9",
               figure = graphs["emojiFrequency"]
            ),
         ])
      ])

   ])

def main():
   dataframe = initialise_dataframe()
   texts_over_date(dataframe)
   texts_day_of_week(dataframe)
   ind_day_of_week(dataframe)
   texts_per_hour(dataframe)
   texts_per_time(dataframe)
   text_ratio(dataframe)
   word_occurances(dataframe)
   stats = stat_functions(dataframe)
   graphs = graph_functions()
   layout(graphs, stats)

if __name__ == "__main__":
   main()
   app.run_server(debug=True)


# print(loc[0,:])