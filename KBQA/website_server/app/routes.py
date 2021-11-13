from app import application
from flask import render_template, request
from app.handler import process_query


@application.route('/', methods=['GET'])
def index():
    """
    Home website.
    :return: HTML home website.
    """
    return render_template('question.html')


@application.route('/', methods=['POST'])
def query_fun():
    """
    Requesting an answer to some question.
    :return: HTML Website with answer.
    """
    query = request.form['query']
    chosen_app = request.form['App']
    answers = process_query(query, chosen_app)
    return render_template('question.html', query=query, answers=answers)


@application.errorhandler(500)
def internal_error(error):
    """
    If something happens internally, return an HTML with error 500.
    :param error: error object thrown by the actual exception.
    :return: HTML with error 500.
    """
    return render_template('500.html'), 500
