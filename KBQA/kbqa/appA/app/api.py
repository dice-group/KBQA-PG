from flask import render_template, request
from app import application
from app.main import main


@application.route('/appA/', methods=['GET', 'POST'])
def endpoint():
    
    if request.method == 'POST':
        query = request.form['query']

        # check, whether the language parameter is set
        if 'lang' in request.form.keys():
            lang = request.form['lang']

            answer = main(query, lang)
        else:
            answer = main(query)

        return answer

    return '<h1>This is the endpoint of approach A. There is nothing to see here</h1>'