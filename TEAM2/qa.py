from SPARQLWrapper import SPARQLWrapper, JSON
from pycorenlp import StanfordCoreNLP
import ssl
import json
from ctypes.test.test_pickling import name

# fix Python SSL CERTIFICATE_VERIFY_FAILED during access to DBPedia
ssl._create_default_https_context = ssl._create_unverified_context

text = (
  'Who is Barack Obama?')

# parse NLP JSON in order to find a subject(nsubj) and all compounds of it
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
# sends request to NLP for the parameter "question", returns json with analysis and dependences in the question    
def ask_coreNLP(question):
    nlp = StanfordCoreNLP('http://localhost:9000')
    output = nlp.annotate(text, 
    properties={
    'annotators': 'tokenize,ssplit,pos,depparse,parse',
    'outputFormat': 'json'
    })
    return output
# sends request to DBPedia with a query for subject and property in the parameters, returns json with information about subject and his property
def ask_DBpedia(subject, property):
    sparql_query='''
        SELECT *
        WHERE
        {
          ?person   rdfs:label  ?label; 
           '''+'''dbp:'''+property+'''?'''+property+'''.'''+'''
                    
         FILTER(?label="'''+subject+'''"@en)
        }'''
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    queryresult = sparql.query().convert()
    return queryresult
# parse the json from DBPedia in order to find value of property
def parse_answer(db_answer):
    answer = db_answer['results']['bindings'][0]['office']['value']
    return answer  
 

nlp = ask_coreNLP(text)
#print(nlp)
name = parse_nlp(nlp)
property = 'office'
print(name)
answer = ask_DBpedia(name, property)
#print(answer)
db_answer = parse_answer(answer)
print(db_answer)


