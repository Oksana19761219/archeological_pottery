import logging
import pandas as pd
from ..models import ContourCorrelation
from .my_decorators import calculate_time

logger = logging.getLogger(__name__)


@calculate_time
def calculate_correlation (this_contour, other_contours, find_id):
    this_contour_sorted = this_contour.sort_values(by=['y', 'x'], ascending=True)
    this_contour_grouped = this_contour_sorted.groupby(['find_id', 'y'])['x']
    this_contour_x_max = this_contour_grouped.max().reset_index()

    other_contours_sorted = other_contours.sort_values(by=['find_id', 'y', 'x'], ascending=True)
    other_contours_grouped = other_contours_sorted.groupby(['find_id', 'y'])
    other_contours_x_max = other_contours_grouped['x'].max().reset_index()

    contours_merged = pd.merge(other_contours_x_max, this_contour_x_max, how='inner', on=['y'])
    correlation = contours_merged.groupby('find_id_x')[['x_x', 'x_y']].corr().unstack().iloc[:,1].dropna().reset_index()
    correlation['find_id_y'] = find_id

    df_records = correlation.to_dict('records')
    model_instances = [ContourCorrelation(

        find_1=record[('find_id_x', '')],
        find_2=record[('find_id_y', '')],
        correlation=round(record[('x_x', 'x_y')], 3)
    ) for record in df_records]
    ContourCorrelation.objects.bulk_create(model_instances)
    logger.info('įrašyti koreliacijos koeficientai')



