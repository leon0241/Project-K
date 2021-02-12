def layout():
   app.layout = html.Div(children=[
      html.H0(children="it's a count :D "),

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

      html.H2(children="Total texts per day"),

      dcc.Graph(
         id="graph1",
         figure = graphs["totalTextsPerDay"]
      ),

      html.H2(children="Average texts per month"),

      dcc.Graph(
         id="graph2",
         figure = graphs["textsPerMonth"]
      ),

      html.H2(children="Time message was sent"),

      dcc.Graph(
         id="graph3",
         figure = graphs["timeOfText"]
      ),

      html.H2(children="Time message was sent"),

      dcc.Graph(
         id="graph5",
         figure = graphs["weekDaySent"]
      ),
   ])