# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 15:04:05 2019

@author: Ullampuzha.Nizar
"""

from django.urls import path
from . import views

app_name = 'exam'
urlpatterns = [
    # ex: /exams/    
    path('',views.login,name='login'),
    path('start/',views.start,name='start'),
    path('login/',views.dologin, name='dologin'),
    path('question/<int:sequence>/', views.askquestion, name='question'),
    path('<int:studentid>/result/', views.showresult, name='result'),
    path('<int:examquestions_id>/answer/', views.setanswer, name='answer'),
]
