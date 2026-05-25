from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),

    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path(
        'dashboard/taken/<int:medicine_id>/<str:planned_time>/',
        views.mark_taken,
        name='mark_taken'
    ),
    path('pet/action/<str:action>/', views.pet_action, name='pet_action'),
    path('pet/new/', views.create_new_pet, name='create_new_pet'),

    path('medicines/', views.medicines_list, name='medicines'),
    path('medicines/create/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/edit/', views.medicine_update, name='medicine_update'),
    path('history/', views.intake_history, name='history'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('profile/', views.profile, name='profile'),
]
