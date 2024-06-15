from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title = 'Instagram project',
        default_version='v1',
        description='difficult authorization system',
        contact=openapi.Contact(email='abduqodirdusmurodov@gmail.com')
    ),
    public=True,
    permission_classes=[IsAuthenticatedOrReadOnly, ],
    authentication_classes=[JWTAuthentication, ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls'))
]

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
