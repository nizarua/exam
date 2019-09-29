from django.db import models

# Create your models here.
class ExamAssessments(models.Model):
    students = models.ForeignKey('ExamStudents', models.DO_NOTHING)
    questions = models.ForeignKey('ExamQuestions', models.DO_NOTHING)
    options = models.ForeignKey('ExamOptions', models.DO_NOTHING, blank=True, null=True)
    

    class Meta:
        managed = False
        db_table = 'exam_assessments'


class ExamOptions(models.Model):
    option = models.CharField(max_length=200)
    answer = models.BooleanField()
    questions = models.ForeignKey('ExamQuestions', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'exam_options'


class ExamQuestions(models.Model):
    question = models.CharField(max_length=200)
    type = models.CharField(max_length=1)
    
    def __str__(self):
        return self.question

    class Meta:
        managed = False
        db_table = 'exam_questions'


class ExamStudents(models.Model):
    name = models.CharField(max_length=50)
    sapid = models.IntegerField(db_column='SAPID')  # Field name made lowercase.
    login_token = models.CharField(max_length=10, blank=True, null=True)
    exam_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exam_students'

class ExamTempAssess(models.Model):
    ''' For temporarily saving questions and options for each student druing
    the exam. Delete the old entries at successful login and logout'''
    students_id = models.IntegerField(blank=True, null=True)
    questions_id = models.IntegerField(blank=True, null=True)
    options_id = models.IntegerField(blank=True, null=True)
    sequence_no = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exam_temp_assess'
