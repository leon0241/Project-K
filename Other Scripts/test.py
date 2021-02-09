import pandas as pd

def initialise_dataframe():
    df = pd.read_csv("../Data/sortedData6M.csv")
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    df["Time"] = df["Time"].str[0:5]
    return df

def texts_day_of_week(df):
    temp = df
    da = df
    print(df)
    temp["Date"] = temp["Date"].dt.day_name()
    temp = df.groupby(["Date", "Name"]).size().reset_index(name="Count")
    print(df)

def main():
    dataframe = initialise_dataframe()
    texts_day_of_week(dataframe)

main()
