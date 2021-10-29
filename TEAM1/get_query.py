import stanza

class QA_query_generation:
    def __init__(self):
        self._processors = 'tokenize,pos,lemma,depparse'
        stanza.download('en', processors=self._processors)
        self._nlp = stanza.Pipeline('en', processors=self._processors)


    def get_query_v1(self, nl_question):
        doc = self._nlp(nl_question)

        dbpedia_resource_base = 'https://dbpedia.org/resource/'
        dbpedia_ontology_base = 'https://dbpedia.org/ontology/'

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
        query = f'SELECT ?s WHERE {{?s {dbpedia_ontology_base + pred} {dbpedia_resource_base + obj} }}'
        print(f'Query: {query}')
        yield query

if __name__ == '__main__':
    qa = QA_query_generation()


    question = 'What is the meaning of Life?'
    for query in qa.get_query_v1(question):
        print(query)

