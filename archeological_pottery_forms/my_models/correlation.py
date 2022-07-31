import logging
import pandas as pd
from ..models import ContourCorrelation
from .my_decorators import calculate_time


logger = logging.getLogger(__name__)


@calculate_time
def calculate_correlation (this_contour, other_contours, find_id):
    this_contour_sorted = this_contour.sort_values(by=['y', 'x'], ascending=True)
    this_contour_grouped = this_contour_sorted.groupby(['find_id', 'y'])['x']
    contour_x_max = this_contour_grouped.max().reset_index()
    contour_x_min = this_contour_grouped.min().reset_index()
    contour_to_correlate = contour_x_max
    contour_to_correlate['width'] = contour_x_max['x'] - contour_x_min['x']

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

    result = pd.merge(correlation_x, correlation_width, how='inner', on=[('find_id_x', '')])
    result = pd.merge(result.droplevel(1, axis=1), length_compared, how='inner', on=['find_id_x'])
    result = result.rename(columns={'find_id_x': 'find_1',
                                    'x_x': 'correlation_x',
                                    'width_x': 'correlation_width'})
    result['find_2'] = find_id

    df_records = result.to_dict('records')
    model_instances = [ContourCorrelation(
        find_1=record['find_1'],
        find_2=record['find_2'],
        correlation_x=round(record['correlation_x'], 4),
        correlation_width=round(record['correlation_width'],4),
        length_compared=record['length_compared']
    ) for record in df_records]

    ContourCorrelation.objects.bulk_create(model_instances)
    logger.info('įrašyti koreliacijos koeficientai')


