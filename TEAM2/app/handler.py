from SPARQLWrapper import SPARQLWrapper, JSON
from pycorenlp import StanfordCoreNLP
from app.query import generate_queries


# handle incoming questions and format the answers
def process_question(question):

	# ------------------------------------------------
	# TODO add here the logic to process the question
	# and return the result from dbpedia
	# ------------------------------------------------

	core_nlp_result = ask_core_nlp(question)
	ent, tok = parse_core_nlp_result(core_nlp_result)
	print('Entities:', ent)

	queries = generate_queries(ent, tok)

	dbpedia_results = list()

	for query in queries:
		print('Query:', query)
		result = ask_dbpedia(query)

		dbpedia_results.append(result)

	print('DBpedia results:', dbpedia_results)

	answers = parse_dbpedia_results(dbpedia_results)

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

def ask_core_nlp(question):
	nlp = StanfordCoreNLP('http://localhost:9000')

	output = nlp.annotate(question, properties={'annotators': 'ner', 'outputFormat': 'json'})

	return output

def parse_core_nlp_result(output):
	entities = list()

	for entity in output['sentences'][0]['entitymentions']:
		ent = entity['text'].replace(' ', '_')
		entities.append(ent)

	tokens = list()

	for token in output['sentences'][0]['tokens']:
		tokens.append(token)

	return entities, tokens


def ask_dbpedia(query):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    query_result = sparql.query().convert()

    return query_result


def parse_dbpedia_results(dbpedia_results):
	answers = list()

	for dbpedia_result in dbpedia_results:

		variables = dbpedia_result['head']['vars']

		for result in dbpedia_result['results']['bindings']:
			for variable in variables:
				answer = result.get(variable)['value']
				answer = answer.split('/')[-1]

				answers.append(answer)

	return answers
