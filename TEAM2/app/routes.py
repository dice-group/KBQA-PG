from app import application
from flask import render_template, request, redirect, url_for
from app.handler import process_question

<<<<<<< HEAD
#@application.route('/')
# @application.route('/index')
# def index():	
# 	return render_template('index.html')
=======
@application.route('/')
@application.route('/index')
def index():
    return render_template('index.html')
>>>>>>> 784324a66e5e2b5a7e871e70097f451bd44c22b2

@application.route('/', methods=['GET', 'POST'])
def question():

    if request.method == 'POST':
        question = request.form['question']
        print('Question', question)

        answers = process_question(question)
        print('Answers', answers)

        return render_template('question.html', question=question, answers=answers)
    
    return render_template('question.html')
