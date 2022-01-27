"""Start the service, when this module is called."""
from app.routes import application


if __name__ == "__main__":
    application.run(debug=False, port=24803)
