from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import json, requests
import boto3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

company_stock_name = {"Adobe":"ADBE", "BankOfAmerica":"BAC" ,"Facebook":"FB", "IBM":"IBM","Netflix":"NFLX",
                      "Qualcomm":"QCOM", "SAP":"SAP", "ServiceNow":"NOW"}


# Get the company current data using query
def get_companies_data():
    latest_stock_price = {}

    dynamodb = boto3.resource('dynamodb')
    table_names = get_tables("Adobe")
    for i in table_names:
        all_table = dynamodb.Table(i)
        all_response = all_table.scan()['Items']
        # insert_latest_stock_price(i, all_response[0]['Date'])
        if '-' in all_response[0]['Date']:
            all_response.sort(key=lambda date: datetime.strptime(date['Date'], '%Y-%m-%d'), reverse=True)
        else:
            all_response.sort(key=lambda date: datetime.strptime(date['Date'], '%m/%d/%Y'), reverse=True)
        latest_stock_price[i] = all_response[0]['Close']

    return latest_stock_price


# When in API date is specified we will call this function to display data
def data_with_date(company_name, days):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(company_name)
    # Select query to get all data
    new_old_response = table.scan()['Items']
    old_new_response = new_old_response
    new_old_response.sort(key=lambda x: datetime.strptime(x['Date'], '%m/%d/%Y'),
                          reverse=True)
    old_new_response.sort(key=lambda x: datetime.strptime(x['Date'], '%m/%d/%Y'))
    res = pd.DataFrame.from_dict(old_new_response[-int(days):])

    fig = go.Figure(data=[go.Candlestick(
        x=res['Date'],
        open=res['Open'], high=res['High'],
        low=res['Low'], close=res['Close'],
        increasing_line_color='green', decreasing_line_color='red'
    )])

    fig.update_layout(xaxis_rangeslider_visible=False)
    figure_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    html_form = {
        "company_name": company_name,
        "figure_html": figure_html,
        "latest_close": new_old_response[0]['Close'],
        "latest_low": new_old_response[0]['Low'],
        "latest_high": new_old_response[0]['High'],
        "latest_open": new_old_response[0]['Open'],
        "latest_volume": int(new_old_response[0]['Volume']) // 1000000,
    }

    return html_form


def get_tables(company_name):
    client = boto3.client("dynamodb")
    response = client.list_tables(
        ExclusiveStartTableName=company_name,
        Limit=20
    )

    response['TableNames'].append(company_name)
    return response['TableNames']


# When in API date is not specified we will call this function to display data
def data_with_no_date(company_name):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(company_name)
    new_old_response = table.scan()['Items']
    old_new_response = new_old_response
    new_old_response.sort(key=lambda x: datetime.strptime(x['Date'], '%m/%d/%Y'),
                          reverse=True)
    old_new_response.sort(key=lambda x: datetime.strptime(x['Date'], '%m/%d/%Y'))
    res = pd.DataFrame.from_dict(old_new_response)

    # Plotly is used to plot candlestick figure
    fig = go.Figure(data=[go.Candlestick(
        x=res['Date'],
        open=res['Open'], high=res['High'],
        low=res['Low'], close=res['Close'],
        increasing_line_color='green', decreasing_line_color='red'
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)
    figure_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    html_form = {
        "company_name": company_name,
        "figure_html": figure_html,
        "latest_close": new_old_response[0]['Close'],
        "latest_low": new_old_response[0]['Low'],
        "latest_high": new_old_response[0]['High'],
        "latest_open": new_old_response[0]['Open'],
        "latest_volume": int(new_old_response[0]['Volume']) // 1000000,
    }

    return html_form


# Insert new value into database using Alphavantage API call
def insert_latest_stock_price(company_name, date):
    data = requests.get(
        'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+company_stock_name[company_name]+'&outputsize=full&apikey=GOFBJYEI7TM7B7T9')
    res = json.loads(data.text)
    new_data = ''
    i = ''
    for i in res['Time Series (Daily)']:
        new_data = res['Time Series (Daily)'][i]
        break
    new_date = datetime.strptime(i, '%Y-%m-%d').strftime('%m/%d/%Y')
    if date != new_date and company_name != "IBM":
        stock_data = {
            'Date': new_date,
            'Close': new_data['4. close'],
            'High': new_data['2. high'],
            'Open': new_data['1. open'],
            'Low': new_data['3. low'],
            'OpenInt': str(0),
            'Volume': new_data['5. volume'],
        }

        dynamodb = boto3.resource('dynamodb')

        table = dynamodb.Table(company_name)
        # Update request
        table.put_item(Item=stock_data)

    else:
        return