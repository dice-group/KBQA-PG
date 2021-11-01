import spacy

from SPARQLWrapper import SPARQLWrapper, JSON
from app.query import generate_queries
from spacy.symbols import nsubj, VERB
from rdflib import URIRef


nlp = spacy.load("en_core_web_sm")


def resource_generator(resource_name):
    '''
    Convert the generated resource name into DBpedia equivalent key_word
    '''

    words = [word.lower() for word in resource_name.split()]
    key = ' '.join([word.capitalize() for word in words ])

    return key


def property_generator(property_name):
    '''
    Convert the generated property name into DBpedia equivalent property
    '''

    words = [word.lower() for word in property_name.split()]
    prop_names = []

    for word in words:
        if word != words[0]:
            word = word.capitalize()
        prop_names.append(word)
    
    prop = ''.join([word for word in prop_names ])

    return prop


def parse_nlp(text):
    '''
    Parse the question as NLP string and extract the name entity and property
    '''

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


def ask_DBpedia(subject, predicate):
    '''
    Send a simple SPARQL query to DBpedia containing the parameters as subject and predicate
    '''

    subject = subject.replace(' ', '_')
    sparql_query = 'SELECT ?o WHERE {{ dbr:{} dbp:{} ?o }}'.format(subject, predicate)

    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    queryresult = sparql.query().convert()

    return queryresult


def process_question(question):
    '''
    Handle an incoming question and format the answers
    '''

    recs_ent, prop_ent = parse_nlp(question)
    name = resource_generator(recs_ent)
    prop = property_generator(prop_ent)

<<<<<<< HEAD
# handle incoming questions and format the answers
def process_question(question):
        recs_ent , prop_ent = parse_nlp(question)

        name = resource_generator(recs_ent)
        prop = property_generator(prop_ent)

        dbpedia_ans = ask_DBpedia(name, prop)

        answers = parse_answer(dbpedia_ans, prop)

        

        return answers
=======
    dbpedia_ans = ask_DBpedia(name, prop)

    answers = parse_answer(dbpedia_ans, 'o')

    return answers

    # -------------------------- BEGIN EXAMPLE ---------------------------------------
    # example in order to check, whether the system works

    # example_question = 'Who is the chancellor of Germany?'
    # example_query = '''
    # 	SELECT ?name 
    # 	WHERE {
    # 		dbr:Germany dbp:leaderName ?name .
    # 		?name dbp:title dbr:Chancellor_of_Germany .
    # 	}
    # '''

    # if question == example_question:
    # 	dbpedia_result = ask_dbpedia(example_query)
    # else:
    # 	# case for unsupported question
    # 	dbpedia_result = ask_dbpedia('SELECT * WHERE { dbp:no dbp:answer dbp:expected }')

    # return dbpedia_result

    # -------------------------- END EXAMPLE ---------------------------------------------


def parse_answer(db_answer, prop_ans):
    '''
    Parse the result from DBpedia and extract the answer for the searched property
    '''

    answers = []
    answer = ''
    
    for i in range(len(db_answer['results']['bindings'])):
        if db_answer['results']['bindings'][i][prop_ans]['type'] == 'uri':
            resource = URIRef(db_answer['results']['bindings'][i][prop_ans]['value'])
            string_value = resource.split('/')[-1].replace('_',' ')
            answers.append(string_value)
        else:
            answers.append(db_answer['results']['bindings'][i][prop_ans]['value'])
    
    answer = ", ".join(str(x) for x in answers)

    return answer  
>>>>>>> 784324a66e5e2b5a7e871e70097f451bd44c22b2
