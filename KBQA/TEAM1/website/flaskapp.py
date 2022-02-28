from flask import Flask
from flask import render_template
from flask import request
from get_answer import get_answer
from get_query import QA_query_generation


app = Flask(__name__)
app.debug = True


@app.route("/")
def startpage():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def enter_question():
    question = request.form["question"]

    query_generator = QA_query_generation()

    for query in query_generator.get_query(question):
        print("trying query: " + query)
        answer = get_answer(query)

        print(answer)

        if answer["results"]["bindings"] != []:
            return answer
    return "No answer found"


if __name__ == "__main__":
    app.run()
