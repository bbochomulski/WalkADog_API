"""django_main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from API.views import *
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'walks', WalksViewSet)
router.register(r'extended_user', ExtendedUserViewSet)
router.register(r'client', ClientViewSet)
router.register(r'dog', DogViewSet)
router.register(r'trainer', TrainerViewSet)
router.register(r'trainer_review', TrainerReviewViewSet)
router.register(r'notification', NotificationViewSet)
router.register(r'coords', CoordsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-token-auth/', CustomAuthToken.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
