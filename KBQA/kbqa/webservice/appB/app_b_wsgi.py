"""Start the service for approach B, when this module is called."""
from app.api import application


if __name__ == "__main__":
    application.run(port=24802)
