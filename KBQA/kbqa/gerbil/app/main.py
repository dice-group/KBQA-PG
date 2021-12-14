import requests
import pandas as pd
import json
import time

def main(query, lang="en"):
    return None

def startExperiment(system_name, system_url, datasets=["QALD9 Train Multilingual"], language="en"):
    url = 'http://gerbil-qa.aksw.org/gerbil/execute'
    experimentData = {"type":"QA","matching":"STRONG_ENTITY_MATCH","annotator":["{}({})".format(system_name, system_url)],"dataset":datasets,"answerFiles":[],"questionLanguage":language}
    param = {"experimentData":json.dumps(experimentData)}
    html = requests.get(url, params=param).content
    id = int(html)
    print(id)
    return id

def getTestResult(id):
    url = 'http://gerbil-qa.aksw.org/gerbil/experiment?id={}'.format(id)
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[0]
    print(df)
    macro_f1 = df.iloc[0]["Macro F1"]
    print(macro_f1)

    if macro_f1 == "The experiment is still running.":
        time.sleep(60)
        return getTestResult(id)
    else:
        df.to_csv('my data.csv')
        return df


id = startExperiment("NIFWS_KBQA-PG-AppA", "http://kbqa-pg.cs.upb.de/appA/")
getTestResult(id)
time.sleep(50)
getTestResult(id)