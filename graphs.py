import dash
import dash_defer_js_import as dji
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import numpy as np
import emoji
data = [0] * 10

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

config = {'displayModeBar': False}
# Initialise dataframe
def initialise_dataframe():
   df = pd.read_csv("Data/sortedData6M.csv")
   df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
   df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S")
   #df["Time"] = pd.to_timedelta(df["Time"])
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
   #ndf.index = ndf.index.astype('timedelta64[h]')

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
   stats["msgCount"] = len(ndf)

   ndf_n = data[6]
   stats["indmsgCount"] = ndf_n["Count"].to_list()# pylint: disable=unsubscriptable-object

   stats["wordCount"] = round(ndf["Count"].sum())

   ndf_n = ndf[["Name", "Count"]]
   ndf_n = ndf.groupby("Name").sum()
   stats["indWordCount"] = ndf_n["Count"].to_list()
   stats["indWordCount"][0] = round(stats["indWordCount"][0])
   stats["indWordCount"][1] = round(stats["indWordCount"][1])

   stats["pictureCount"] = ndf["Attachments"].count()

   ndf_n = ndf[["Name", "Attachments"]]
   ndf_n = ndf_n.groupby("Name").count()
   stats["indPicCount"] = ndf_n["Attachments"].to_list()

   stats["emojiCount"] = ndf_e["Count"].sum() # pylint: disable=unsubscriptable-object

   ndf_n = data[9]
   stats["indEmojiCount"] = ndf_n["Count"].to_list()# pylint: disable=unsubscriptable-object


   stats["mostWords"] = ndf_d["Total"].max() # pylint: disable=unsubscriptable-object
   stats["mostWordsDate"] = ndf_d["Total"].idxmax() # pylint: disable=unsubscriptable-object
   stats["avgMsgs"] = ndf_d["Total"].mean() # pylint: disable=unsubscriptable-object
   stats["avgMsgsLen"] = ndf["Count"].mean()
   stats["activeHour"] = ndf_t["Count"].idxmax() # pylint: disable=unsubscriptable-object
   stats["activeHourCount"] = ndf_t["Count"].max()# pylint: disable=unsubscriptable-object
   stats["activeDay"] = ndf_wd["Count"].idxmax() # pylint: disable=unsubscriptable-object
   stats["activeDayCount"] = ndf_wd["Count"].max()# pylint: disable=unsubscriptable-object

   stats["mostUsedEmoji"] = ndf_ew["Total"].idxmax() # pylint: disable=unsubscriptable-object

   return stats

   #print(msgCount, wordCount, pictureCount, mostWords, mostWordsDate, avgMsgs, avgMsgsLen)
   # 462156 400031.0 1192 1403 2020-09-21 00:00:00 472.55214723926383 5.235939320165967 13326

def reassign_df(df):
   ndf = df.rename(columns = {"Name":"a"})
   ndf = ndf.rename(columns = {"a":"Name"})
   return ndf

colors = ["#2E3440", "#3B4252", "#434C5E","#4C566A", "#D8DEE9", "#E5E9F0", "#ECEFF4", "#8FBCBB", "#88C0D0","#81A1C1","#5E81AC","#BF616A", "#D08770","#EBCB8B","#A3BE8C", "#B48EAD"]

