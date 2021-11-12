# Knowledge Base Question Answering

Webservice for answering simple questions

# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) in order to install all needed dependencies:

```bash
pip install -r requirements.txt
```

In addition to the python libraries you have to install **en_core_web_sm**. Simply run the following command:

```bash
python -m spacy download en_core_web_sm
```

# Start the WebService

Depending on which system you are using, you first have to set the **FLASK_APP** variable:

(Linux, Mac)
```bash
$ export FLASK_APP=kbqa
$ python kbqa.py
```

Windows CMD:
```bash
> set FLASK_APP=kbqa
> python kbqa.py
```

Windows Powershell:
```bash
> $env:FLASK_APP="kbqa"
> python kbqa.py
```


# Open the Website

After starting the Webservice and the Stanford CoreNLP you can visit the website **http://127.0.0.1:5000/** or **http://localhost:5000/** in order to ask questions.
