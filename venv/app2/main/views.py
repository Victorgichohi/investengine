from flask import render_template, flash, redirect, session, url_for, request, g, json, request
from flask.ext.login import login_user, LoginManager, logout_user, current_user, login_required
from .forms import LoginForm, EditForm, PostForm, SearchForm
from .models import User, Post
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS

import QSTK.qstkutil.qsdateutil as du
import csv
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import QSTK.qstkutil.tsutil as tsu

import datetime as dt

import matplotlib.pyplot as plt, mpld3
from matplotlib.finance import candlestick


import pandas as pd

import math
import copy
import numpy as np
from copy import deepcopy


from pylab import *

from main import app, db, lm, oid


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def event_study(start_date, stop_date, price_change_low, price_change_high):

    # Start and End date of the charts
    dt_start = dt.datetime.strptime(start_date, '%Y, %m, %d')
    dt_end = dt.datetime.strptime(stop_date, '%Y, %m, %d')
    
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    f = open('presentorders.csv', 'w')

    dataobj = da.DataAccess('Yahoo')
    
    #CHANGES HERE
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('NASI')
    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
   
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_bollinger_events(ls_symbols, d_data, price_change_low, price_change_high)
    print "Creating Study 1"
    return ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                     s_filename='present.pdf', b_market_neutral=True,
                     b_errorbars=True, s_market_sym='NASI')

def bollinger_events(stocks, start_date, stop_date):
    ROLLING_WINDOW = 20
    N_STD_FACTOR = 2
    print stocks

    # Start and End date of the charts
    dt_start = dt.datetime.strptime(start_date, '%Y, %m, %d')
    dt_end = dt.datetime.strptime(stop_date, '%Y, %m, %d')
    
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    
    ls_symbols = stocks
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
        
    df_close = d_data['actual_close']
    
    # Create empty dataframe
    df_columns = np.concatenate((['Date'], ls_symbols))
    df = pd.DataFrame(index=range(len(ldt_timestamps)), columns=df_columns)
    df['Date'] = ldt_timestamps
    
    for s_sym in ls_symbols:
    
        # Calculate rolling mean and rolling std
        close_price = df_close[s_sym]
        rolling_mean = pd.rolling_mean(close_price, window=ROLLING_WINDOW)
        rolling_std = pd.rolling_std(close_price, window=ROLLING_WINDOW)
        
        # Calculate upper and lower Bollinger bands
        upper_bollinger = rolling_mean + rolling_std * N_STD_FACTOR
        lower_bollinger = rolling_mean - rolling_std * N_STD_FACTOR
        
        # Calculate normalized Bollinger values
        normalized_bollinger_values = (close_price - rolling_mean) / (rolling_std * N_STD_FACTOR)
        normalized_upper_values = normalized_bollinger_values > 1
        normalized_lower_values = normalized_bollinger_values < -1
        
        # Get dates where Bollinger values are not in the interval [-1, 1]
        normalized_upper_dates = [val for val, valmask in zip(ldt_timestamps, normalized_upper_values) if valmask]
        normalized_lower_dates = [val for val, valmask in zip(ldt_timestamps, normalized_lower_values) if valmask]
        
        #
        # Plot benchmark
        #
        plt.clf()
        fig = plt.figure()
        plt.subplot(2, 1, 1)
        # Plot close price and Bollinger bands
        
        fid = plt.plot(ldt_timestamps, close_price)
        plt.fill_between(ldt_timestamps, lower_bollinger, upper_bollinger, facecolor='lightgreen', edgecolor='gray')
        for date in normalized_upper_dates:
            plt.axvline(date, color='red', linewidth=0.1)
        for date in normalized_lower_dates:
            plt.axvline(date, color='green', linewidth=0.1)
        plt.legend([s_sym])
        plt.ylabel('Adjusted Close')
        plt.xlabel('Date')
        
        # Plot normalized Bollinger values
        plt.subplot(2, 1, 2)
        fid = plt.plot(ldt_timestamps, normalized_bollinger_values)
        for date in normalized_upper_dates:
            plt.axvline(date, color='red', linewidth=0.1)
        for date in normalized_lower_dates:
            plt.axvline(date, color='green', linewidth=0.1)
        plt.fill_between(ldt_timestamps, np.ones(len(ldt_timestamps)), np.zeros(len(ldt_timestamps)) - 1, facecolor='lightgray', edgecolor='gray')
        plt.ylabel('Bollinger Feature')
        plt.xlabel('Date')
        
        # Fix x axis range to fit with the plot above
        plt.xlim(xmin=ldt_timestamps[0])
        
        # Save the plot
        fig.savefig('Homework 5 - bollinger ' + str(s_sym) + '.pdf', format='pdf')
        return mpld3.fig_to_html(fig)

