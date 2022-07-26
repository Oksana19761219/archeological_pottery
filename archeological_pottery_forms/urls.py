from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('object/<int:object_id>', views.object, name='object'),
    path('register/', views.register, name='register'),
    path('describe/<int:object_id>', views.get_pottery_description, name='describe'),
    path('read_drawings/<int:object_id>', views.vectorize_drawings, name='read_drawings'),
    path('my_ceramic/', views.review_ceramic_profiles, name='my_ceramic'),
    path('correlation/', views.view_correlation, name='correlation')
]


