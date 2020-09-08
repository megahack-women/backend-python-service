from django.urls import path
from backend import *
from api.views import *

urlpatterns = [
    path('', HelloWord.as_view()),
    path('person', PersonAPI.as_view()),
    path('person/<int:id>', PersonAPI.as_view()),
    path('person/<int:id>/group', GroupAPI.as_view())
]