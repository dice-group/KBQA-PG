from app.api import application
from app.main import main

if __name__ == "__main__":
    main()

    application.run(port=24804)
