import random
import string, os
from .models import get_companies_data, data_with_date, data_with_no_date
from django.shortcuts import render

table_names_json = {"adobe":"Adobe", "bankofamerica":"BankOfAmerica", "facebook":"Facebook",
                    "ibm":"IBM", "netflix":"Netflix", "qualcomm":"Qualcomm", "sap": "SAP",
                    "servicenow": "ServiceNow"}


# render the template by getting companies current data
def home(request):
    companies_data = get_companies_data()
    return render(request, 'stockmarketapis/home.html', companies_data)


# Get request API will execute when user enters url then it will render it to populate companies data.
def api(request):
    company_name = ''
    response_date = ''
    # If company_name is present in api
    if request.GET:
        company_name = (request.GET['name']).lower()
        company_name = table_names_json[company_name]

    try:
        # If dayaAgo is present in api
        if "daysAgo" in request.GET:
            days = request.GET['daysAgo']

            try:
                # If api_key is present in api
                if request.GET['key'] and days:
                    key = request.GET['key']
                    api_key = ''
                    if 'api_key' in os.environ:
                        api_key = os.environ['api_key']
                    # if the api key and url key is similar so user is authnticated
                    if key == api_key:
                        response_data = data_with_date(company_name, days)

                        return render(request, 'stockmarketapis/company.html', response_data)

                    else:
                        error = "401 UNAUTHORIZED USER"
                        return render(request, 'stockmarketapis/error.html', error)

            except Exception as error:
                error = "There is some issue by entering api key"
                return render(request, 'stockmarketapis/error.html', error)

        else:
            response_date = data_with_no_date(company_name)

    except Exception as error:
        error = "There is some issue with processing the data for specified days"
        return render(request, 'stockmarketapis/error.html', error)

    return render(request, 'stockmarketapis/company.html', response_date)


# Generate random api_key every time user click to generate new api
def apikey(request):
    get_apikey = ''
    for i in range(1):
        apijey_int = random.randint(0, 9)
        apikey_string = string.ascii_lowercase[6:10]
        apijey_int_1 = random.randint(10, 35)
        apikey_string_1 = string.ascii_lowercase[15:21]
        apijey_int_2 = random.randint(50, 100)
        apikey_string_2 = string.ascii_lowercase[2:5]
        apijey_int_3 = random.randint(101,120)
        get_apikey += str(apijey_int) + str(apikey_string) + str(apijey_int_1) + str(apikey_string_1) + \
                      str(apijey_int_2) + str(apikey_string_2) + str(apijey_int_3)

    os.environ['api_key'] = get_apikey
    pass_apikey = {
        'api_key': get_apikey
    }

    return render(request, "stockmarketapis/apikey.html", pass_apikey)







