from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Роутер для API
router = DefaultRouter()
router.register(r'movies', views.MovieViewSet, basename='movie')

urlpatterns = [
    # # URL из первой лабораторной
    # path('', views.index, name='home'),
    # path('categories/<int:catid>/', views.categories),
    # path('archive/<int:year>/', views.archive),

    path('', views.index, name='home'),

    # API
    path('api/', include(router.urls)),

]