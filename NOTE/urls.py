from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dash/', views.dashboard, name='dash'),
    path('add/', views.add_book, name='add'),
    path('success/', views.success, name='success'),
    path('bborrow/', views.borrow_book, name='bborrow'),
    path('count/', views.count, name='count'),
    path('uf/', views.uf, name='uf'),
    path('borrow-book/', views.borrow_book, name='borrow_book'),
    path('acr/', views.acr, name='acr'),
    path('bret/', views.bret, name='bret'),
    path('confirm-return/<int:borrowed_book_id>/', views.confirm_return, name='confirm_return'),
]