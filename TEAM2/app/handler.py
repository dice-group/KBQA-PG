from SPARQLWrapper import SPARQLWrapper, JSON
#from pycorenlp import StanfordCoreNLP
from app.query import generate_queries
import spacy
from spacy.symbols import nsubj, VERB
from rdflib import URIRef #modified for parsing answer of type - uri
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

def parse_answer(db_answer, prop_ans):
    answer = db_answer['results']['bindings'][0][prop_ans]['value']
    return answer







# handle incoming questions and format the answers
def process_question(question):

	# ------------------------------------------------
	# TODO add here the logic to process the question
	# and return the result from dbpedia
	# ------------------------------------------------

	# core_nlp_result = ask_core_nlp(question)
	# ent, tok = parse_core_nlp_result(core_nlp_result)
	# print('Entities:', ent)


	recs_ent, prop_ent = parse_nlp(question)
	name = resource_generator(recs_ent)
	prop = property_generator(prop_ent)

	dbpedia_ans = ask_DBpedia(name, prop)

	answers = parse_answer(dbpedia_ans, prop)

	

	return answers

	# -------------------------- BEGIN EXAMPLE ---------------------------------------
	# example in order to check, whether the system works

	example_question = 'Who is the chancellor of Germany?'
	example_query = '''
		SELECT ?name 
		WHERE {
			dbr:Germany dbp:leaderName ?name .
			?name dbp:title dbr:Chancellor_of_Germany .
		}
	'''

	if question == example_question:
		dbpedia_result = ask_dbpedia(example_query)
	else:
		# case for unsupported question
		dbpedia_result = ask_dbpedia('SELECT * WHERE { dbp:no dbp:answer dbp:expected }')

	return dbpedia_result

	# -------------------------- END EXAMPLE ---------------------------------------------

# 





# def parse_dbpedia_results(dbpedia_results):
# 	answers = list()

# 	for dbpedia_result in dbpedia_results:

# 		variables = dbpedia_result['head']['vars']

# 		for result in dbpedia_result['results']['bindings']:
# 			for variable in variables:
# 				answer = result.get(variable)['value']
# 				answer = answer.split('/')[-1]

# 				answers.append(answer)

# 	return answers


# sends request to DBPedia with a query for subject and property in the parameters, returns json with information about subject and his property


def parse_answer(db_answer, prop_ans):
    answers =[]
    answer = ''
    # print((db_answer['results']['bindings']))
    for i in range(len(db_answer['results']['bindings'])):
        if db_answer['results']['bindings'][i][prop_ans]['type'] == 'uri':
            resource = URIRef(db_answer['results']['bindings'][i][prop_ans]['value'])
            string_value = resource.split('/')[-1].replace('_',' ')
            answers.append(string_value)
        else:
            answers.append(db_answer['results']['bindings'][i][prop_ans]['value'])
    # answer = db_answer['results']['bindings'][0][prop_ans]['value']
    answer = ",".join(str(x) for x in answers)
    return answer  
 
# recs_ent, prop_ent = parse_nlp(text)
# name = resource_generator(recs_ent)
# prop = property_generator(prop_ent)


# answer = ask_DBpedia(name, prop)
# db_answer = parse_answer(answer, prop)
# print(db_answer)