def graph_functions():
   #nord0, nord1, nord4, nord5, blue, pink
   graphs = {}
   colorscheme = {"Leon": colors[8], "Kristi": colors[15]}

   graphs["textsPerDay"] = px.line(data[0], x=data[0].index, y=["Kristi", "Leon"], # pylint: disable=maybe-no-member
      color_discrete_map={"Leon": colors[8], "Kristi": colors[15]})
   graphs["textsPerDay"] = apply_layout(graphs["textsPerDay"])


   #graphs["textsPerDayTrend"] = px.scatter(data[0], x=data[0].index, y=["Kristi", "Leon"], trendline="lowess") # pylint: disable=maybe-no-member
   graphs["totalTextsPerDay"] = px.bar(data[0], x=data[0].index, y=["Kristi", "Leon"], title="Chart",
      color_discrete_map=colorscheme) # pylint: disable=maybe-no-member
   graphs["totalTextsPerDay"] = apply_layout(graphs["totalTextsPerDay"])
   #graphs["totalTextsPerDay"].update_layout({"bargap":0})

   #graphs["textsPerMonth"] = px.bar(data[1], x=data[1].index, y=["Kristi", "Leon"], barmode="group") # pylint: disable=maybe-no-member

   graphs["weekDaySent"] = px.bar(data[2], x="Count", y=data[2].index, orientation='h',
      color_discrete_sequence=[colors[9]]) # pylint: disable=maybe-no-member
   graphs["weekDaySent"] = apply_layout(graphs["weekDaySent"])
   #graphs["indWeekDaySent"] = px.bar(data[3], x=data[3].index, y=["Kristi", "Leon"], barmode="group") # pylint: disable=maybe-no-member

   graphs["hourOfText"] = px.bar(data[4], x=data[4].index, y="Count",
      color_discrete_sequence=[colors[9]]) # pylint: disable=maybe-no-member
   graphs["hourOfText"] = apply_layout(graphs["hourOfText"])
   graphs["hourOfText"].update_layout(
      xaxis_tickformat="%H:%M",
      xaxis={
         "dtick":3600000,
         "tickangle":21
         }
   )
   #graphs["timeOfText"] = px.bar(data[5], x=data[5].index, y="Count") # pylint: disable=maybe-no-member

   graphs["percentMessages"] = px.pie(data[6], values="Count", names="Name",
      color="Name", color_discrete_map=colorscheme)
   graphs["percentMessages"] = apply_layout(graphs["percentMessages"])

   tt = data[8].head(20) # pylint: disable=maybe-no-member
   #graphs["emojiPie"] = px.pie(tt, values="Count", names=tt.index, color=tt.index,color_discrete_sequence=px.colors.sequential.Sunsetdark)
   graphs["emojiPie"] = px.bar(tt, x=tt.index, y=["Leon", "Kristi"], 
   color_discrete_map=colorscheme)
   graphs["emojiPie"] = apply_layout(graphs["emojiPie"])
   graphs["emojiPie"].update_layout(
      showlegend = False,
      xaxis={"tickfont_size": 23},
      yaxis={"title_text":"Count"}
   )

   graphs["emojiFrequency"] = px.pie(data[9], values="Count" , names=data[9].index, color=data[9].index, color_discrete_map=colorscheme) # pylint: disable=maybe-no-member
   graphs["emojiFrequency"] = apply_layout(graphs["emojiFrequency"])

   return graphs

def apply_layout(graph):
   def_leg = {"bgcolor": colors[2], "title": "Name"}
   xy = {"color": colors[4], "linecolor": colors[4]}
   def_layout = {
      "plot_bgcolor": colors[2], 
      "paper_bgcolor": "rgba(0, 0, 0, 0)", 
      "font_color": colors[4], 
      "legend":def_leg,
      "xaxis":xy,
      "yaxis":xy,
   }
   def_trace = {"marker_line_width":0}
   graph.update_layout(def_layout)
   graph.update_traces(def_trace)
   return graph

def generate_row(emoji, count, message, indCount):
   strCount = str(count)
   strInd = [str(indCount[0]), str(indCount[1])]

   return html.Div(className="statList", children=[
      html.H2(className="gridItem statEmoji", children=[emoji]),
               
      html.H2(className="gridItem statMain", children=[
         html.Span(className="highlight", children=[strCount]),
         message
      ]),

      html.H3(className="gridItem statLeon", children=[
         strInd[0]
      ]),

      html.Div(className="gridItem statBar", children=[
         html.Div(className="barLeon", style={
            "--size":(str(indCount[0] / count * 100) + "%")}
         ),
         html.Div(className="barKristi", style={
            "--size":(str(indCount[1] / count * 100) + "%")}
         )
      ]),

      html.H3(className="gridItem statKristi", children=[
         strInd[1]
      ])
   ])

