#!/usr/bin/python3
from datetime import date

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pandas

# data URL
url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv'
today = date.today()
REF_TAMP = 9000  # reference value

# read csv for url
df = pandas.read_csv(url)
df = df.loc[df['denominazione_regione'] == 'Lombardia']

plotly_js_minified = ['https://cdn.plot.ly/plotly-basic-latest.min.js']

app = dash.Dash(__name__,
                external_scripts=plotly_js_minified,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}],
                requests_pathname_prefix='/lombardy/',
                routes_pathname_prefix='/lombardy/'
                )
app.title = 'Dashboard Lombardia'

server = app.server

# chart config
chart_config = {'displaylogo': False,
                'displayModeBar': False,
                'responsive': True
                }

# slider buttons
slider_button = list([
    dict(count=1,
         label="1m",
         step="month",
         stepmode="backward"),
    dict(count=3,
         label="3m",
         step="month",
         stepmode="backward"),
    dict(count=6,
         label="6m",
         step="month",
         stepmode="backward"),
    dict(step="all")
])


def refresh_data():
    global df
    global today
    # read csv for url and get date
    df = pandas.read_csv(url)
    df = df.loc[df['denominazione_regione'] == 'Lombardia']
    today = date.today()

    # data calculation
    df['terapia_intensiva_avg'] = df['terapia_intensiva'].rolling(7).mean()
    df['nuovi_decessi'] = df.deceduti.diff().fillna(df.deceduti)

    # percentage swab - cases
    df['delta_casi_testati'] = df.casi_testati.diff().fillna(df.casi_testati)
    df['incr_tamponi'] = df.tamponi.diff().fillna(df.tamponi)
    df['perc_positivi_tamponi'] = (df['nuovi_positivi'] / df['incr_tamponi']) * 100  # AB
    df['perc_positivi_test'] = (df['nuovi_positivi'] / df['delta_casi_testati']) * 100  # AD

    # rolling averages
    df['nuovi_positivi_avg'] = df['nuovi_positivi'].rolling(7).mean()
    df['nuovi_decessi_avg'] = df['nuovi_decessi'].rolling(7).mean()
    df['totale_ospedalizzati_avg'] = df['totale_ospedalizzati'].rolling(7).mean()
    df['perc_positivi_tamponi_avg'] = df['perc_positivi_tamponi'].rolling(3).mean()
    df['perc_positivi_test_avg'] = df['perc_positivi_test'].rolling(3).mean()

    # norm cases
    df['nuovi_casi_norm'] = df['nuovi_positivi'] * REF_TAMP / df['incr_tamponi']


def serve_layout():
    refresh_data()
    return html.Div(
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='andamento-contagi',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['nuovi_positivi'], 'type': 'bar', 'name': 'Nuovi Casi'},
                                {'x': df['data'], 'y': df['nuovi_positivi_avg'], 'type': 'scatter',
                                 'line': dict(color='orange'),
                                 'name': 'Media 7 giorni'}
                            ],
                            'layout': {
                                'title': 'Andamento dei contagi',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )
            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='perc-casi-tamponi',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['perc_positivi_test'], 'type': 'scatter',
                                 'name': 'Nuovi Casi testati', 'line': dict(color='orange')},
                                {'x': df['data'], 'y': df['perc_positivi_tamponi'], 'type': 'scatter',
                                 'line': dict(color='blue'),
                                 'name': 'Totale casi testati'},
                                {'x': df['data'], 'y': df['perc_positivi_test_avg'], 'type': 'scatter',
                                 'name': 'Nuovi Casi (media 3gg)', 'line': dict(color='orange', dash='dot')},
                                {'x': df['data'], 'y': df['perc_positivi_tamponi_avg'], 'type': 'scatter',
                                 'line': dict(color='blue', dash='dot'),
                                 'name': 'Totale casi (media 3gg)'}
                            ],
                            'layout': {
                                'title': '% Nuovi Casi / Test tramite tamponi',
                                'xaxis': {
                                    'type': 'date',
                                    'range': ['2020-04-22', today],
                                    'rangeselector': dict(buttons=slider_button),
                                    'rangeslider': dict(visible=False)

                                },
                                'yaxis': {
                                    'range': [0, 50],
                                    'tickprefix': '% '
                                }

                            }
                        },
                        config=chart_config
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='contagi-norm',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['nuovi_casi_norm'], 'type': 'bar',
                                 'name': 'Nuovi Casi norm.', 'line': dict(color='orange')}
                            ],
                            'layout': {
                                'title': 'Nuovi casi normalizzati',
                                'xaxis': {
                                    'type': 'date',
                                    'range': ['2020-04-22', today],
                                    'rangeselector': dict(buttons=slider_button),
                                    'rangeslider': dict(visible=False)

                                },
                                'yaxis': {
                                    'range': [75, 2200]  # hardcoded range, find better solution
                                }
                            }
                        },
                        config=chart_config

                    )
                )

            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='totale-ospedalizzati',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['totale_ospedalizzati'], 'type': 'bar',
                                 'name': 'Ospedalizzazioni'},
                                {'x': df['data'], 'y': df['totale_ospedalizzati_avg'], 'type': 'scatter',
                                 'line': dict(color='orange'),
                                 'name': 'Media 7 giorni'}
                            ],
                            'layout': {
                                'title': 'Totale ospedalizzati',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='decessi-giornalieri',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['nuovi_decessi'], 'type': 'bar', 'name': 'Decessi',
                                 'marker': dict(color='grey')},
                                {'x': df['data'], 'y': df['nuovi_decessi_avg'], 'type': 'scatter',
                                 'line': dict(color='blue'),
                                 'name': 'Media 7 giorni'}
                            ],
                            'layout': {
                                'title': 'Decessi giornalieri',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )

            ),

            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id='Terapia-intensiva',
                        figure={
                            'data': [
                                {'x': df['data'], 'y': df['terapia_intensiva'], 'type': 'bar',
                                 'name': 'Terapia Intensiva',
                                 'marker': dict(color='LightSalmon')},
                                {'x': df['data'], 'y': df['terapia_intensiva_avg'], 'type': 'scatter',
                                 'line': dict(color='blue'),
                                 'name': 'Media 7 giorni'}
                            ],
                            'layout': {
                                'title': 'Terapia intensiva',
                                'xaxis': dict(
                                    rangeselector=dict(buttons=slider_button),
                                    rangeslider=dict(visible=False),
                                    type='date'
                                )
                            }
                        },
                        config=chart_config
                    )
                )

            )

        ])
    )


app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
