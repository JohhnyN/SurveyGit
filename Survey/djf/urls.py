from django.urls import path, include
from . import views
from .app_settings import SURVEYS_ADMIN_BASE_PATH

app_name = 'djf'
urlpatterns = [
    path('', views.SurveyListView.as_view(), name='index'),
    path('detail/<str:slug>/', views.DetailSurveyView.as_view(), name='detail'),
    path('edit/<int:pk>/', views.EditSurveyFormView.as_view(), name='edit'),
    path('detail/result/<int:pk>/', views.DetailResultSurveyView.as_view(), name='detail_result'),
    path('survey/<str:slug>/', views.CreateSurveyFormView.as_view(), name='create'),
    path('delete/<int:pk>/', views.DeleteSurveyAnswerView.as_view(), name='delete'),
    path('share/<str:slug>/', views.share_link, name='share_link'),
    path(SURVEYS_ADMIN_BASE_PATH, include('djf.admins.urls')),
]