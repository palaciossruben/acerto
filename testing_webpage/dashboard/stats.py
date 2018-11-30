"""
Has views of stats.
"""

import pandas as pd
from django.shortcuts import render
from fusioncharts import FusionCharts
from django.db.models import Q

from dashboard.models import Candidate, StateEvent, State, User
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


def candidate_count(request):
    # Chart data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    data_source = dict()
    CHART["caption"] = "Total candidates registrations"
    data_source['chart'] = CHART

    data_source['data'] = []

    columns = ['id', 'created_at']
    data = pd.DataFrame(list(Candidate.objects.filter(~Q(state=State.objects.get(code='P'), removed=False))
                             .values_list(*columns)), columns=columns)

    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))

    data.drop('created_at', axis=1, inplace=True)

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
    CHART["caption"] = graph_type + "forecasts"
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


def get_number_of_second_candidates():
    """
    select date_trunc('month', created_at) m,
      count(*) new_candidates
    from candidates
    where id not in (select min(id) first_candidate_id
                       from candidates
                       where not removed
                       and state_id!=11
                       group by user_id)
    and state_id!=11
    and not removed
    group by m
    order by m;
    """

    first_candidate_columns = ['id', 'user_id']
    values = Candidate.objects.filter(~Q(state=State.objects.get(code='P')),
                                      removed=False).values_list(*first_candidate_columns)

    candidates = pd.DataFrame(list(values), columns=first_candidate_columns)

    gb = candidates.groupby('user_id').agg({'id': min})
    first_ids = pd.DataFrame(gb)['id']

    columns = ['id', 'created_at']
    data = pd.DataFrame(list(Candidate.objects.filter(~Q(state=State.objects.get(code='P')),
                                                      ~Q(pk__in=first_ids),
                                                      removed=False).values_list(
        *columns)), columns=columns)

    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.drop('created_at', inplace=True, axis=1)

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    data = pd.DataFrame(gp)

    return data


def get_number_of_unique_users():
    """
    select date_trunc('month', created_at) m,
      count(distinct user_id) unique_users
    from candidates
    where state_id!=11
    and not removed
    group by m
    order by m;
    """

    first_candidate_columns = ['user_id', 'user__created_at']
    data = pd.DataFrame(list(Candidate.objects.filter(~Q(state=State.objects.get(code='P')), removed=False)
                             .values_list(*first_candidate_columns)), columns=first_candidate_columns)

    data['month'] = data['user__created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                                 m=get_month_format(date.month)))
    data.drop('user__created_at', inplace=True, axis=1)

    gp = pd.groupby(data, by='month').aggregate({'user_id': pd.Series.nunique})
    data = pd.DataFrame(gp)

    return data


def candidates_per_user(request):
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
    CHART["caption"] = "Second candidates vs new Users"
    data_source['chart'] = CHART

    data = get_number_of_second_candidates()
    users = get_number_of_unique_users()
    data = data.join(users)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(round(row['id'] / row['user_id'], 2))})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def candidates_from_old_users(request):
    """
    select date_trunc('month', created_at) m,
      count(*) new_candidates
    from candidates
    where id not in (select min(id) first_candidate_id
                       from candidates
                       where not removed
                       and state_id!=11
                       group by user_id)
    and state_id!=11
    and not removed
    group by m
    order by m;
    """

    data_source = dict()
    CHART["caption"] = "Candidates from old user"
    data_source['chart'] = CHART

    data = get_number_of_second_candidates()

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(round(row['id']))})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def stuck_candidates(request):
    """
    People don't want to do the tests, how many are there?
    select date_trunc('month', c.created_at) m,
           cast(count(distinct case when s.code in ('BL', 'P') then c.id end) as float) / cast(count(distinct c.id) as float)
    from candidates c inner join states s on s.id = c.state_id where not removed
    group by m order by m;
    """

    data_source = dict()
    CHART["caption"] = "Candidates in backlog or prospect"
    data_source['chart'] = CHART

    columns = ['id', 'state__code', 'created_at']
    data = pd.DataFrame(list(Candidate.objects.filter(removed=False)
                             .values_list(*columns)), columns=columns)
    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.drop('created_at', inplace=True, axis=1)

    data['stuck'] = data['state__code'].apply(lambda x: int(x in ['BL', 'P']))

    gp = pd.groupby(data, by='month').aggregate({'id': 'count',
                                                 'stuck': 'sum'})
    data = pd.DataFrame(gp)
    data.sort_index(inplace=True)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(round(row['stuck'] / row['id'], 2))})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def recommended_candidates(request):
    """
    Recommended
    """

    data_source = dict()
    CHART["caption"] = "Recommended candidates"
    data_source['chart'] = CHART

    columns = ['id', 'created_at']
    data = pd.DataFrame(list(Candidate.objects.filter(state__code__in=['GTJ', 'STC'], removed=False)
                             .values_list(*columns)), columns=columns)
    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.drop('created_at', inplace=True, axis=1)

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    data = pd.DataFrame(gp)
    data.sort_index(inplace=True)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(row['id'])})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


