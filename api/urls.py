from django.urls import include, path
from rest_framework import routers
from rest_framework import renderers
from . import views

router = routers.DefaultRouter()
router.register(r'adaptruns', views.ADAPTRunViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
