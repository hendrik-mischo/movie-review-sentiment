import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import pickle
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
#from flask import Flask, request, jsonify
from models.RNN.transformers import TextToSequence, RemoveHTML
from models.RNN.rnn_predict import rnn_make_predictions
from models.SVM.utils import clean_text_tokenized
from models.SVM.predict import svm_make_prediction
import pandas as pd
import random


#####
from bs4 import BeautifulSoup
def RemoveHTML(text):
    text = BeautifulSoup(text, "html.parser").get_text()
    return text
#####

movies  = pd.read_csv('./movie scraper/data/movies.csv', sep=';')

external_stylesheets = [
    dbc.themes.FLATLY,
    'https://use.fontawesome.com/releases/v5.7.2/css/all.css'
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    suppress_callback_exceptions=True
)

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(
        id='page-content',
        style={
            'width':'80%',
            'max-width':'350px',
            'min-width':'350px',
            'margin':'0 auto',
            'margin-top':'10px',
            'padding':'5px',
            'height':'600px',
            #'border':'1px solid grey'
        }
    )
], style={'height':'100vh','width':'100vw'}
)

home_layout = html.Div([
    html.H3(
        'Review this movie 🎬',
        id='title',
        className='display-5',
        style={'text-align':'center', 'font-weight':'bold'}
    ),

    # Movie title wrapper
    html.Div(
        [
            html.Div(
                [
                    html.Img(
                        id='poster',
                        style={
                            'position':'relative',
                            'top':'50%',
                            'left':'50%',
                            'transform':'translate(-50%,-50%)'
                        }
                    )
                ],
                style={
                    'height':'80px',
                    'width':'50px',
                    'float':'left',
                    #'border':'1px solid red'
                }
            ),
            html.Div(
                [
                html.H4(
                        id='movie_title',
                        style={
                            'display':'table-cell',
                            'vertical-align':'middle'
                        }
                    ),
                ],
                style={
                    #'border':'1px solid green',
                    'float':'left',
                    'margin-left':'5px',
                    'max-width':'270px',
                    'height':'80px',
                    'overflow': 'auto',
                    'display':'table',
                    'vertical-align':'middle'
                }
            ),
        ],
        className='alert alert-dismissible alert-light',
        style={
            'height':'90px',
            'padding':'5px',
            'overflow': 'hidden',
            #'border':'1px solid lightgrey',
            #'border-radius':'15px''
        }
    ),

    # Review and results wrapper
    html.Div(
        [
            dcc.Textarea(
                className="form-control z-depth-1",
                id="review",
                rows="6",
                placeholder="Write a review here..."
            ),
            html.H5(
                'Classifying sentiment...',
                style={'margin-top':'10px'}
            ),
            dbc.Progress(
                id='progress',
                value=0,
                striped=False,
                color='success',
                style={
                    'height':'20px',
                    'margin-top':'10px'
                }
            ),
            html.H4(
                id='decision',
                style={'margin-top':'10px', 'font-weight':'bold'}
            ),
            html.H5(
                'Was your review classified correctly? 🤔',
                style={'margin-top':'25px'}
            ),
            dbc.ButtonGroup(
                [
                    dbc.Button('Yes', id='button_yes', className='btn btn-primary', active=True),
                    dbc.Button('No', id='button_no', className='btn btn-primary', active=False)
                ],
            ),
            dbc.Button(
                [
                    html.Span(
                        'Submit',
                        style={'margin-right':'10px'}
                    ),
                    html.I(
                        className='fas fa-flag-checkered'
                    )
                ],
                id='submit_button',
                color='primary',
                className='btn btn-primary btn-lg btn-block',
                n_clicks_timestamp=0,
                style={'margin-top':'25px'}
            ),
            dbc.Button(
                [
                    html.Span(
                        'Review another movie',
                        style={'margin-right':'10px'}
                    ),
                    html.I(
                        className='fas fa-redo-alt'
                    )
                ],
                id='shuffle_button',
                color='secondary',
                className='btn btn-primary btn-lg btn-block',
                n_clicks_timestamp=0
            ),
            html.H5(
                'Change classifier:',
                style={'margin-top':'15px'}
            ),
            dbc.ButtonGroup(
                [
                    dbc.Button('SVM', id='button_svm', className='btn btn-primary', active=True),
                    dbc.Button('RNN', id='button_rnn', className='btn btn-primary', active=False)
                ],
            )
        ],
        style={
            #'border':'1px solid green',
            'margin-top':'10px',
            'text-align':'center'
        }
    )
    ]
)

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return home_layout
    else:
        return [
            html.Div(
                [
                    html.H2('404 Page not found')
                ],
            ),
            dcc.Link("Go to Home", href="/"),
        ]


@app.callback(
    [
        Output('progress','value'),
        Output('progress','children'),
        Output('progress','color'),
        Output('decision','children')
    ],
    [
        Input('review','value'),
        Input('button_svm','active'),
        Input('button_rnn','active')
    ]
)
def update_progress(review, button_svm, button_rnn):

    if review is not None and review.strip() != '':
        if button_svm:
            pred_sentiment = svm_make_prediction(review)
        elif button_rnn:
            pred_sentiment = rnn_make_predictions(review)

        pred_sentiment = round(pred_sentiment * 100, 1)
        pred_sentiment_text = f'{pred_sentiment}%'
        bar_value = pred_sentiment

        if pred_sentiment >= 67:
            color = 'success'
        elif 33 < pred_sentiment < 67:
            color = 'warning'
        else:
            color = 'danger'

        if pred_sentiment >= 50:
            decision = 'Sentiment: Positive 👍'
        else:
            decision = 'Sentiment: Negative 👎'
        return bar_value, pred_sentiment_text, color, decision
    else:
        return 0, None, None, 'Classification: ---'


@app.callback(
    [
        Output('poster','src'),
        Output('movie_title','children'),
        Output('review', 'value')
    ],
    [
        Input('submit_button','n_clicks_timestamp'),
        Input('shuffle_button','n_clicks_timestamp')
    ]
)
def shuffle_movie(submit_click_ts, shuffle_click_ts):
    if submit_click_ts > shuffle_click_ts:
        x=1

    random_movie = movies.sample(1).to_dict(orient='records')[0]
    movie_title = random_movie['title']
    poster_url = random_movie['poster_url']
    movie_year = random_movie['year']
    movie_title_year = f'{movie_title} ({movie_year})'

    return poster_url, movie_title_year, ''


@app.callback(
    [
        Output('button_yes','active'),
        Output('button_no','active')
    ],
    [
        Input('button_yes','n_clicks'),
        Input('button_no','n_clicks')
    ]
)
def toggle_yesno_buttons(yes_clicks, no_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not any([yes_clicks, no_clicks]):
        return False, False
    elif button_id == 'button_yes':
        return True, False
    elif button_id == 'button_no':
        return False,True


@app.callback(
    [
        Output('button_svm','active'),
        Output('button_rnn','active')
    ],
    [
        Input('button_svm','n_clicks'),
        Input('button_rnn','n_clicks')
    ]
)
def toggle_model_buttons(svm_clicks, rnn_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'button_svm':
        return True, False
    elif button_id == 'button_rnn':
        return False, True


if __name__ == '__main__':
    app.run_server(debug=True)#, host='0.0.0.0')