def layout(graphs, stats):
   app.layout = html.Div(id="pageDiv", children=[
      html.Header(id="title", className="outerDiv", children=[
         html.H1("Our half-year in review"),
         html.Hr(className="divider"),
         html.H4("A visual representation of our message data from 30/07/2020 to 08/01/2021 (discord won't give me the rest)")
      ]),

      html.Section(id="generalStats", className="outerDiv", children=[
         html.Header([
            html.H2("Who texts the most?"),
         ]),

         html.Main([
            html.Section(id="percentPie", children=[
               dcc.Graph(
                  id="graph_1",
                  figure = graphs["percentMessages"]
               )
            ]),

            html.Section(id="percentStats", className="innerDiv", children=[
               generate_row("✉️", stats["msgCount"], " messages",  stats["indmsgCount"]),
               generate_row("📄", stats["wordCount"], " words",  stats["indWordCount"]),
               generate_row("🖼️", stats["pictureCount"], " pictures",  stats["indPicCount"]),
               generate_row("🤔", stats["emojiCount"], " emojis",  stats["indEmojiCount"])
            ])
         ])
      ]),

      html.Section(id="perDay", className="outerDiv", children=[
         html.Header([
            html.H2("How often do we text?"),
         ]),

         html.Main([
            dcc.Graph(
               id="graph_2",
               figure = graphs["textsPerDay"]
            ),

            html.Section(id="perDayStats", children=[
               html.Section(className="innerDiv", children=[
                  html.Div(className="centerDiv", children=[
                     html.H3(className="", children=[
                     "We text an average of ",
                     html.Span(className="highlight", children=[
                        str(round(stats["avgMsgs"]))]),
                     " messages per day",
                     html.Br(),
                     "That's around 20 a messages an hour!"]),
                  ])
               ]),

               html.Section(className="innerDiv", children=[
                  html.Div(className="centerDiv", children=[
                     html.H3(className="", children=[
                        "Our busiest day was ",
                        html.Span(className="highlight", children=[
                           str(stats["mostWordsDate"])[0:10]]), ", ",
                        html.Br(),
                        "where we sent ",
                        html.Span(className="highlight", children=[
                           str(stats["mostWords"])]),
                        " messages",
                        html.Br(),
                        "That's around 58 a messages an hour!"
                     ]),
                  ])
               ])
            ]),

            dcc.Graph(
               id="graph_3",
               figure = graphs["totalTextsPerDay"]
            )
         ])
      ]),
      
      html.Section(id="activeTime", className="outerDiv", children=[
         html.Header([
            html.H2("When do we text the most?"),
         ]),

         html.Main([
            html.Section([
               html.Div(className="innerDiv", children=[
                  html.H2(["Our most active hour of the day",
                     html.Br(),
                     "is ",
                     html.Span(className="highlight", children=[
                        str(stats["activeHour"])[11:16]
                     ]),
                     ", with a total of ",
                     html.Br(),
                     html.Span(className="highlight", children=[
                        str(stats["activeHourCount"])
                     ]),
                     " messages."
                  ]),
               ]),

               dcc.Graph(
                  id="graph_4",
                  figure = graphs["hourOfText"]
               )
            ]),

            html.Section([
               dcc.Graph(
                  id="graph_5",
                  figure = graphs["weekDaySent"]
               ),

               html.Div(className="innerDiv", children=[
                  html.H2(["Our most active day of the week",
                     html.Br(),
                     "is ",
                     html.Span(className="highlight", children=[
                        stats["activeDay"]
                     ]),
                     ", with a total of ",
                     html.Br(),
                     html.Span(className="highlight", children=[
                        str(stats["activeDayCount"])
                     ]),
                     " messages."
                  ]),
                  
               ])
            ])
         ])
      ]),

      html.Section(id="emoji", className="outerDiv", children=[
         html.Header([
            html.H2("Top emojis")
         ]),

         html.Main([
            html.Section(id="emojiPie", children=[
               html.Div([
                  html.Img(src=app.get_asset_url('kristi.png')),
               ]),
               
               dcc.Graph(
                  id="graph_6",
                  figure = graphs["emojiPie"]
               )
            ]),

            html.Section(id="emojiFreq", children=[
               html.H2("lol"),
               dcc.Graph(
                  id="graph_7",
                  figure = graphs["emojiFrequency"]
               )
            ])
         ])
      ]),

      html.Footer(id="footer", className="outerDiv", children=[
         html.Section([
            html.H5("To be continued....")
         ]),
         html.Hr(className="divider"),
         html.Section([
            html.H6("Data extracted from Discord's Data package. Data visualised using Plotly and Dash.")
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
   app.run_server(debug=False)


# print(loc[0,:])