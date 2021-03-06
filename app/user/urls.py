from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('createapple/', views.CreateAppleUserView.as_view(),
         name='createapple'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('appleme/', views.AppleUserApiView.as_view(), name='appleme'),
    path('validate/', views.ValidateApiView.as_view(), name='validate'),
]
