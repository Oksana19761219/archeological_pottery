from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bibliography/', views.bibliography, name='bibliography'),
    path('search/', views.search, name='search'),
    path('object/<int:object_id>', views.object, name='object'),
    path('register/', views.register, name='register'),
    path('my_pottery/', views.UserPotteryListView.as_view(), name='my_pottery'),
    path('describe/<int:object_id>', views.get_pottery_description, name='describe'),
    path('read_drawings/<int:object_id>', views.read_drawings, name='read_drawings'),
]


