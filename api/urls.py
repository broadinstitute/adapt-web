from django.urls import include, path
from rest_framework import routers
from rest_framework import renderers
from . import views

# router = routers.DefaultRouter()
# router.register(r'adaptruns', views.ADAPTRunViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('adaptruns/', views.adaptrun_list),
    path('adaptruns/<int:pk>/', views.adaptrun_detail),
    # path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]