def draw_fig(stocks, start_date, stop_date):

    # List of symbols
    
    print start_date
    print stop_date
    ls_symbols = stocks
    print ls_symbols
    
    # Start and End date of the charts
    dt_start = dt.datetime.strptime(start_date, '%Y, %m, %d')
    dt_end = dt.datetime.strptime(stop_date, '%Y, %m, %d')
    
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)


    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    # Getting the numpy ndarray of close prices.
    na_price = d_data['open'].values
    print na_price

    

    
    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]
    
    fig, ax = subplots()
    ax.plot(ldt_timestamps, na_normalized_price)
    
    plt.legend(ls_symbols)
    plt.ylabel('Normalized Close')
    plt.xlabel('Date')
    plt.grid(True)
    plt.savefig('normalized.pdf', format='pdf')

    
    

    return mpld3.fig_to_html(fig)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['nickname'], request.form['password'], request.form['email'], request.form['age'], request.form['address'], request.form['county'], request.form['constituency'], request.form['ward'])
    db.session.add(user)
    db.session.commit()
    flash('User sucssefully registered')
    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()

@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)


@app.errorhandler(404)
def not_found_error(error):
    return (render_template('404.html'), 404)


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return (render_template('500.html'), 500)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page = 1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', title='Home', form=form, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    nickname = request.form['nickname']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = User.query.filter_by(nickname=nickname).first()
    if registered_user is None:
        flash('Username or Password is invalid', 'error')
        return redirect(url_for('register'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    if request.method != 'POST':
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route('/follow/<nickname>')
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))


@app.route('/viewstocks')
def viewstocks():
    stock_symbols = ['EGAD', 'KUKZ', 'KAPC','BAT', 'LIMT', 'REA',
                     'SASN', 'WTK', 'C&G', 'MASH', 'FIRE', 'BBK',
                      'CFC', 'COOP', 'DTK', 'EQTY', 'HFCK', 'I&M',
                       'KCB', 'NBK', 'NIC', 'SCBK', 'XPRS', 'KQ',
                        'LKL', 'NMG', 'SCAN', 'SGL', 'TPSE', 'UCHM',
                         'ARM', 'BAMB', 'BERG', 'CABL', 'PORT', 'KEGN',
                          'KENO', 'KPLC', 'TOTL', 'UMME', 'BRIT', 'CIC',
                           'JUB', 'KNRE', 'CFCI', 'PAFR', 'ICDC', 'OCH',
                            'TCL', 'BOC',  'CARB', 'EABL', 'EVRD', 'ORCH',
                             'MSC', 'UNGA', 'SCOM', 'HAFR', 'KPLC-P4', 'KPLC-P7', 'NASI', 'N20I']
    return render_template('viewstocks.html', stock_symbols=stock_symbols)


@app.route('/query', methods=['POST'])
def query():
    data = json.loads(request.data)
    return draw_fig(data['stocks'], data['start_date'], data['stop_date'])


