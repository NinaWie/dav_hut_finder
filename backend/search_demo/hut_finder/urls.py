from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_view, name='search_view'),
    path('search/results/', views.search_results_view, name='search_results_view')
]