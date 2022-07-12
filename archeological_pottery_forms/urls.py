from django.urls import path

from . import views

urlpatterns = [
    path('bibliography/', views.bibliography, name='bibliography'),
    path('search/', views.search, name='search'),
    path('object/<int:object_id>', views.object, name='object')
]


