import stanza
import json
processors = 'tokenize,pos,lemma,depparse'
stanza.download('en', processors=processors)
nlp = stanza.Pipeline('en', processors=processors)


questions = ['Who is the chancellor of Germany?',
             'What is the meaning of Life?',
             'Who won the world cup?',
             'When was the first world war']


### Queries: SELECT ?s WHERE {?s chancellor Germany}
### Queries: SELCET ?s WHERE {?s meaning Life}
### Queries: SELECT ?s WHERE {?s won world-cup}

queries = []

dbpedia_resource_base = 'https://dbpedia.org/resource/'
dbpedia_ontology_base = 'https://dbpedia.org/ontology/'

with open('Data/qald-9-train-multilingual.json') as json_file:
    data = json.load(json_file)

dataset_questions = []

en_lang_index = 3

for q in data['questions']:
    print(q['question'][en_lang_index]['string'])
    print(q['query']['sparql'])
    dataset_questions.append(q['question'][en_lang_index]['string'])

for q in dataset_questions[:10]:
    doc = nlp(q)
    for sentence in doc.sentences:
        print(f'Question decomposition of question: {q}')
        pred = ''
        obj = ''
        for word in sentence.words:
            print(f'{word.text}: {word.lemma}, {word.pos}, {word.head}, {word.deprel}')
            if(word.deprel == 'nsubj'):
                pred = word.text
            elif word.deprel == 'obj' or word.deprel == 'nmod':
                obj = word.text

        print(f'Query for question: {q}')
        query = f'SELECT ?s WHERE {{?s {dbpedia_ontology_base + pred} {dbpedia_resource_base + obj} }}'
        print(f'Query: {query}')
        queries.append(query)
        print('------------------------------------------------------------------------------------------------------------\n')

