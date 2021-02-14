from . import views
from django.urls import path

urlpatterns = [
    path('',views.home,name='home'),
    path('mask/',views.mask,name='mask'),
    path('rec_foods/',views.rec_foods,name='rec_foods'),
    path('rec_books/',views.rec_books,name='rec_books'),
    path('send_news/',views.send_news,name='send_news'),
    path('startCall/',views.startCall,name='startCall'),
    path('search/', views.index, name="search"),
    path('results', views.show_results, name="results")   
]