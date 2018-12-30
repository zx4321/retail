"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from django.urls import include
from rest_framework import routers
from rest_framework.authtoken.views import ObtainAuthToken

from retail.serializers import *
from retail.views import *
from rest_framework_jwt.views import obtain_jwt_token


router = routers.DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'provider', ProviderViewSet)
router.register(r'inlog', InLogViewSet)
router.register(r'order', OrderViewSet)
router.register(r'register', RegisterViewSet)
router.register(r'user/info', UserInfoViewSet)
# router.register(r'info', UserInfoViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('login/', obtain_jwt_token),
    path('admin/custom_link/', custom_view, name='custom_name'),
    path('miniapporder', miniappOrder, name='miniappOrder'),
    path('miniLogin', Login.as_view(), name='Login'),
    # path('info/', info)
    # url(r'^api-token-auth/', obtain_jwt_token),
]
