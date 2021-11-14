from django import template
from django.shortcuts import render
from .process_ques import process_question
# Create your views here.


#returns homepage when webserver is accessed
def base(request):
    return render(request, 'base.html' )



#returns answers to webpage when get_answers is requested
def get_answers(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = process_question(question)
        return render(request, 'base.html', {'question' : question, 'answers' : answer})
        