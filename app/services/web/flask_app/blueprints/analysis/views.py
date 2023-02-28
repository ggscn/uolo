from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for

from flask_app.blueprints.analysis.forms import SearchForm
from flask_app.blueprints.user.models import User
from flask_app.blueprints.analysis.models import StockPrice, CompanyFactAnalysis
from flask_app.extensions import limiter
from sqlalchemy import Column

analysis = Blueprint('analysis', __name__, template_folder='templates')

#don't forget to rate limit!
@analysis.route('/')
def home():
    form = SearchForm()
    return render_template('analysis/home.html', form=form, data=data)

@analysis.route('/overview')
def overview():
    form = SearchForm()
    labels = CompanyFactAnalysis.query.with_entities(
        CompanyFactAnalysis.analysis_label
    ).distinct()
    choices =[(i.analysis_label, i.analysis_label) for i in set(labels)]
    choices = [('Select One', 'Select One')] + choices
    form.analysis_label.choices = choices
    return render_template('analysis/overview.html', form=form)

@analysis.route('/company-fact-chart')
def get_company_fact_chart():
    response = {
        'labels': [],
        'data': {}
    }
    analysis_label = request.args.get('analysis_label', None)
    ticker = request.args.get('ticker', None)

    if analysis_label is None or ticker is None:
        return jsonify({'error':'Could not find analysis'})
    company_facts = CompanyFactAnalysis.get_company_fact_chart_data(
        analysis_label, ticker)

    response['labels'].extend([x.frame for x in company_facts 
                if x.frame not in response['labels']])
    response['data'][ticker] = [float(x.val) for x in company_facts]
    return jsonify(response)


@analysis.route('/analysis/company-fact')
def get_company_fact():
    response = {'items':[], 'columns':['rank','ticker']}
    analysis_label = request.args.get('query', None)
    print(analysis_label)
    company_facts = CompanyFactAnalysis.get_company_fact(
        analysis_label)
    response['items'] = [{'rank': i,'ticker':x.ticker} 
        for i, x in enumerate(company_facts, start=1)]
        
    return jsonify(results=response)


@limiter.limit("3/minute")
@analysis.route('/get-quote', methods=['GET'])
def get_quote():
    response = {
        'labels': [],
        'data': {}
    }
    tickers = request.args.get('title', '').split(',')
    start_date, end_date = request.args.get('author', '').split(' - ')
    print(tickers, start_date, end_date)
    for ticker in tickers:
        ticker = ticker.upper()
        data = StockPrice.find_by_identity(
            ticker, start_date, end_date)
        if not data:
            StockPrice().backfill(ticker, start_date, end_date)
            data = StockPrice.find_by_identity(
                ticker, start_date, end_date)
        response['labels'].extend(
            [x.date.strftime('%Y-%m-%d') for x in data 
                if x.date.strftime('%Y-%m-%d') not in response['labels']])
        response['data'][ticker] = [float(x.close) for x in data]
    return jsonify(response)

@analysis.route('/privacy-policy')
def privacy_policy():
    return render_template('analysis/privacy-policy.html')

@analysis.route('/terms')
def terms():
    return render_template('analysis/terms.html')

@analysis.route('/backfill-prices')
def backfill_prices():
    
    from flask_app.blueprints.analysis.tasks import backfill
    backfill.delay()
    return redirect(url_for('analysis.overview'))

