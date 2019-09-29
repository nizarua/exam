from django.contrib import admin

from .models import ExamQuestions,ExamOptions,ExamStudents

admin.site.register(ExamQuestions)
admin.site.register(ExamOptions)
admin.site.register(ExamStudents)


# Register your models here.
