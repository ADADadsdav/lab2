from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render, redirect
from rest_framework import viewsets, status, pagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Movie
from .serializers import MovieSerializer


# ---------- Функции из первой лабораторной ----------
def index(request):
    return HttpResponse("Страница приложения")


def categories(request, catid):
    return HttpResponse(f"<h1>Статьи по категориям</h1><p>{catid}</p>")


def archive(request, year):
    if int(year) > 2026:
        return redirect('home', permanent=True)
    return HttpResponse(f"<h1>Архив по годам</h1><p>{year}</p>")


# ---------- Обработчики ошибок ----------
def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Ресурс не найден</h1>')


def pageBadRequest(request, exception):
    return HttpResponseBadRequest('<h1>Неверный формат данных</h1>')


def pageServerError(request):
    return HttpResponseServerError('<h1>Внутренняя ошибка сервера</h1>')


def pageConflict(request, exception):
    return HttpResponse('<h1>Конфликт данных</h1>', status=409)


# ---------- API для второй лабораторной ----------
class CustomPagination(pagination.PageNumberPagination):
    """Кастомная пагинация в формате из задания"""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'total': self.page.paginator.count,
                'page': self.page.number,
                'limit': self.page_size,
                'totalPages': self.page.paginator.num_pages,
            }
        })


class MovieViewSet(viewsets.ViewSet):
    """
    API для работы с фильмами
    GET    /movies/          - список с пагинацией
    GET    /movies/{id}/     - получить один фильм
    POST   /movies/          - создать фильм
    PUT    /movies/{id}/     - полное обновление
    PATCH  /movies/{id}/     - частичное обновление
    DELETE /movies/{id}/     - мягкое удаление
    """
    pagination_class = CustomPagination

    def list(self, request):
        """GET /movies/ - список всех активных фильмов с пагинацией"""
        movies = Movie.active_objects.all()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(movies, request)
        serializer = MovieSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /movies/{id}/ - получить конкретный фильм"""
        movie = get_object_or_404(Movie.active_objects.all(), pk=pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """POST /movies/ - создать новый фильм"""
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            movie = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """PUT /movies/{id}/ - полностью обновить фильм"""
        movie = get_object_or_404(Movie.active_objects.all(), pk=pk)
        serializer = MovieSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """PATCH /movies/{id}/ - частично обновить фильм"""
        movie = get_object_or_404(Movie.active_objects.all(), pk=pk)
        serializer = MovieSerializer(movie, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """DELETE /movies/{id}/ - мягкое удаление"""
        movie = get_object_or_404(Movie.active_objects.all(), pk=pk)
        movie.delete()  # soft delete
        return Response(status=status.HTTP_204_NO_CONTENT)