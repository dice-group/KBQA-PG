import spacy_dbpedia_spotlight


def find_entity(sentence):
    nlp = spacy_dbpedia_spotlight.create('en')
    doc = nlp(sentence)
    placeholder = 65
    entities = dict()
    for ent in doc.ents:
        entities[chr(placeholder)] = (ent.text, ent.kb_id_)
        placeholder += 1
    return entities


def replace_entities(sentence, entities):
    for placeholder, (entity, _) in entities.items():
        if entity in sentence:
            sentence = sentence.replace(entity, '<' + placeholder + '>')
    return sentence


def fix_start_end(sparql):
    sparql = sparql.replace('<start>', '')
    sparql = sparql.replace('<end>', '')
    return sparql


def restore_entity(sparql, entities):
    for placeholder, (_, uri) in entities.items():
        placeholder = ' ' + placeholder + '> '
        if  placeholder in sparql in sparql:
            sparql = sparql.replace(placeholder, ' <' + uri + '> ')
    return sparql
