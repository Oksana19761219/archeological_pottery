from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('object/<int:object_id>', views.object, name='object'),
    path('register/', views.register, name='register'),
    path('describe/<int:object_id>', views.get_pottery_description, name='describe'),
    path('read_drawings/<int:object_id>', views.vectorize_drawings, name='read_drawings'),
    path('view_correlation/', views.view_correlation, name='view_correlation'),
    path('calculate_correlation/', views.calculate_correlation_coefficient, name='calculate_correlation'),
    path('review_profiles/', views.review_profiles, name='review_profiles')
]


