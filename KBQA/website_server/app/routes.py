from app import application
from flask import render_template, request, redirect, url_for
from app.handler import process_question


@application.route('/', methods=['GET'])
def index():
    return render_template('question.html')


@application.route('/WEB', methods=['POST'])
def question():
    asked_question = request.form['query']
    chosen_app = request.form['App']
    print('Question', asked_question)

    answers = process_question(asked_question, chosen_app)
    print('Answers', answers)

    return render_template('question.html', query=asked_question, answers=answers)


@application.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
