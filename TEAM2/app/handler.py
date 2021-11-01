from SPARQLWrapper import SPARQLWrapper, JSON
from app.query import generate_queries
import spacy
from spacy.symbols import nsubj, VERB
nlp = spacy.load("en_core_web_sm")

#converts geberated resouce name into db-pedia equivalent key_word
def resource_generator(resource_name):
    words = [word.lower() for word in resource_name.split()]
    key = ' '.join([word.capitalize() for word in words ])
    return key


#converts geberated property name into db-pedia equivalent property_word
def property_generator(property_name):
    words = [word.lower() for word in property_name.split()]
    prop_names = []
    for word in words:
        if word != words[0]:
            word = word.capitalize()
        prop_names.append(word)
    prop = ''.join([word for word in prop_names ])
    return prop


#parse the question as nlp string and exteact name entity and property to be answered
def parse_nlp(text):
    doc = nlp(text)
    recs_ent = doc.ents[0].text


    prop_ents = []
    for chunk in doc.noun_chunks:
        if str(chunk) == recs_ent:
            continue
        prop_ents.append( " ".join(str(word)  for word in chunk if not word.is_stop))
    prop_ents = [prop for prop in prop_ents if prop]
   
    prop_ent = prop_ents[0]

    return recs_ent, prop_ent


#ask questions to dbpedia using sparql
def ask_DBpedia(subject, property):
    sparql_query='''
        SELECT *
        WHERE
        {
          ?person   rdfs:label  ?label; 
           '''+'''dbo:'''+property+'''?'''+property+'''.'''+'''
                    
         FILTER(?label="'''+subject+'''"@en)
        }'''
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    queryresult = sparql.query().convert()
    return queryresult



#parse the response of dbpedia response
def parse_answer(db_answer, prop_ans):
    answer = db_answer['results']['bindings'][0][prop_ans]['value']
    return answer







# handle incoming questions and format the answers
def process_question(question):
        recs_ent , prop_ent = parse_nlp(question)

        name = resource_generator(recs_ent)
        prop = property_generator(prop_ent)

        dbpedia_ans = ask_DBpedia(name, prop)

        answers = parse_answer(dbpedia_ans, prop)

        

        return answers