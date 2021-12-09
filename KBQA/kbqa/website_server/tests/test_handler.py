import unittest
import json

from app.handler import extract_bindings_from_QALD, format_bindings


class TestHandler(unittest.TestCase):

    qald_single_answer = '''{
            "questions" : [ {
                "id" : "1",
                "answertype" : "resource",
                "aggregation" : false,
                "onlydbo" : false,
                "hybrid" : false,
                "question" : [ {
                      "language" : "en",
                      "string" : "What is the alma mater of the chancellor of Germany Angela Merkel?",
                      "keywords" : "Angela Merkel"
                } ],
                "query" : {
                      "sparql" : "PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT ?Almamater WHERE { dbr:Angela_Merkel dbo:almaMater ?Almamater }"
                },
                "answers" : [ {
                      "head" : {
                        "vars" : [ "uri" ]
                      },
                      "results" : {
                        "bindings" : [ {
                              "uri" : {
                                "type" : "uri",
                                "value" : "http://dbpedia.org/resource/Leipzig_University"
                              }
                        } ]
                      }
                } ]
            } ]
        }
    '''

    qald_multiple_answers = '''{ 
        "questions" : [ {
            "id" : "46",
            "answertype" : "resource",
            "aggregation" : false,
            "onlydbo" : true,
            "hybrid" : false,
            "question" : [ {
                "language" : "en",
                "string" : "What other books have been written by the author of The Fault in Our Stars?",
                "keywords" : "books,  author,  The Fault in Our Stars"
            } ],
            "query" : {
                "sparql" : "PREFIX dbo: <http://dbpedia.org/ontology/> SELECT ?books WHERE { ?books dbo:author <http://dbpedia.org/resource/John_Green_(author)> }"
            },
            "answers" : [ {
                "head" : {
                    "vars" : [ "uri" ]
                },
                "results" : {
                    "bindings" : [ {
                        "uri" : {
                            "type" : "uri",
                            "value" : "http://dbpedia.org/resource/Will_Grayson,_Will_Grayson"
                        }
                    }, {
                        "uri" : {
                            "type" : "uri",
                            "value" : "http://dbpedia.org/resource/An_Abundance_of_Katherines"
                        }
                    }, {
                        "uri" : {
                            "type" : "uri",
                            "value" : "http://dbpedia.org/resource/Looking_for_Alaska"
                        }
                    }, {
                        "uri" : {
                            "type" : "uri",
                            "value" : "http://dbpedia.org/resource/The_Fault_in_Our_Stars"
                        }
                    }, {
                        "uri" : {
                            "type" : "uri",
                            "value" : "http://dbpedia.org/resource/Let_It_Snow:_Three_Holiday_Romances"
                        }
                    }, {
                        "uri" : {
                            "type" : "uri",
                            "value" : "http://dbpedia.org/resource/Paper_Towns"
                        }
                    } ]
                }
            } ]
        } ]
    }
    '''

    qald_empty_answer = '''{
            "questions" : [ {
                "id" : "1",
                "answertype" : "resource",
                "aggregation" : false,
                "onlydbo" : false,
                "hybrid" : false,
                "question" : [ {
                      "language" : "en",
                      "string" : "What is the sense of life?",
                      "keywords" : "sense"
                } ],
                "query" : {
                    "sparql" : "PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT ?sense WHERE { ?sense dbo:of dbr:life }"
                },
                "answers" : [ {
                    "head" : {
                        "vars" : [ "uri" ]
                    },
                    "results" : {
                        "bindings" : []
                    }
                } ]
            } ]
        }
    '''


    def test_QALD_parsing_for_single_answer(self):
        json_format = json.loads(self.qald_single_answer)
        bindings = extract_bindings_from_QALD(json_format)

        self.assertListEqual(bindings, [('uri', 'http://dbpedia.org/resource/Leipzig_University')])

        formated_bindings = format_bindings(bindings)

        self.assertListEqual(formated_bindings, ["Leipzig University"])


    def test_QALD_parsing_for_multiple_answers(self):
        json_format = json.loads(self.qald_multiple_answers)
        bindings = extract_bindings_from_QALD(json_format)

        self.assertListEqual(bindings, [
            ('uri', 'http://dbpedia.org/resource/Will_Grayson,_Will_Grayson'), 
            ('uri', 'http://dbpedia.org/resource/An_Abundance_of_Katherines'), 
            ('uri', 'http://dbpedia.org/resource/Looking_for_Alaska'), 
            ('uri', 'http://dbpedia.org/resource/The_Fault_in_Our_Stars'), 
            ('uri', 'http://dbpedia.org/resource/Let_It_Snow:_Three_Holiday_Romances'), 
            ('uri', 'http://dbpedia.org/resource/Paper_Towns')
        ])

        formated_bindings = format_bindings(bindings)
        
        self.assertListEqual(formated_bindings, [
            "Will Grayson, Will Grayson", 
            "An Abundance of Katherines", 
            "Looking for Alaska", 
            "The Fault in Our Stars", 
            "Let It Snow: Three Holiday Romances", 
            "Paper Towns"
        ])

    def test_QALD_parsing_for_empty_answer(self):
        json_format = json.loads(self.qald_empty_answer)
        bindings = extract_bindings_from_QALD(json_format)

        self.assertListEqual(bindings, [])

        formated_bindings = format_bindings(bindings)

        self.assertListEqual(formated_bindings, ['No answer found'])

if __name__ == '__main__':
    unittest.main()
