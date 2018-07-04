from django.urls import path
from django.views.generic import TemplateView
from .views import (
    SetUserInBinaryAPIView,
    GetTreeAPIView,
    PointsHistoryAPIView,
    StatusAPIView,
    ChangeStatusAPIView,
    DeleteNodeAPIView,
)


app_name = 'tree'
urlpatterns = [
    path('', TemplateView.as_view(template_name='tree/examle-tree-view.html'), name='index'),
    path('<str:api_key>/get-tree/', GetTreeAPIView.as_view(), name='get-tree'),
    path('<str:api_key>/set-user-to-tree/', SetUserInBinaryAPIView.as_view(), name='set-user-to-tree'),
    path('<str:api_key>/get-points-history/', PointsHistoryAPIView.as_view(), name='get-points-history'),
    path('<str:api_key>/get-statuses/', StatusAPIView.as_view(), name='get-statuses'),
    path('<str:api_key>/change-user-status/', ChangeStatusAPIView.as_view(), name='change-user-status'),
    path('<str:api_key>/delete-nodes/', DeleteNodeAPIView.as_view(), name='delete-nodes'),
]
