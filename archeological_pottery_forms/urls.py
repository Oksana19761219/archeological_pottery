from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('object/<int:object_id>', views.object, name='object'),
    path('register/', views.register, name='register'),
    path('my_pottery/', views.UserPotteryListView.as_view(), name='my_pottery'),
    path('describe/<int:object_id>', views.get_pottery_description, name='describe'),
    path('read_drawings/<int:object_id>', views.vectorize_drawings, name='read_drawings'),
    path('my_ceramic/', views.show_ceramic_profiles, name='my_ceramic')
]


