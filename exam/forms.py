# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 20:27:37 2019

@author: Ullampuzha.Nizar
"""

from django import forms
from .models import ExamStudents

class LoginForm(forms.Form):
    sapid = forms.CharField(max_length=50)
    token = forms.CharField(widget= forms.PasswordInput())
    username =""
    message=""
    
    def clean_sapid(self):
        user_sapid = self.cleaned_data.get("sapid")
        user_token = self.cleaned_data.get("token")
        student = ExamStudents.objects.filter(sapid=user_sapid)        
        if not student:
            self.message =f"Username {user_sapid} not registerd for exam!"
            raise forms.ValidationError(f"Username {user_sapid} not registerd for exam!")
        self.username = student[0].name           
        self.sapid = user_sapid        
        return self.sapid