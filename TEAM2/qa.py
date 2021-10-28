from SPARQLWrapper import SPARQLWrapper, JSON
from pycorenlp import StanfordCoreNLP
import ssl
import json
from ctypes.test.test_pickling import name
ssl._create_default_https_context = ssl._create_unverified_context

text = (
  'What is the birthsday of Barack Obama?')
sparql_query='''
SELECT *
WHERE
{
  ?person  rdfs:label  ?label;
               dbp:office ?office.
 FILTER(?label="Obama Barack"@en || ?label="Barack Obama"@en)
}'''


def parse_nlp(text):
    output = json.loads(text)
    search = output['sentences'][0]['basicDependencies']
    nsubj = ""
    subj = ""
    for item in reversed(search):
        if item['dep']=='nsubj':
            nsubj=item['dependentGloss']
            subj=nsubj
        if item['dep']=='compound' and item['governorGloss']==nsubj:
            subj=item['dependentGloss']+' '+subj
    return subj    

def ask_coreNLP(question):
    nlp = StanfordCoreNLP('http://localhost:9000')
    output = nlp.annotate(text, 
    properties={
    'annotators': 'tokenize,ssplit,pos,depparse,parse',
    'outputFormat': 'json'
    })
    return output

def ask_DBpedia(name):
    sparql_query='''
        SELECT *
        WHERE
        {
          ?person  rdfs:label  ?label;
                       dbp:office ?office.
         FILTER(?label="'''+name+'''"@en)
        }'''
    answers = []
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    queryresult = sparql.query().convert()
    return queryresult

def parse_answer(db_answer):
    #output = json.loads(db_answer)
    answer = db_answer['results']['bindings'][0]['office']['value']
    return answer  
 

nlp = ask_coreNLP(text)
print(nlp)
#name = parse_nlp(nlp)
#print(name)
#answer = ask_DBpedia(name)
#db_answer = parse_answer(answer)
#print(answer)
#print(db_answer)


