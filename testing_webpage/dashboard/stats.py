"""
Has views of stats.
"""

import datetime
import pandas as pd
from django.shortcuts import render
from fusioncharts import FusionCharts
from django.db.models import Q

from dashboard.models import Candidate, StateEvent, State
from dashboard import constants as cts
from beta_invite.models import Campaign, User


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

    data_source['data'] = []
    for idx, row in gp.iterrows():
        data_source['data'].append({'label': idx, 'value': str(row['id'])})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def number_of_forecasts(request):
    return render_forecast(request, 'all')


def positive_forecasts(request):
    return render_forecast(request, 'positive')


def negative_forecasts(request):
    return render_forecast(request, 'negative')


# TODO: complete this shit!
def candidates_per_new_user(request):
    """
    This is equivalent to this SQL:
    select s.m, cast(s.candidate_count as float) / cast(s.user_count as float) from
        (select date_trunc('month', u.created_at) as m,
                count(distinct u.id) user_count,
                count(distinct c.id) candidate_count
                from candidates c
                inner join users u on c.user_id = u.id
                where not removed and c.state_id != 11
                and u.created_at > '2018-01-01'
                group by m order by m) as s;
    :param request:
    :return:
    """

    data_source = dict()
    CHART["caption"] = "Average candidates per user"
    data_source['chart'] = CHART

    columns = ['id', 'user_id', 'user__created_at']
    data = pd.DataFrame(list(Candidate.objects.filter(~Q(state=State.objects.get(code='P')),
                                                      removed=False,
                                                      user__created_at__gt=datetime.datetime(year=2018, month=1, day=1)).values_list(*columns)), columns=columns)
    data['month'] = data['user__created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                                 m=get_month_format(date.month)))
    data.drop('user__created_at', inplace=True, axis=1)

    gp = pd.groupby(data, by=['month', 'user_id']).aggregate({'id': 'count'})
    data = pd.DataFrame(gp)
    data.reset_index(inplace=True)

    gp = pd.groupby(data, by=['month']).aggregate({'user_id': 'count',
                                                   'id': 'sum'})
    data = pd.DataFrame(gp)
    data.reset_index(inplace=True)

    data.sort_values(by=['month'], inplace=True)
    data.set_index('month', inplace=True)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(round(row['id'] / row['user_id'], 2))})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


# TODO: implement, more than one campaign counter:
"""
select s.m,
       s.candidate_count - s.user_count
       from (select date_trunc('month', u.created_at) as m,
                    count(distinct u.id) user_count,
                    count(distinct c.id) candidate_count
             from candidates c inner join users u on c.user_id = u.id
                    where not removed and c.state_id != 11
                    and u.created_at > '2018-01-01'
                    group by m order by m) as s;
"""
