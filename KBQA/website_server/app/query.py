
resources = {
	'born' : 'birthDate',
	'birthday' : 'birthDate',
	'capital' : 'capital',
	'developed' : 'developer',
	'located' : 'location',
	'mayor' : 'leaderName',
	'die' : 'deathDate',
}

def generate_queries(entities, tokens):
	queries = list()

	for entity in entities:
		for token in tokens:
			if token['word'] in resources.keys():
				key = token['word']

				subject_query = subject_query_template(entity, resources[key])
				queries.append(subject_query)

				#object_query = object_query_template(resources[key], entity)
				#queries.append(object_query)

	return queries

def subject_query_template(subject, predicate):
	return 'SELECT ?o WHERE {{ dbr:{} dbp:{} ?o }}'.format(subject, predicate)

def object_query_template(predicate, obj):
	return 'SELECT ?s WHERE {{ ?s dbp:{} dbr:{} }}'.format(predicate, obj)
