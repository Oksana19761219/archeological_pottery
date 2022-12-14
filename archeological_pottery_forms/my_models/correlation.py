import pandas as pd
from ..models import ContourCorrelation
from .my_decorators import calculate_time


# @calculate_time
def calculate_correlation (this_contour, other_contours, find_id, neck_min_y, shoulders_min_y):
    this_contour_sorted = this_contour.sort_values(by=['y', 'x'], ascending=True)
    this_contour_grouped = this_contour_sorted.groupby(['find_id', 'y'])['x']
    contour_x_max = this_contour_grouped.max().reset_index()
    contour_x_min = this_contour_grouped.min().reset_index()
    contour_to_correlate = contour_x_max
    contour_to_correlate['width'] = contour_x_max['x'] - contour_x_min['x']

    if neck_min_y:
        contour_to_correlate_neck = contour_to_correlate[contour_to_correlate['y'] < neck_min_y]
    else:
        contour_to_correlate_neck = pd.DataFrame()

    if neck_min_y and shoulders_min_y:
        contour_to_correlate_shoulders = contour_to_correlate[
            (contour_to_correlate['y'] >= neck_min_y) & (contour_to_correlate['y'] < shoulders_min_y)]
    elif neck_min_y and not shoulders_min_y:
        contour_to_correlate_shoulders = contour_to_correlate[contour_to_correlate['y'] >= neck_min_y]
    else:
        contour_to_correlate_shoulders = pd.DataFrame()

    if shoulders_min_y:
        contour_to_correlate_body = contour_to_correlate[contour_to_correlate['y'] >= shoulders_min_y]
    else:
        contour_to_correlate_body = pd.DataFrame()

    contours_sorted = other_contours.sort_values(by=['find_id', 'y', 'x'], ascending=True)
    contours_grouped = contours_sorted.groupby(['find_id', 'y'])
    contours_x_max = contours_grouped['x'].max().reset_index()
    contours_x_min = contours_grouped['x'].min().reset_index()
    contours_to_correlate = contours_x_max
    contours_to_correlate['width'] = contours_x_max['x'] - contours_x_min['x']

    contours_merged = pd.merge(contours_to_correlate, contour_to_correlate, how='inner', on=['y'])
    length_compared = contours_merged.groupby('find_id_x').count()['y'].reset_index()
    length_compared = length_compared.rename(columns={'y': 'length_compared'})

    correlation = contours_merged.groupby('find_id_x').corr().unstack()
    correlation_width = correlation[('width_x', 'width_y')].reset_index()
    correlation_x = correlation[('x_x', 'x_y')].reset_index()

    if not contour_to_correlate_neck.empty:
        contours_merged_neck = pd.merge(contours_to_correlate, contour_to_correlate_neck, how='inner', on=['y'])
        correlation_neck = contours_merged_neck.groupby('find_id_x').corr().unstack()
        correlation_x_neck = correlation_neck[('x_x', 'x_y')].reset_index()
        correlation_x_neck = correlation_x_neck.droplevel(1, axis=1)
        correlation_x_neck = correlation_x_neck.rename(columns={'x_x': 'correlation_x_neck'})
    else:
        correlation_x_neck = pd.DataFrame()

    if not contour_to_correlate_shoulders.empty:
        contours_merged_shoulders = pd.merge(contours_to_correlate, contour_to_correlate_shoulders, how='inner',
                                             on=['y'])
        correlation_shoulders = contours_merged_shoulders.groupby('find_id_x').corr().unstack()
        correlation_x_shoulders = correlation_shoulders[('x_x', 'x_y')].reset_index()
        correlation_x_shoulders = correlation_x_shoulders.droplevel(1, axis=1)
        correlation_x_shoulders = correlation_x_shoulders.rename(columns={'x_x': 'correlation_x_shoulders'})
    else:
        correlation_x_shoulders = pd.DataFrame()

    if not contour_to_correlate_body.empty:
        contours_merged_body = pd.merge(contours_to_correlate, contour_to_correlate_body, how='inner', on=['y'])
        correlation_body = contours_merged_body.groupby('find_id_x').corr().unstack()
        correlation_x_body = correlation_body[('x_x', 'x_y')].reset_index()
        correlation_x_body = correlation_x_body.droplevel(1, axis=1)
        correlation_x_body = correlation_x_body.rename(columns={'x_x': 'correlation_x_body'})
    else:
        correlation_x_body = pd.DataFrame()


    result = pd.merge(correlation_x, correlation_width, how='inner', on=[('find_id_x', '')])
    result = pd.merge(result.droplevel(1, axis=1), length_compared, how='inner', on=['find_id_x'])
    if not correlation_x_neck.empty:
        result = pd.merge(result, correlation_x_neck, how='left', on=['find_id_x'])
    else:
        result['correlation_x_neck'] = 0
    if not correlation_x_shoulders.empty:
        result = pd.merge(result, correlation_x_shoulders, how='left', on=['find_id_x'])
    else:
        result['correlation_x_shoulders'] = 0
    if not correlation_x_body.empty:
        result = pd.merge(result, correlation_x_body, how='left', on=['find_id_x'])
    else:
        result['correlation_x_body'] = 0
    result = result.rename(columns={'find_id_x': 'find_1',
                                    'x_x': 'correlation_x',
                                    'width_x': 'correlation_width'})
    result['find_2'] = find_id
    result['correlation_avg'] = (result['correlation_x_neck'] + result['correlation_x_shoulders'] + result['correlation_x_body']) / 3
    result = result.fillna(value=0)


    df_records = result.to_dict('records')
    model_instances = [ContourCorrelation(
        find_1=record['find_1'],
        find_2=record['find_2'],
        correlation_x=round(record['correlation_x'], 4),
        correlation_width=round(record['correlation_width'],4),
        correlation_x_neck=round(record['correlation_x_neck'],4),
        correlation_x_shoulders=round(record['correlation_x_shoulders'], 4),
        correlation_x_body=round(record['correlation_x_body'], 4),
        correlation_avg=round(record['correlation_avg'], 4),
        length_compared=record['length_compared']
    ) for record in df_records]

    ContourCorrelation.objects.bulk_create(model_instances)



