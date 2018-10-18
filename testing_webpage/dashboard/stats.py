"""
Has views of stats.
"""

import pandas as pd
from django.shortcuts import render
from fusioncharts import FusionCharts

from dashboard.models import Candidate, StateEvent
from dashboard import constants as cts
from beta_invite.models import Campaign


CHART = {
    "xAxisName": "Month",
    "yAxisName": "Count",
    "numberPrefix": "",
    "paletteColors": "#0075c2",
    "bgColor": "#ffffff",
    "borderAlpha": "0",
    "canvasBorderAlpha": "0",
    "usePlotGradientColor": "0",
    "plotBorderAlpha": "10",
    "placevaluesInside": "1",
    "rotatevalues": "1",
    "valueFontColor": "#ffffff",
    "showXAxisLine": "1",
    "xAxisLineColor": "#999999",
    "divlineColor": "#999999",
    "divLineIsDashed": "1",
    "showAlternateHGridColor": "0",
    "subcaptionFontBold": "0",
    "subcaptionFontSize": "14"
}


def get_month_format(number):
    if number < 10:
        return '0' + str(number)
    else:
        return str(number)


def candidates_count(request):
    # Chart data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    data_source = dict()
    CHART["caption"] = "Total candidates registrations"
    data_source['chart'] = CHART

    data_source['data'] = []

    my_candidates = [c for c in Candidate.objects.filter(removed=False)]

    data = pd.DataFrame()
    data['id'] = [c.pk for c in my_candidates]
    data['created_at'] = [c.created_at for c in my_candidates]
    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.sort_values(by=['month'], inplace=True)

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    gp = pd.DataFrame(gp)

    for idx, row in gp.iterrows():
        data = dict()
        data['label'] = idx
        data['value'] = str(row['id'])
        data_source['data'].append(data)

        # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def campaign_count(request):
    # Chart data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    data_source = dict()
    CHART["caption"] = "Total campaign registrations"
    data_source['chart'] = CHART

    data_source['data'] = []

    my_campaigns = [c for c in Campaign.objects.filter(removed=False)]

    data = pd.DataFrame()
    data['id'] = [c.pk for c in my_campaigns]
    data['created_at'] = [c.created_at for c in my_campaigns]
    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.sort_values(by=['month'], inplace=True)

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    gp = pd.DataFrame(gp)

    for idx, row in gp.iterrows():
        data = dict()
        data['label'] = idx
        data['value'] = str(row['id'])
        data_source['data'].append(data)

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


# TODO: add
def operational_efficiency():
    pass


def render_forecast(request, graph_type):

    data_source = dict()
    CHART["caption"] = "Total Forecasts"
    data_source['chart'] = CHART

    data_source['data'] = []

    if graph_type == 'all':
        events = [e for e in StateEvent.objects.filter(use_machine_learning=True)]
    elif graph_type == 'positive':
        events = [e for e in StateEvent.objects.filter(use_machine_learning=True, forecast=True)]
    elif graph_type == 'negative':
        events = [e for e in StateEvent.objects.filter(use_machine_learning=True, forecast=False)]
    else:
        raise NotImplementedError('abraço apertado')

    data = pd.DataFrame()
    data['id'] = [c.pk for c in events]
    data['created_at'] = [c.created_at for c in events]
    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.sort_values(by=['month'], inplace=True)

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    gp = pd.DataFrame(gp)

    for idx, row in gp.iterrows():
        data = dict()
        data['label'] = idx
        data['value'] = str(row['id'])
        data_source['data'].append(data)

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def number_of_forecasts(request):
    return render_forecast(request, 'all')


def positive_forecasts(request):
    return render_forecast(request, 'positive')


def negative_forecasts(request):
    return render_forecast(request, 'negative')
