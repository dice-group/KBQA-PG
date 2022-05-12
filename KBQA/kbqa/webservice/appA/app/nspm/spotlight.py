from ast import Dict, Tuple
import spacy_dbpedia_spotlight


def find_entity(sentence: str) -> Dict[str, Tuple[str, str]]:
    """Find the entities in the sentence. 
    
    Find the entities in the sentence using dbpedia spotlight.

    Parameters
    ----------
    sentence : str
        Natural language question asked by an enduser.
    
    Returns
    -------
    entities : dict
        Dictionary with the placeholders as keys and the entities as values.
    """
    nlp = spacy_dbpedia_spotlight.create('en')
    doc = nlp(sentence)
    placeholder = 65
    entities = dict()
    for ent in doc.ents:
        entities[chr(placeholder)] = (ent.text, ent.kb_id_)
        placeholder += 1
    return entities


def replace_entities(sentence: str, entities: Dict[str, Tuple[str, str]]) -> str:
    """Replace the entities in the sentence.
    
    Replace the entities in the sentence with the placeholders.

    Parameters
    ----------
    sentence : str
        Natural language question asked by an enduser.
    entities : dict
        Dictionary with the placeholders as keys and the entities as values.
    
    Returns
    -------
    sentence : str
        Question with the placeholders replaced with the entities.
    """
    for placeholder, (entity, _) in entities.items():
        if entity in sentence:
            sentence = sentence.replace(entity, '<' + placeholder + '>')
    return sentence


def fix_start_end(sparql: str) -> str:
    """Fix the start and end of the query.
    
    Remove the "<start>" and "<end>" tokens in generated sparql query, 
    which appear sometime in the query.

    Parameters
    ----------
    sparql : str
        Generated sparql query from summarizer. 
    
    Returns
    -------
    sparql : str
        Query without "<start>" and "<end>" tokens.
    """
    sparql = sparql.replace('<start>', '')
    sparql = sparql.replace('<end>', '')
    return sparql


def restore_entity(sparql: str, entities: Dict[str, Tuple[str, str]]) -> str:
    """Restore the entities in the query.
    
    Replace the placeholders with the entities from question.

    Parameters
    ----------
    sparql : str
        Query with the placeholders. 
    entities : dict
        Dictionary with the placeholders as keys and the entities as values.
    
    Returns
    -------
    sparql : str
        Query with the placeholders replaced with the entities.
    """
    for placeholder, (_, uri) in entities.items():
        placeholder = ' ' + placeholder + '> '
        if  placeholder in sparql in sparql:
            sparql = sparql.replace(placeholder, ' <' + uri + '> ')
    return sparql
