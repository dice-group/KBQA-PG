import json


def qald_builder(sparql_query, answer, question, language):
    """qald builder if sparql is found

    parameters:sparql_query,question,language
    returns:qald json with answer
    """

    # id-Object
    json_id = {
       "id": "1" 
    }

    # question-Object   
    json_question = {
            "question" : [{
                "language": language,
                "string": question
            }]
        }

    # query-Object        
    json_query = {
            "query": {
                "sparql": sparql_query
            }        
    }
    
    # answers-Object
    json_answers = {
            "answers": []
    }

    json_answers["answers"].append(answer)
    
    # Combined-Object  
    questions_obj = {
        "id" : json_id["id"],
        "question" : json_question["question"],
        "query" : json_query["query"],
        "answers" : json_answers["answers"]        
    }
    
    # Question-Object
    json_questions = {
        "questions": []
    }

    json_questions["questions"].append(questions_obj)
    
    return json.dumps(json_questions)


def qald_builder_empty_answer(sparql_query, question, language):
    """qald builder if sparql is not found
    
    parameters:sparql_query,question,language
    returns:qald json with empty answer 
    """   

    # id-Object
    json_id = {
       "id": "1" 
    }

    # question-Object    
    json_question = {
            "question" : [{
                "language": language,
                "string": question
            }]
        }

    # query-Object          
    json_query = {
            "query": {
                "sparql": sparql_query
            }        
    }
    
    # answers-Object
    json_answers = {
            "answers": [{
                "head": {
                    "vars":[]
                    
                },
                "results": {
                    "bindings":[]
                }
            }]
    }    
    
    # Combined-Object    
    questions_obj = {
        "id" : json_id["id"],
        "question" : json_question["question"],
        "query" : json_query["query"],
        "answers" : json_answers["answers"]        
    }
    
    
    # Question-Object
    json_questions = {
        "questions": []
    }
     
    json_questions["questions"].append(questions_obj)
    
    return json.dumps(json_questions)

