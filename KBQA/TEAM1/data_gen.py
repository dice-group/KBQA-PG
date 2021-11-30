import json
import re
from get_answer import get_answer, get_ask_result

def join_incomplete_tokens(tokens):
    resulting_tokens = []
    is_token_incomplete = False
    incomplete_token = []
    for token in tokens:
        if token.count('"') == 1:
            is_token_incomplete = not is_token_incomplete
        
        if is_token_incomplete:
            if incomplete_token:
                incomplete_token.append(token)
            else:
                incomplete_token = [token]
        else:
            if incomplete_token:
                incomplete_token.append(token)
                token = ' '.join(incomplete_token)
                incomplete_token = []
            resulting_tokens.append(token)
    
    return resulting_tokens

def tokenize_query(query):

    #tokens = query.split(' ')
    #tokens = [x for x in tokens if x]
    #tokens = join_incomplete_tokens(tokens)
    tokens = []
    new_token = ''
    ignore_space = True
    for i,c in enumerate(query):
        if c == ' ' and ignore_space:
            if new_token != '':
                tokens.append(new_token)
                new_token = ''
            continue
        elif c in [';','{','}']:
            if new_token != '':
                tokens.append(new_token)
            tokens.append(c)
            new_token = ''
            continue
        elif c == '.':
            if query[i+1] in [' ','}']:
                if new_token != '':
                    tokens.append(new_token)
                tokens.append(c)
                new_token = ''
                continue
        elif c == '"':
            ignore_space = not ignore_space
        new_token += c
    return tokens[1:-1]
    #return resulting_tokens

def construct_triple_templates(triple_tokens):
    triples = []
    union_triples = []
    leading_token = None
    in_union = False
    for token in triple_tokens:
        if token == '{':
            leading_token = None
            in_union = True
        elif token == '}':
            leading_token = None
            in_union = False
        elif token == 'UNION':
            continue
        elif leading_token == None:
            leading_token = token
            if in_union:
                union_triples.append(leading_token)
            else:
                triples.append(leading_token)
        elif token == ';':
            if in_union:
                union_triples.append(leading_token)
            else:
                triples.append(leading_token)
        elif token == '.':
            leading_token = None
       
        else:
            if in_union:
                union_triples[-1] = union_triples[-1] + ' ' + token
            else:
                triples[-1] = triples[-1] + ' ' + token
    for triple in triples:
        if len(triple.split(' ')) != 3:
            print('Bad triple:', triple)
            print(triple_tokens)
    for triple in union_triples:
        if len(triple.split(' ')) != 3:
            print('Bad triple:', triple)
            print(triple_tokens)
    return triples, union_triples

def extract_sparql_prefixes(sparql_query):
    prefixes = dict()
    tokens = sparql_query.split(' ')
    for i,token in enumerate(tokens):
        if token == 'PREFIX':
            prefix_key = tokens[i+1][:-1]
            prefix_val = tokens[i+2]
            prefixes[prefix_key] = prefix_val
    return prefixes

datafile = 'Data/qald-9-train-multilingual.json'
with open(datafile,'r') as f:
    data = json.load(f)
#print(data)

