from django.urls import path

from . import views

urlpatterns = [
    path('bibliography/', views.bibliography, name='bibliography'),
    path('search/', views.search, name='search'),
    path('object/<int:object_id>', views.object, name='object'),
    path('register/', views.register, name='register'),
    path('my_pottery/', views.UserPotteryListView.as_view(), name='my_pottery'),
    path('pottery_description/', views.get_pottery_description, name='pottery_description'),
]


