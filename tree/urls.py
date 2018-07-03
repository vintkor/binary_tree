from django.urls import path, re_path, include
from .views import (
    SetUserInBinaryAPIView,
    GetTreeAPIView,
    PointsHistoryAPIView,
)


app_name = 'tree'
urlpatterns = [
    path('<str:api_key>/get-tree/', GetTreeAPIView.as_view(), name='get-tree'),
    path('<str:api_key>/set-user-to-tree/', SetUserInBinaryAPIView.as_view(), name='set-user-to-tree'),
    path('<str:api_key>/get-points-history/', PointsHistoryAPIView.as_view(), name='get-points-history'),
]
