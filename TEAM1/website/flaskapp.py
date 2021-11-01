from flask import Flask, request, render_template
from get_query import QA_query_generation
from get_answer import get_answer


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
        
        if answer:        
            return answer


if __name__ == "__main__":
    app.run()
