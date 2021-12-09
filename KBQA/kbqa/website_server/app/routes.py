from app import application
from flask import render_template, request, jsonify
from app.handler import process_question


@application.route('/', methods=['GET'])
def index():
    """
    Home website.
    :return: HTML home website.
    """
    return render_template('index.html')


@application.route('/', methods=['POST'])
def query_fun():
    """
    Requesting an answer to some question.
    :return: HTML Website with answer.
    """

    question = request.form['question']
    chosen_app = request.form['approach']
    answers, query = process_question(question, chosen_app)
    
    #return render_template('index.html', query=query, answers=answers)
    return jsonify({ 'question' : question, 'answers' : answers, 'query' : query})


@application.errorhandler(500)
def internal_error(error):
    """
    If something happens internally, return an HTML with error 500.
    :param error: error object thrown by the actual exception.
    :return: HTML with error 500.
    """
    return render_template('500.html'), 500
