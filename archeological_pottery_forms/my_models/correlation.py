import pandas as pd
from ..models import ContourCorrelation
from .my_decorators import calculate_time


# @calculate_time
def calculate_correlation (this_contour, other_contours, find_id):
    # this_contour_sorted = this_contour.sort_values(by=['y', 'x'], ascending=True)
    # this_contour_grouped = this_contour_sorted.groupby(['find_id', 'y'])[['x', 'curvature']]
    # contour_x_max = this_contour_grouped.max().reset_index()
    # contour_x_min = this_contour_grouped.min().reset_index()
    # contour_to_correlate = contour_x_max
    # contour_to_correlate['width'] = contour_x_max['x'] - contour_x_min['x']
    #
    # contours_sorted = other_contours.sort_values(by=['find_id', 'y', 'x'], ascending=True)
    # contours_grouped = contours_sorted.groupby(['find_id', 'y'])
    # contours_x_max = contours_grouped['x'].max().reset_index()
    # contours_x_min = contours_grouped['x'].min().reset_index()
    # contours_to_correlate = contours_x_max.merge(contours_sorted, how='inner', on=['find_id', 'y', 'x'])
    # contours_to_correlate['width'] = contours_x_max['x'] - contours_x_min['x']
    # contours_to_correlate = contours_to_correlate.drop(['id'], axis=1)
    #
    # contours_merged = pd.merge(contours_to_correlate, contour_to_correlate, how='inner', on=['y'])
    # length_compared = contours_merged.groupby('find_id_x').count()['y'].reset_index()
    # length_compared = length_compared.rename(columns={'y': 'length_compared'})
    #
    # correlation = contours_merged.groupby('find_id_x').corr().unstack()
    # correlation_width = correlation[('width_x', 'width_y')].reset_index()
    # correlation_x = correlation[('x_x', 'x_y')].reset_index()
    # correlation_curvature = correlation[('curvature_x', 'curvature_y')].reset_index()
    #
    # result = pd.merge(correlation_x, correlation_width, how='inner', on=[('find_id_x', '')])
    # result = pd.merge(result, correlation_curvature, how='inner', on=[('find_id_x', '')])
    # result = pd.merge(result.droplevel(1, axis=1), length_compared, how='inner', on=['find_id_x'])
    #
    # result = result.rename(columns={'find_id_x': 'find_1',
    #                                 'x_x': 'correlation_x',
    #                                 'curvature_x': 'correlation_curvature',
    #                                 'width_x': 'correlation_width'})


    this_contour_sorted = this_contour.sort_values(by=['y', 'x'], ascending=True)
    this_contour_grouped = this_contour_sorted.groupby(['find_id', 'y'])[['x', 'curvature']]
    contour_x_max = this_contour_grouped.max().reset_index()
    contour_x_min = this_contour_grouped.min().reset_index()
    contour_to_correlate = contour_x_max
    contour_to_correlate['width'] = contour_x_max['x'] - contour_x_min['x']

    contours_sorted = other_contours.sort_values(by=['find_id', 'y', 'x'], ascending=True)
    contours_grouped = contours_sorted.groupby(['find_id', 'y'])
    contours_x_max = contours_grouped['x'].max().reset_index()
    contours_x_min = contours_grouped['x'].min().reset_index()
    contours_to_correlate = contours_x_max.merge(contours_sorted, how='inner', on=['find_id', 'y', 'x'])
    contours_to_correlate['width'] = contours_x_max['x'] - contours_x_min['x']

    contours_merged = pd.merge(contours_to_correlate, contour_to_correlate, how='inner', on=['y'])
    correlation = contours_merged.groupby('find_id_x').corr().unstack()

    correlation_width = correlation[('width_x', 'width_y')].reset_index().droplevel(1, axis=1)
    correlation_x = correlation[('x_x', 'x_y')].reset_index().droplevel(1, axis=1)
    correlation_curvature = correlation[('curvature_x', 'curvature_y')].reset_index().droplevel(1, axis=1)

    length_compared = contours_merged.groupby('find_id_x').count()['y'].reset_index()
    length_compared = length_compared.rename(columns={'y': 'length_compared'})

    contours_merged['x_y_changed'] = contours_merged['x_y'] - contours_merged['x_y'].min()
    x_x_min = contours_merged.groupby('find_id_x')['x_x'].min().reset_index()
    x_x_min = x_x_min.rename(columns={'x_x': 'x_x_min'})
    contours_merged = pd.merge(contours_merged, x_x_min, how='inner', on=['find_id_x'])
    contours_merged['x_x_changed'] = contours_merged['x_x'] - contours_merged['x_x_min']
    contours_merged['x_diff'] = (contours_merged['x_y_changed'] - contours_merged['x_x_changed']).abs()
    area = contours_merged.groupby(['find_id_x'])['x_diff'].sum()

    result = pd.merge(correlation_x, correlation_width, how='inner', on=['find_id_x'])
    result = pd.merge(result, correlation_curvature, how='inner', on=['find_id_x'])
    result = pd.merge(result, length_compared, how='inner', on=['find_id_x'])
    result = pd.merge(result, area, how='inner', on=['find_id_x'])
    result = result.rename(columns={'find_id_x': 'find_1',
                                    'x_x': 'correlation_x',
                                    'curvature_x': 'correlation_curvature',
                                    'width_x': 'correlation_width',
                                    'x_diff': 'area'
                                    })

    result['find_2'] = find_id

    df_records = result.to_dict('records')
    model_instances = [ContourCorrelation(
        find_1=record['find_1'],
        find_2=record['find_2'],
        correlation_x=round(record['correlation_x'], 4),
        correlation_width=round(record['correlation_width'],4),
        correlation_curvature=round(record['correlation_curvature'],4),
        length_compared=record['length_compared'],
        area=record['area']
    ) for record in df_records]

    ContourCorrelation.objects.bulk_create(model_instances)



