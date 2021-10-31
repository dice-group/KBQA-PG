import stanza
import json
import itertools


class QA_query_generation:
    def __init__(self):
        self._processors = 'tokenize,mwt,pos,lemma,depparse'
        stanza.download('en', processors=self._processors)
        self._nlp = stanza.Pipeline('en', processors=self._processors)
        self._dbpedia_resource_base = 'http://dbpedia.org/resource/'
        self._dbpedia_ontology_base = 'http://dbpedia.org/ontology/'

    def get_query(self, nl_question):
        print(f'Question decomposition of question: {nl_question}')
        print("\n")

        doc = self._nlp(nl_question)
        # Consider only first sentence because we should only have one question.
        sentence = doc.sentences[0]

        # Just some sentence informations.
        print("doc of question:")
        print(f'word\tlemma\tpos\thead_id\thead\tdeprel')
        for word in sentence.words:
            print(f'{word.text}\t{word.lemma}\t{word.pos}\t{word.head}\t' +
                  f'{sentence.words[word.head - 1].text if word.head > 0 else "root"}\t{word.deprel}')
        print("\n")

        # Extract reasonable tokens only.
        considered_POS_tags = ['NOUN', 'PROPN', 'VERB']
        # Extract only words that have a considered POS tag
        considered_words = [word for word in sentence.words if word.pos in considered_POS_tags]
        # Remove duplicates
        considered_words = list(set(considered_words))
        # Convert to lemmas list
        considered_word_lemmas = []
        for word in considered_words:
            considered_word_lemmas.append(word.lemma)
        # Concat MWEs (Multi Word Expressions)
        for word in considered_words:
            if word.deprel in ['flat', 'fixed', 'compound']:
                is_leading_word = False
                concatenated_word = word.lemma
                current_word = word
                while is_leading_word is False:
                    current_word = sentence.words[current_word.head-1]
                    concatenated_word = current_word.lemma + "_" + concatenated_word
                    if current_word.deprel not in ['flat', 'fixed', 'compound']:
                        is_leading_word = True
                considered_word_lemmas.append(concatenated_word)

        print("The considered words are:")
        print(', '.join([w for w in considered_word_lemmas]))
        print("\n")

        # Iterate through all 2 combinations
        for word_permutations in itertools.permutations(considered_word_lemmas, 2):
            word0 = word_permutations[0]
            word1 = word_permutations[1]
            query_string = 'SELECT {} WHERE {{ {} {} {} }}'
            subj_query = query_string.format('?s', '?s', '<' + self._dbpedia_resource_base + word0 + '>',
                                             '<' + self._dbpedia_ontology_base + word1 + '>')
            yield subj_query
            obj_query = query_string.format('?o', '<' + self._dbpedia_resource_base + word0 + '>',
                                            '<' + self._dbpedia_ontology_base + word1 + '>', '?o')
            yield obj_query


if __name__ == '__main__':
    qa = QA_query_generation()

    # Example 1.
    # Examples from the data set.
    # with open('Data/qald-9-train-multilingual.json') as json_file:
    #     data = json.load(json_file)
    #
    # dataset_questions = []
    # en_lang_index = 3
    # for q in data['questions']:
    #     print("\n")
    #     print(q['question'][en_lang_index]['string'])
    #     print(q['query']['sparql'])
    #     dataset_questions.append(q['question'][en_lang_index]['string'])
    #
    # for question in dataset_questions[:10]:
    #     print("\n")
    #     print(question)
    #     for query in qa.get_query(question):
    #         print(query)
    #         print("\n")

    # Example 2.
    # Some working query.
    # for query in qa.get_query("What is the anthem of Germany?"):
    #     print(query)


