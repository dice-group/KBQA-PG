"""
Run the flask server when this .py is called as __main__.
"""

from app.routes import application


if __name__ == "__main__":
    application.run(debug=False, port=24803)
