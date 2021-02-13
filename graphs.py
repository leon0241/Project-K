import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
import numpy as np
import emoji
graphs = {}
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
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})
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
   ndf = ndf.sort_values(by=["Count"], ascending=False)
   ndf = ndf.reset_index()
   # Emojize the demojized emojis
   ndf["Emoji"] = ndf["Emoji"].apply(emoji.emojize)
   # Grab top 20 emojis
   ndf_tt = ndf.head(20)
   data[7] = ndf_tt
   # Group by name
   ndf = ndf.groupby("Name").sum()
   data[8] = ndf

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
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})

   ndf_d = data[0]
   ndf["Count"] = df["Contents"].str.split().str.len()
   messageCount = ndf.size
   wordCount = ndf["Count"].sum()
   pictureCount = ndf["Attachments"].count()

   mostWords = ndf_d["Total"].max() # pylint: disable=unsubscriptable-object
   mostWordsDate = ndf_d["Total"].idxmax() # pylint: disable=unsubscriptable-object
   avgMsgs = ndf_d["Total"].mean() # pylint: disable=unsubscriptable-object
   avgMsgsLen = ndf["Count"].mean()

   print(messageCount, wordCount, pictureCount, mostWords, mostWordsDate, avgMsgs, avgMsgsLen)

def reassign_df(df):
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})
   return ndf

def graph_functions():
   graphs["textsPerDay"] = px.line(data[0], x=data[0].index, y=["Kristi", "Leon"]) # pylint: disable=maybe-no-member
   graphs["textsPerDayTrend"] = px.scatter(data[0], x=data[0].index, y=["Kristi", "Leon"], trendline="lowess") # pylint: disable=maybe-no-member
   graphs["totalTextsPerDay"] = px.bar(data[0], x=data[0].index, y=["Kristi", "Leon"], title="Chart") # pylint: disable=maybe-no-member

   graphs["textsPerMonth"] = px.bar(data[1], x=data[1].index, y=["Kristi", "Leon"], barmode="group") # pylint: disable=maybe-no-member

   graphs["weekDaySent"] = px.bar(data[2], x="Count", y="Date", orientation='h')

   graphs["indWeekDaySent"] = px.bar(data[3], x=data[3].index, y=["Kristi", "Leon"], barmode="group") # pylint: disable=maybe-no-member

   graphs["hourOfText"] = px.bar(data[4], x=data[4].index, y="Count") # pylint: disable=maybe-no-member

   graphs["timeOfText"] = px.bar(data[5], x=data[5].index, y="Count") # pylint: disable=maybe-no-member

   graphs["percentMessages"] = px.pie(data[6], values="Count", names="Name")

   graphs["emojiPie"] = px.pie(data[7], values="Count", names="Emoji")
   graphs["emojiFrequency"] = px.bar(data[8], x=data[8].index , y="Count") # pylint: disable=maybe-no-member


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
         figure = graphs["hourOfText"]
      ),

      html.H3(children="Time message was sent"),

      dcc.Graph(
         id="graph6",
         figure = graphs["weekDaySent"]
      ),

      html.H3(children="Emoji"),

      dcc.Graph(
         id="graph8",
         figure = graphs["emojiPie"]
      ),

      dcc.Graph(
         id="graph9",
         figure = graphs["emojiFrequency"]
      ),
   ])

def main():
   dataframe = initialise_dataframe()
   texts_over_date(dataframe)
   texts_day_of_week(dataframe)
   ind_day_of_week(dataframe)
   texts_per_hour(dataframe)
   texts_per_time(dataframe)
   text_ratio(dataframe)
   stat_functions(dataframe)
   word_occurances(dataframe)
   graph_functions()
   layout()

if __name__ == "__main__":
   main()
   app.run_server(debug=True)


# print(loc[0,:])