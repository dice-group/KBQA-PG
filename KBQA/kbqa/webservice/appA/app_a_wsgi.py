"""Start the service for approach A, when this module is called."""
import ssl
from app.api import application

ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == "__main__":
    
    application.run(port=24801)
