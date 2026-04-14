from django.urls import path

from .views import rectangle_demo, signals_assignment_demo

urlpatterns = [
    path("rectangle/", rectangle_demo, name="rectangle-demo"),
    path("signals-assignment/", signals_assignment_demo, name="signals-assignment-demo"),
]
