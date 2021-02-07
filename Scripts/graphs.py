import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

df = pd.read_csv("Data/sortedData6M.csv")
df["Date"] = pd.to_datetime(df["Date"], dayfirst="True")
print(df.dtypes)
#data1 = df.groupby(["Date", "Name"]).size().reset_index(name="count")