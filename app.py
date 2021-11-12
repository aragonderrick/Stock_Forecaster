import dash
import dash_bootstrap_components as dbc 
import pandas as pd
import plotly.express as px
import yfinance as yf
from dash import dcc
from dash import html
from datetime import datetime as dt
from datetime import timedelta as timedelta
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from model import prediction

# func to get the price action
def get_price_action(df):
    fig = px.line(
        data_frame = df,
        x = "Date",
        y = ["Close", "Open"],
        title = "Price Action",
        template = "plotly_dark"
    )
    return fig

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)
app.layout = html.Div(
    children=[
        html.H1(
            children = "Stock Price Forecast and Visualizer",
            className = "top_h",
        ),# end H1()
        html.Div(
            children = "An open-source tool for analyzing and predicting price action of your favorite stocks!",
            className = "bottom_div",
        ),# end Div()
        html.Div(
            children=[
                html.P("Predict the future of any stock!", className="start"),
                html.Div(
                    children = [
                        # stock code input
                        html.P("Enter a Ticker:"),
                        html.Div(
                            children = [
                                dcc.Input(id="input_tickers",
                                    type="text",
                                    placeholder = "          ticker symbol",
                                    className = "forecast"
                                ),
                                html.Button("Get Info", id='submit'),
                            ],
                            className = "form"
                        ),# end Div()  
                    ],
                    className = "input_place"
                ),# end Div()
                html.Div(
                    children = [
                        # Date range picker input
                        dcc.DatePickerRange(
                            id='my_date_picker_range',
                            min_date_allowed=dt(1995, 8, 5),
                            max_date_allowed=dt.now(),
                            initial_visible_month=dt.now(),
                        )
                    ],
                    className="forecast"
                ),
                html.Div(
                    children = [
                        dcc.Input(
                            id = "n_days",
                            type = "text",
                            placeholder = "    # Days In The Future",
                            className = "forecast",
                        ),#end input()
                        # Forecast button
                        html.Button(
                            "Forecast", 
                            className = "forecast_btn",
                            id="forecaste"
                        )#end button()
                    ],
                    className = "buttons"
                ),
            ], 
            className = "navbar"
        ),# end Div()
        html.Div(
            children=[
                html.Div(
                    children = [  
                        # Logo
                        html.Img(id="logo"),
                        # Company Name
                        html.P(id="ticker")
                    ],
                    className="header"
                ),#end Div()
                html.Div(
                    children = [

                    ],
                    #Description
                    id="description", 
                    className="description_ticker"
                ),# end Div()
                html.Div(
                    children = [
                        # Stock price plot
                    ], 
                    id="graphs_content",
                    className="graph_ticker"
                ),# end Div()
                html.Div(
                    children = [
                        # Indicator plot
                    ], 
                    id="main_content"
                ),# end Div()
                html.Div(
                    children = [
                        # Forecast plot
                    ], 
                    id="forecast_content"
                )# end Div()
            ], 
            className="content"
        )#end Div()
    ],
    className="container"
)

# callback for info
@app.callback(
    [
        Output("description", "children"),
        Output("logo", "src"),
        Output("ticker", "children"),
        Output("forecaste", "n_clicks")
    ], 
    [
        Input("submit", "n_clicks")
    ], 
    [
        State("input_tickers", "value")
    ]
)
def update_data(n, val):  # input parameter(s)
    if n == None:
        return "Input a Ticker Above!", "assets/logo.png", None, None
        # raise PreventUpdate
    else:
        if val == None:
            raise PreventUpdate
        else:
            tick = yf.Ticker(val)
            inf = tick.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[0], df['shortName'].values[0], None

# callback for graphs
@app.callback(
    [
        Output("graphs_content", "children"),
    ], 
    [
        Input("submit", "n_clicks"),
        Input('my_date_picker_range', 'start_date'),
        Input('my_date_picker_range', 'end_date')
    ], 
    [
        State("input_tickers", "value")
    ]
)
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    else:
        df = yf.download(val, str(start_date), str(end_date))

    df.reset_index(inplace=True)
    fig = get_price_action(df)
    return [dcc.Graph(figure=fig)]

# callback for prediction
@app.callback(
    [
        Output("forecast_content", "children")
    ],
    [
        Input("forecaste", "n_clicks")
    ],
    [
        State("n_days", "value"),
        State("input_tickers", "value")
    ]
)
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]

if __name__=='__main__':
    app.run_server(debug=True)
