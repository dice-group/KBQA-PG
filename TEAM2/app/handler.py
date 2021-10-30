from SPARQLWrapper import SPARQLWrapper, JSON

# handle incoming questions and format the answers
def process_question(question):

	# ------------------------------------------------
	# TODO add here the logic to process the question
	# and return the result from dbpedia
	# ------------------------------------------------

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


def ask_dbpedia(query):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    query_result = sparql.query().convert()

    return query_result


def parse_dbpedia_results(results):
	answers = list()

	variables = results['head']['vars']

	for result in results['results']['bindings']:
		for variable in variables:
			answer = result.get(variable)['value']
			answer = answer.split('/')[-1]

			answers.append(answer)

	return answers
