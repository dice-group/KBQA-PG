from app import application
from flask import render_template, request
from app.handler import process_question


@application.route('/', methods=['GET'])
def index():
    return render_template('question.html')


@application.route('/', methods=['POST'])
def query_fun():
    query = request.form['query']
    chosen_app = request.form['App']
    answers = process_question(query, chosen_app)
    return render_template('question.html', query=query, answers=answers)


@application.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