@app.route('/event_form')
def event_form():
    stock_symbols = ['EGAD', 'KUKZ', 'KAPC','BAT', 'LIMT', 'REA',
                     'SASN', 'WTK', 'C&G', 'MASH', 'FIRE', 'BBK',
                      'CFC', 'COOP', 'DTK', 'EQTY', 'HFCK', 'I&M',
                       'KCB', 'NBK', 'NIC', 'SCBK', 'XPRS', 'KQ',
                        'LKL', 'NMG', 'SCAN', 'SGL', 'TPSE', 'UCHM',
                         'ARM', 'BAMB', 'BERG', 'CABL', 'PORT', 'KEGN',
                          'KENO', 'KPLC', 'TOTL', 'UMME', 'BRIT', 'CIC',
                           'JUB', 'KNRE', 'CFCI', 'PAFR', 'ICDC', 'OCH',
                            'TCL', 'BOC',  'CARB', 'EABL', 'EVRD', 'ORCH',
                             'MSC', 'UNGA', 'SCOM', 'HAFR', 'KPLC-P4', 'KPLC-P7', 'NASI', 'N20I']
  
    return render_template('event_study.html', stock_symbols=stock_symbols)


@app.route('/study', methods=['POST'])
def study():
    data = json.loads(request.data)
    return event_study(data['start_date'], data['stop_date'], data['price_change_low'], data['price_change_high'])


@app.route('/visualise')
def visualise():
    stock_symbols = ['EGAD', 'KUKZ', 'KAPC','BAT', 'LIMT', 'REA', 'SASN', 'WTK', 'C&G', 'MASH', 'FIRE', 'BBK', 'CFC', 'COOP', 'DTK', 'EQTY', 'HFCK', 'I&M', 'KCB', 'NBK', 'NIC', 'SCBK', 'XPRS', 'KQ', 'LKL', 'NMG', 'SCAN', 'SGL', 'TPSE', 'UCHM', 'ARM', 'BAMB', 'BERG', 'CABL', 'PORT', 'KEGN', 'KENO', 'KPLC', 'TOTL', 'UMME', 'BRIT', 'CIC', 'JUB', 'KNRE', 'CFCI', 'PAFR', 'ICDC', 'OCH', 'TCL', 'BOC',  'CARB', 'EABL', 'EVRD', 'ORCH', 'MSC', 'UNGA', 'SCOM', 'HAFR', 'KPLC-P4', 'KPLC-P7', 'NASI', 'N20I']
  
    return render_template('visualise.html', stock_symbols=stock_symbols)


@app.route('/visualise_boll', methods=['POST'])
def visualise_boll():
    data = json.loads(request.data)
    return bollinger_events(data['stocks'], data['start_date'], data['stop_date'])


@app.route('/simulate_form')
def simulate_form():
    stock_symbols = ['EGAD', 'KUKZ', 'KAPC','BAT', 'LIMT', 'REA', 'SASN', 'WTK', 'C&G', 'MASH', 'FIRE', 'BBK', 'CFC', 'COOP', 'DTK', 'EQTY', 'HFCK', 'I&M', 'KCB', 'NBK', 'NIC', 'SCBK', 'XPRS', 'KQ', 'LKL', 'NMG', 'SCAN', 'SGL', 'TPSE', 'UCHM', 'ARM', 'BAMB', 'BERG', 'CABL', 'PORT', 'KEGN', 'KENO', 'KPLC', 'TOTL', 'UMME', 'BRIT', 'CIC', 'JUB', 'KNRE', 'CFCI', 'PAFR', 'ICDC', 'OCH', 'TCL', 'BOC',  'CARB', 'EABL', 'EVRD', 'ORCH', 'MSC', 'UNGA', 'SCOM', 'HAFR', 'KPLC-P4', 'KPLC-P7', 'NASI', 'N20I']
  
    return render_template('simulate_form.html', stock_symbols=stock_symbols)


@app.route('/simulate', methods=['POST'])
def mysimulator():
    data = json.loads(request.data)
    end, portfolio, start, sharpe, total_return, sd, avg_daily_rets = simulate(data['start_date'], data['stop_date'], data['cash'], data['price_change_low'], data['price_change_high'])
    return render_template('results_form.html', dt_end=end, dt_start=start, myportfolio=portfolio, mysharpe=sharpe, returns=total_return, sdev=sd, adr=avg_daily_rets)


@app.route('/results_form')
def myresults(dt_end, dt_start, myportfolio, mysharpe, returns, sdev, adr):
    print results
    return (dt_end,
     dt_start,
     myportfolio,
     mysharpe,
     returns,
     sdev,
     adr)
