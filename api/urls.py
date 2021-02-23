from django.urls import include, path
from rest_framework import routers
from rest_framework import renderers
from rest_framework.authtoken import views as auth_views
from . import views


router = routers.DefaultRouter()
for view_name in dir(views):
    if view_name.endswith("ViewSet"):
        view = views.__dict__[view_name]
        if isinstance(view, type):
            base = view.serializer_class.Meta.model.__name__.lower()
            router.register(base, view, base)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', auth_views.obtain_auth_token)
]
