from django.urls import path, re_path, include
from .views import (
    SetUserInBinaryAPIView,
    GetTreeAPIView,
)


app_name = 'tree'
urlpatterns = [
    path('<str:api_key>/get-tree/', GetTreeAPIView.as_view(), name='get-tree'),
    path('<str:api_key>/set-user-to-tree/', SetUserInBinaryAPIView.as_view(), name='set-user-to-tree'),
]
