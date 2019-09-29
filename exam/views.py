from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import connection
import random

from .models import ExamQuestions,ExamOptions,ExamStudents,ExamTempAssess,ExamAssessments
from .forms import LoginForm

QUESTION_COUNT = 5;

def login(request):
    message = "" #No error message for inital display
    print(message)
    return render(request,'exam/login.html',{'message':message})

def dologin(request):
    message = "not logged in"
    if request.method == "POST":
        ExamLoginForm = LoginForm(request.POST) 
        
        if ExamLoginForm.is_valid():            
            #username = ExamLoginForm.username            
            request.session['sapid']=ExamLoginForm.sapid
            student = ExamStudents.objects.filter(sapid=ExamLoginForm.sapid)[0]
            score=getscore(student.id)
            #call start.html show previous exam information
            return render(request,'exam/start.html',{'student':student,
                                                     'score':score,
                                                     'QUESTION_COUNT':QUESTION_COUNT,
                                                     })                        
        else:
            message = f"{ExamLoginForm.message}. Please try again"           
    
    return render(request,'exam/login.html',{'message':message})    

def getscore(studentid):
    # Check the count of correct options from previous test 
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) score FROM  exam_assessments EA, exam_options EO\
                   WHERE EA.students_id = %s \
                   AND EA.options_id = EO.id\
                   and EO.answer = True",[studentid])
    score = cursor.fetchone()[0]
    print(score)
    return score
#display startpage with user details
def start(request):
    if request.session.has_key('sapid'):
        stsapid = request.session['sapid']   
    else:
        message = "You are not logged in. Please log in."
        return render(request,'exam/login.html',{'message':message})
    
    setexam(stsapid)
    
    #to check in askquestion to avoid calling directly from browser URL. 
    request.session['redirected'] = "start"
    return HttpResponseRedirect(reverse('exam:question', args = (1,)))
    
    
def logout(request):
    try:
        if request.session.has_key('sapid'):
            del request.session['sapid']
        if request.session['redirected']:
            del request.session['redirected']
    except:
        pass
    

def setexam(stsapid):
    questlist = ([EQ.id for EQ in ExamQuestions.objects.all()])
    questset = random.sample(questlist,QUESTION_COUNT)
    
    studentid = ExamStudents.objects.filter(sapid=stsapid)[0].id
    #delete previous entries if any
    ExamTempAssess.objects.filter(students_id = studentid).delete()
    i=0
    for quest in questset:
        i+=1
        temp = ExamTempAssess(students_id = studentid, questions_id = quest,
                              sequence_no=i) 
        temp.save()

def askquestion(request, sequence):
    #request.method is POST when called from question.html
    # redirected is available when redirected from start(), setanswer()
    if request.session.has_key('sapid') and (request.method=='POST' or
                                 request.session['redirected']=='start' or
                                 request.session['redirected']=='setanswer'):
        stsapid = request.session['sapid']   
        #del request.session['redirected'] #required only for redirection
    else:
        message = "You are not logged in. Please log in."
        return render(request,'exam/login.html',{'message':message})
    
    studentid = ExamStudents.objects.filter(sapid=stsapid)[0].id
    studentname = ExamStudents.objects.filter(sapid=stsapid)[0].name
    TempAsses = ExamTempAssess.objects.filter(students_id = studentid,sequence_no=sequence)[0]
    question = ExamQuestions.objects.get(id=TempAsses.questions_id)
    return render(request,'exam/question.html',{'examquestions':question,
                                                'sequence':sequence,
                                                'studentdetails':f"{studentname} ({stsapid})"})

def showresult(request, studentid):
    # check if redirected from setanswer() to avoid direct call from browser URL
    if request.session.has_key('redirected') and request.session['redirected'] =='setanswer':
        assessment = ExamAssessments.objects.filter(students=studentid)
        student = ExamStudents.objects.get(pk=studentid) 
        #logout from session    
        logout(request)
        return render(request,'exam/result.html',{'examassessment':assessment,'student':student})    
    else:
        message = "You are not logged in. Please log in."
        return render(request,'exam/login.html',{'message':message})
    
def setanswer(request,examquestions_id):     
    #Check if URL is wrongly entered    
    if request.method == 'GET' or not (request.session.has_key('sapid')):
        message = "You are not logged in. Please log in."
        return render(request,'exam/login.html',{'message':message})
    stsapid = request.session['sapid']
    question = get_object_or_404(ExamQuestions, pk=examquestions_id)     
    sequence = int(request.POST['sequence'])
    try:
        selected_option = question.examoptions_set.get(pk=request.POST['option'])        
    except (KeyError, ExamOptions.DoesNotExist):
        studentname = ExamStudents.objects.filter(sapid=stsapid)[0].name
        # Redisplay the question voting form.
        return render(request, 'exam/question.html',{
                'examquestions': question,
                'sequence':sequence,
                'error_message' : "You didn't select an option.",
                'studentdetails':f"{studentname} ({stsapid})"})
    else:
        #Save selected option in ExamTempAssess
        studentid = ExamStudents.objects.filter(sapid=stsapid)[0].id
        TempAsses = ExamTempAssess.objects.filter(students_id = studentid,sequence_no=sequence)[0]
        TempAsses.options_id = selected_option.id
        TempAsses.save()
        
         #to check in askquestion/showresult to avoid calling directly from browser URL. 
        request.session['redirected'] = "setanswer"
        if sequence == QUESTION_COUNT:
            #Remove previous assessment results
            ExamAssessments.objects.filter(students=studentid).delete()
            
            assessments = ExamTempAssess.objects.filter(students_id = studentid)
            #copy current assessment results
            for assessment in assessments:
                assess = ExamAssessments(students = ExamStudents.objects.get(pk=assessment.students_id),
                                         questions = ExamQuestions.objects.get(pk=assessment.questions_id),
                                         options = ExamOptions.objects.get(pk=assessment.options_id))
                assess.save()
            #cleanup ExamTempAssess table for current student.
            assessments.delete()
            ExamStudents.objects.filter(id=studentid).update(exam_count=1)
            #show assessment summary
            return HttpResponseRedirect(reverse('exam:result', args = (studentid,)))
            
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.        
        return HttpResponseRedirect(reverse('exam:question', args = (sequence+1,)))
        
