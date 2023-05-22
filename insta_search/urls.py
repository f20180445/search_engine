from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search, name="search-page"),
    path('upload/', views.upload, name="upload-page"),
    path('uploaded/', views.uploaded, name="uploaded-page"),
    path('results/', views.go_to_results, name="results-page"),
]
