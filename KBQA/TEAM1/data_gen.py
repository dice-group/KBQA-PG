import json
import re


def tokenize_query(query):
    tokens = query.split(' ')
    tokens = [x for x in tokens if x != '' and x != ' ']
    
    triple_tokens = []
    union_tokens = []
    constraint_tokens = []

    open_brackets = 0
    for token in tokens:
        if open_brackets == 0:
            if token == '{':
                open_brackets += 1
                triple_tokens.append(token)
            else:
                constraint_tokens.append(token)
        elif open_brackets == 1:
            if token == '{':
                open_brackets += 1
                union_tokens.append(token)
            elif token == '}':
                open_brackets -= 1
                triple_tokens.append(token)
            elif token == 'UNION':
                pass
            else:
                triple_tokens.append(token)
        else:
            if token == '}':
                open_brackets -= 1
                union_tokens.append(token)
            else:
                union_tokens.append(token)
    return triple_tokens, union_tokens, constraint_tokens

def construct_triples(triple_tokens):
    triples = []
    leading_token = None
    for token in triple_tokens:
        if token == '{' or token == '}':
            pass
        elif leading_token == None:
            leading_token = token
            triples.append(leading_token)
        elif token == ';':
            triples.append(leading_token)
        elif token == '.':
            leading_token = None
        else:
            triples[-1] = triples[-1] + ' ' + token
    return triples

def construct_unions(union_tokens):
    unions = []
    curr_union = []
    for token in union_tokens:
        curr_union.append(token)
        if token == '}':
            unions.append(construct_triples(curr_union))
            curr_union = []
    return unions

datafile = 'Data/qald-9-train-multilingual.json'
with open(datafile,'r') as f:
    data = json.load(f)
#print(data)

questions = data['questions']

qta_list = []
for q in questions:
    question = ''
    for qq in q["question"]:
        if qq['language'] == 'en':
            question = qq['string']
            break
    if 'SELECT' in q['query']['sparql'] and \
    not 'SELECT COUNT' in  q['query']['sparql'] and \
    not 'SELECT (COUNT' in  q['query']['sparql']:
        query = re.sub('(.*) WHERE','',q['query']['sparql'])
        search_token = re.sub('(.*)SELECT (DISTINCT )?','',q['query']['sparql'])
        search_token = search_token.split(' ')[0]
        triple_tokens, union_tokens, constraint_tokens = tokenize_query(query)
        triple_templates = construct_triples(triple_tokens)
        unions = construct_unions(union_tokens)
        constraints = ' '.join(constraint_tokens)

        #print(q['answers'][0])
        if q['answers'][0]['head']:
            answer_type = q['answers'][0]['head']['vars'][0]
            answers = [x[answer_type]['value'] for x in q['answers'][0]['results']['bindings']]
        else:
            answers = [q['answers'][0]['boolean']]

        
        triples = []
        for answer in answers:
            for triple in triple_templates:
                triple = triple.replace(search_token, answer)
                if '?' in triple:
                    print(search_token, triple)
                else:
                    triples.append(triple)

        qta_list.append({'question':question, 'triples':triples, 'answers':answers})
        


        #print(f'search token: {search_token}')
        #print(f'triple tokens: {triple_tokens}')
        #print(f'union tokens: {union_tokens}')
        #print(f'constraint tokens: {constraint_tokens}')
        #print(f'Question: {question}')
        #print(f"Query: {q['query']['sparql']}")
        #print(f'Triples: {triple_templates}')
        #print(f'Unions: {unions}')
        #print(f'Constraints: {constraints}')
        #print('\n\n')

        #print(f'Split Query: {split_query}')
        #for a in answers:
        #    print(f'Answer: {a}')
qta_dict = {'qtas':qta_list}
#print(qta_dict)
json_dump = json.dumps(qta_dict)

#print(json_dump)
