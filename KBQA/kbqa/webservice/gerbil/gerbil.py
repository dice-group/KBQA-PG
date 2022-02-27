"""Start the gerbil service, when this module is called."""
from app.api import application
from app.main import startup


if __name__ == "__main__":
    startup("dice")  # set gerbil system
    application.run(port=24804)
