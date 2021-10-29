import stanza
import json
import itertools

class QA_query_generation:
    def __init__(self):
        self._processors = 'tokenize,pos,lemma,depparse'
        stanza.download('en', processors=self._processors)
        self._nlp = stanza.Pipeline('en', processors=self._processors)
        self._dbpedia_resource_base = 'https://dbpedia.org/resource/'
        self._dbpedia_ontology_base = 'https://dbpedia.org/ontology/'

    def get_query_v1(self, nl_question):
        
        doc = self._nlp(nl_question)
        for sentence in doc.sentences:
            print(f'Question decomposition of question: {nl_question}')
            pred = ''
            obj = ''
            for word in sentence.words:
                print(f'{word.text}: {word.lemma}, {word.pos}, {word.head}, {word.deprel}')
                if(word.deprel == 'nsubj'):
                    pred = word.text
                elif word.deprel == 'obj' or word.deprel == 'nmod':
                    obj = word.text

        print(f'Query for question: {nl_question}')
        query = f'SELECT ?s WHERE {{?s {self._dbpedia_ontology_base + pred} {self._dbpedia_resource_base + obj} }}'
        print(f'Query: {query}')
        yield query

    def get_query_v2(self, nl_question):
        
        doc = self._nlp(nl_question)
        #Consider only first sentence
        sentence = doc.sentences[0] 
        considered_POS_tags = ['ADJ', 'ADV', 'AUX', 'CCONJ', 'NOUN', 'PRON', 'PROPN', 'VERB']

        #Extract only words that have a considered POS tag
        considered_words = [word for word in sentence.words if word.pos in considered_POS_tags]
        #Remove duplicates
        considered_words = list(set(considered_words))
        print(', '.join([w.lemma for w in considered_words]))

        #Iterate through all 2 combinations
        for word_permutations in itertools.permutations(considered_words, 2):
            print(f'{word_permutations[0].lemma:15} | {word_permutations[1].lemma}')
            word0 = word_permutations[0].lemma
            word1 = word_permutations[1].lemma
            query_string = 'SELECT {} WHERE {{ {} {} {} }}'
            subj_query = query_string.format('?s', '?s', self._dbpedia_ontology_base + word0, self._dbpedia_resource_base + word1)
            yield subj_query
            obj_query = query_string.format('?o', self._dbpedia_ontology_base + word0, self._dbpedia_resource_base + word1, '?o')
            yield obj_query

if __name__ == '__main__':
    qa = QA_query_generation()

    with open('Data/qald-9-train-multilingual.json') as json_file:
        data = json.load(json_file)

    dataset_questions = []
    en_lang_index = 3
    for q in data['questions']:
        print(q['question'][en_lang_index]['string'])
        print(q['query']['sparql'])
        dataset_questions.append(q['question'][en_lang_index]['string'])

    for question in dataset_questions[:10]:
        print(question)
        for query in qa.get_query_v2(question):
            print(query)

