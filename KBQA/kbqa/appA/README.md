# Approach A

This is the implementation of approach A. (TODO give some information for approach A)

## Local Tests

In order to test the functionality of the application for approach A, a local script can be executed to simulate the behaviour of the application.

First **argparse** has to be installed:

```bash
pip install argparse
```

Then, the development server can be started:

```bash
python appA_wsgi.py
```

In another terminal the script **local_test.py** can be executed:

```bash
python local_test.py <question>
```

<question> is a string, which contains a natural language question, which might be asked by an enduser and is forwarded to the application by the webserver. After processing this question, the result of the application is printed and can be checked/evaluated.