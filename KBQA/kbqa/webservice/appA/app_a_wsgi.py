"""Start the service for approach A, when this module is called."""
from app.api import application


if __name__ == "__main__":
    application.run(port=24801)