# TODO: make this with the orm we only have the query
def ml_automation_percentage(request):
    """
    # What percentage of recommended have been automatic?
    select m,
      cast(count(distinct automatic.id) as float) / cast(count(distinct my_all.id) as float)
      from (select date_trunc('month', c.created_at) m, c.id id
            from candidates c
              inner join states s on s.id = c.state_id
            where s.code in ('STC', 'GTJ')
              and c.created_at > '2018-10-01') my_all
    left join
      (select c.id id
       from candidates c
          inner join candidates_state_events ce on ce.candidate_id = c.id
          inner join state_events e on e.id = ce.stateevent_id
          inner join states s on s.id = e.to_state_id
       where e.use_machine_learning
          and e.forecast
          and s.code='STC'
          and c.created_at > '2018-10-01') automatic
    on my_all.id = automatic.id
    group by m
    order by m;
    """

    data_source = dict()
    CHART["caption"] = "Recommended candidates"
    data_source['chart'] = CHART

    columns = ['id', 'created_at']
    recommended = pd.DataFrame(list(Candidate.objects.filter(state__code__in=['GTJ', 'STC'],
                                                             removed=False)
                                    .values_list(*columns)), columns=columns)
    recommended['month'] = recommended['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                                         m=get_month_format(date.month)))
    recommended.drop('created_at', inplace=True, axis=1)

    automatic_columns = ['automatic_id', 'created_at']
    automatic = pd.DataFrame(list(Candidate.objects.filter(removed=False,
                                                           state_events__in=StateEvent.objects.filter(use_machine_learning=True,
                                                                                                      forecast=True,
                                                                                                      to_state__code='STC'))
                                  .values_list(*columns)), columns=automatic_columns)
    automatic.drop('created_at', inplace=True, axis=1)
    #lambda x: x.nunique()
    data = recommended.join(automatic, how='left')

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    data = pd.DataFrame(gp)
    data.sort_index(inplace=True)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(row['id'])})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def get_paid_campaign_registrations(request):
    """
    Paid registrations
    """

    data_source = dict()
    CHART["caption"] = "Paid Campaign registrations"
    data_source['chart'] = CHART

    columns = ['id', 'created_at']
    data = pd.DataFrame(list(Campaign.objects.filter(free_trial=False, removed=False)
                             .values_list(*columns)), columns=columns)
    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.drop('created_at', inplace=True, axis=1)

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    data = pd.DataFrame(gp)
    data.sort_index(inplace=True)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(row['id'])})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


def get_unique_users_registrations(request):
    """
    Unique users registered per month
    """

    data_source = dict()
    CHART["caption"] = "Unique user registrations"
    data_source['chart'] = CHART

    columns = ['id', 'created_at']
    data = pd.DataFrame(list(User.objects.all()
                             .values_list(*columns)), columns=columns)
    data['month'] = data['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                           m=get_month_format(date.month)))
    data.drop('created_at', inplace=True, axis=1)

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    data = pd.DataFrame(gp)
    data.sort_index(inplace=True)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(row['id'])})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})


# TODO: make the SQL query work in django work
def work_area_segment_match(request):
    """
    Get the percentage of match between workAreaSegments by month

    Checks if the candidate and its campaign have a match

    select date_trunc('month', c.created_at) as m,
      count(distinct (case when w.segment_id = wcam.segment_id then c.id end)),
      count(*) as all,
      cast(count(distinct (case when w.segment_id = wcam.segment_id then c.id end)) as float) / count(*)
    from candidates c
    inner join users u on u.id = c.user_id
    inner join work_areas w on w.id = u.work_area_id
    inner join campaigns cam on cam.id = c.campaign_id
    inner join work_areas wcam on wcam.id = cam.work_area_id
      where not cam.removed
    group by m order by m;
    """

    data_source = dict()
    CHART["caption"] = "WorkAreaSegment match percentage"
    data_source['chart'] = CHART

    columns = ['id', 'created_at', 'campaign__work_area__segment_id', 'user__work_area__segment_id']
    df = pd.DataFrame(list(Candidate.objects.filter(removed=False)
                                    .values_list(*columns)), columns=columns)
    df['month'] = df['created_at'].apply(lambda date: '{y}-{m}'.format(y=date.year,
                                                                       m=get_month_format(
                                                                         date.month)))
    df.drop('created_at', inplace=True, axis=1)

    #df['match'] = df.apply(lambda row: )

    #gb = df.groupby('month').agg({'percentage': })
    #df = pd.DataFrame(gb)

    automatic_columns = ['automatic_id', 'created_at']
    automatic = pd.DataFrame(list(Candidate.objects.filter(removed=False,
                                                           state_events__in=StateEvent.objects.filter(
                                                               use_machine_learning=True,
                                                               forecast=True,
                                                               to_state__code='STC'))
                                  .values_list(*columns)), columns=automatic_columns)
    automatic.drop('created_at', inplace=True, axis=1)
    # lambda x: x.nunique()
    data = df.join(automatic, how='left')

    gp = pd.groupby(data, by='month').aggregate({'id': 'count'})
    data = pd.DataFrame(gp)
    data.sort_index(inplace=True)

    data_source['data'] = []
    for idx, row in data.iterrows():
        data_source['data'].append({'label': idx, 'value': str(row['id'])})

    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column_2d = FusionCharts("column2D", "ex1", "600", "350", "chart-1", "json", data_source)
    return render(request, cts.STATS_INDEX, {'output': column_2d.render()})