questions = data['questions']
result_dict = {'questions' : []}
i = 0
for q in questions[:]:
    question = ''
    for q_lang in q["question"]:
        if q_lang['language'] == 'en':
            question = q_lang['string']
            break

    sparql_query = q['query']['sparql']

    if 'ASK' in q['query']['sparql']:
        sparql_query = sparql_query.replace('ASK', 'SELECT *')
    sparql_query = re.sub('SELECT (.*) WHERE','SELECT * WHERE',sparql_query)
    left_start = sparql_query.index('{')
    right_start = sparql_query.rindex('}')
    query_pattern = sparql_query[left_start:right_start+1]
    query_pattern = re.sub(' FILTER(.*)\)', '', query_pattern)
    query_pattern = re.sub(' OPTIONAL','',query_pattern)

    query_constraint = sparql_query[right_start+1:]
    prefixes = extract_sparql_prefixes(sparql_query)
    #prefixes['dbr'] = '<http://dbpedia.org/resource/>'

    if 'FILTER' in query_pattern:
        print('Bad Filter: ', query_pattern)
    
    tokens = tokenize_query(query_pattern)
    triple_templates, union_templates = construct_triple_templates(tokens)

    #print(q['answers'][0])
    if q['answers'][0]['head']:
        answer_type = q['answers'][0]['head']['vars'][0]
        answers = [x[answer_type]['value'] for x in q['answers'][0]['results']['bindings']]
    else:
        answers = [q['answers'][0]['boolean']]
    
    group_by_var = None
    group_by_results = []
    if 'GROUP' in query_constraint:
        group_by_var = re.findall('\?(.*?) ', query_constraint)[0]
        group_by_sparql_query = sparql_query.replace('*', '?' + group_by_var)
        pattern_variables = get_answer(sparql_query[:right_start+1])
        group_by_variables = get_answer(group_by_sparql_query)

        for result in group_by_variables['results']['bindings']:
            group_by_results.append(result[group_by_var]['value'])

        #print(pattern_variables)
        #print(group_by_variables)
        pass
    else:
        #continue
        pattern_variables = get_answer(sparql_query)


    print(question)
    print(sparql_query)
    relevant_triples = set()

    ask_template = ''
    for prefix, val in prefixes.items():
        ask_template += 'PREFIX ' + prefix + ': ' + val + ' '
    ask_template += 'ASK WHERE { *TRIPLE* . }'
    print(ask_template)

    

    for result in pattern_variables['results']['bindings']:
        print(result)
        triples = set()
        union_triples = set()
        if group_by_var and not result[group_by_var]['value'] in group_by_results:
            print('Not',result[group_by_var]['value'])
            continue
        for template in triple_templates:
            new_triple = template
            for var in result.keys():
                result_string = result[var]['value']
                result_string = result_string.replace('\n','\\n')
                new_triple = new_triple.replace('?'+var,'<'+result_string+'>')
            
            triples = triples | {new_triple}
        for template in union_templates:
            new_triple = template
            for var in result.keys():
                result_string = result[var]['value']
                result_string = result_string.replace('\n','\\n')
                print(result_string)
                #print(result[var])
                if result[var]['type'] == 'uri':
                    new_triple = new_triple.replace('?'+var,'<'+result_string+'>')
                elif result[var]['type'] == 'literal':
                    language = result[var]['xml:lang']
                    new_triple = new_triple.replace('?'+var,'"'+result_string+'"'+'@'+language)
                elif result[var]['type'] == 'typed-literal':
                    datatype = result[var]['datatype']
                    new_triple = new_triple.replace('?'+var,'"'+result_string+'"^^<'+datatype+'>')
                else:
                    print('Unexpected result type:', result[var]['type'])
                    exit(0)
            #print(new_triple)
            ask_query = ask_template.replace('*TRIPLE*', new_triple)
                
            ask_result = get_ask_result(ask_query)
            if ask_result['boolean']:
                union_triples = union_triples | {new_triple}

        if union_templates == [] or len(union_triples) != 0:
            relevant_triples |= triples
            relevant_triples |= union_triples
        else:
            print('Triples:', triples)
            print('Not compatible with union templates:', union_templates)
        print(triples)
        print(union_triples)
    print(i)
    i = i+1

    print(relevant_triples)
    qtq_dict = dict()
    qtq_dict['question'] = question
    qtq_dict['query'] = q['query']['sparql']
    qtq_dict['triples'] = list(relevant_triples)
    result_dict['questions'].append(qtq_dict)
    print('\n\n')
    #print(pattern_variables,end='\n\n')
with open('dataset.json', 'w') as f:
    json.dump(result_dict, f, indent=4, separators=(',', ': '))

#print(json_dump)
