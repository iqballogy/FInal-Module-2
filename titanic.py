import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly import tools
import numpy as np
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)
server = app.server


 #CREATE DATAFRAME FROM SQL
engine = create_engine(
    "mysql+mysqlconnector://root:abc123@localhost/titanic?host=localhost?port=3306")
conn = engine.connect()
results = conn.execute("SELECT * from titanic").fetchall()
dfTitanic = pd.DataFrame(results, columns=results[0].keys())

def generate_table(dataframe, max_rows=10) :
    return html.Table(
         # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(str(dataframe.iloc[i,col])) for col in range(len(dataframe.columns))
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app.title = 'Dashboard Titanic'
app.layout = html.Div([
    html.H1('Dashboard Titanic'),
    html.H3('Created By : Muhammad Iqbal'
    ),
        dcc.Tabs(id="tabs", value='tab-1', children=[
            dcc.Tab(label = 'Data Titanic', value = 'tab-1', children = [
                html.Div([
                    html.Div([
                        html.P('Survived : : '),
                        dcc.Dropdown(
                             id='filtersurvivor',
                             options=[i for i in [{ 'label': 'All', 'value': '' },
                                                { 'label': 'Survived', 'value': 'yes' },
                                                { 'label': 'Not-Survived', 'value': 'no' }]],
                            value=''
                        )
                    ], className = 'col-4'),
                ], className='row'),
                html.Br(),
                html.Div([
                    html.Div([
                        html.P('Select Age : '),
                        dcc.RangeSlider(
                            marks={i: str(i) for i in range(dfTitanic['age'].min(), dfTitanic['age'].max()+1,10)},
                            min=dfTitanic['age'].min(),
                            max=dfTitanic['age'].max(),
                            value=[dfTitanic['age'].min(),dfTitanic['age'].max()],
                            className='rangeslider',
                            id='filterageslider'
                        )
                    ], className='col-9'),
                    html.Div([

                    ],className='col-1'),
                    html.Div([
                        html.Br(),
                        html.Button('Search', id='buttonsearch', style=dict(width='100%'))
                    ], className='col-2')
                ], className='row'),
                html.Br(),html.Br(),html.Br(),
                html.Div([
                    html.Div([
                        html.P('Max Rows : '),
                        dcc.Input(
                            id='filterrowstable',
                            type='number',
                            value=10,
                            style=dict(width='100%')
                        )
                    ], className='col-1')
                ], className='row'),
                html.Center([
                    html.H2('Data Titanic', className='title'),
                    html.Div(id='tablediv'),
                ])
            ]),
#TAB 2
        dcc.Tab(label='Categorical Plots', value='tab-5', children=[
            html.Br(),html.Br(),
            html.Div([
                html.Div([
                    html.P('Kind : '),
                    dcc.Dropdown(
                        id='jenisplotcategory',
                        options=[{'label': i, 'value': i} for i in ['Bar','Box','Violin']],
                        value='Bar'
                    )
                ], className='col-3'),
                html.Div([
                    html.P('X : '),
                    dcc.Dropdown(
                        id='xplotcategory',
                        options=[i for i in [{ 'label': 'Age', 'value': 'age' },
                                                { 'label': 'Alone', 'value': 'alone' },
                                                { 'label': 'Alive', 'value': 'alive' },
                                                { 'label': 'Embark Town', 'value': 'embark_town' },
                                                { 'label': 'Sex', 'value': 'sex' },
                                                { 'label': 'Who', 'value': 'who' }]],
                        value='alone'
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Y : '),
                    dcc.Dropdown(
                        id='yplotcategory',
                        options=[i for i in [{ 'label': 'Age', 'value': 'fare' },
                                            { 'label': 'Fare', 'value': 'age' }]],
                        value='age'
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Stats : '),
                    dcc.Dropdown(
                        id='statsplotcategory',
                        options=[i for i in [{ 'label': 'Mean', 'value': 'mean' },
                                            { 'label': 'Standard Deviation', 'value': 'std' },
                                            { 'label': 'Count', 'value': 'count' },
                                            { 'label': 'Min', 'value': 'min' },
                                            { 'label': 'Max', 'value': 'max' },
                                            { 'label': '25th Percentiles', 'value': '25%' },
                                            { 'label': 'Median', 'value': '50%' },
                                            { 'label': '75th Percentiles', 'value': '75%' }]],
                        value='mean',
                        disabled=False
                    )
                ], className='col-3')
            ], className='row'),
            html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),
            dcc.Graph(
                id='categorygraph'
            )
        ]),
        ]),
], style={
    'maxWidth': '1200px',
    'margin': '0 auto'
})

@app.callback(
    Output(component_id='tablediv', component_property='children'),
    [Input('buttonsearch', 'n_clicks'),
    Input('filterrowstable', 'value')],
    [State('filtersurvivor', 'value'),
    State('filterageslider', 'value')]
)

def update_table(n_clicks,maxrows, live,age):
    dfFilter = dfTitanic[((dfTitanic['age'] >= age[0]) & (dfTitanic['age'] <= age[1]))]
    if(live != '') :
        dfFilter = dfFilter[dfFilter['alive'] == str(live)]
    return generate_table(dfFilter, max_rows=maxrows)

def generateValuePlot(legendary, x, y, stats = 'mean') :
    return {
        'x': {
            'Bar': dfTitanic[dfTitanic['alive'] == legendary][x].unique(),
            'Box': dfTitanic[dfTitanic['alive'] == legendary][x],
            'Violin': dfTitanic[dfTitanic['alive'] == legendary][x]
        },
        'y': {
            'Bar': dfTitanic[dfTitanic['alive'] == legendary].groupby(x)[y].describe()[stats],
            'Box': dfTitanic[dfTitanic['alive'] == legendary][y],
            'Violin': dfTitanic[dfTitanic['alive'] == legendary][y]
        }
    }

@app.callback(
    Output(component_id='categorygraph', component_property='figure'),
    [Input(component_id='jenisplotcategory', component_property='value'),
    Input(component_id='xplotcategory', component_property='value'),
    Input(component_id='yplotcategory', component_property='value')]
)

def update_category_graph(jenisplot, xplot, yplot):
    listGoFunc = {
    'Bar': go.Bar,
    'Box': go.Box,
    'Violin': go.Violin
}
    return dict(
        layout= go.Layout(
            title= '{} Plot Titanic'.format(jenisplot),
            xaxis= { 'title': 'alive' },
            yaxis= dict(title='Age'),
            boxmode='group',
            violinmode='group'
        ),
        data=[
            listGoFunc[jenisplot](
                x=generateValuePlot('yes',xplot,yplot)['x'][jenisplot],
                y=generateValuePlot('yes',xplot,yplot)['y'][jenisplot],
                name='yes'
            ),
        ]
    )

if __name__ == '__main__':
    app.run_server(debug=True)



