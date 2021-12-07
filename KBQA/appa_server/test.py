import requests

if __name__ == "__main__":
    query = "capital of China?"
    r = requests.post("http://127.0.0.1:24801/", data={"query": query})
    print(r)
    print(r.text)
