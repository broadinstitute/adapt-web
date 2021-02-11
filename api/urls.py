from django.urls import include, path
from rest_framework import routers
from rest_framework import renderers
from rest_framework.authtoken import views as auth_views
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'adaptruns', views.ADAPTRunViewSet)
router.register(r'virus', views.VirusViewSet)
router.register(r'assay', views.AssayViewSet)
router.register(r'leftprimer', views.LeftPrimerViewSet)
router.register(r'rightprimer', views.RightPrimerViewSet)
router.register(r'crrnaset', views.crRNASetViewSet)
router.register(r'crrna', views.crRNAViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', auth_views.obtain_auth_token)
]
