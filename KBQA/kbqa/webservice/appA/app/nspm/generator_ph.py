
import collections
import http.client
import json
import logging
import re
import sys
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
from functools import reduce

import argparse
import collections
import datetime
import json
import logging
import operator
import os
import random
import re
import sys
import traceback
from tqdm import tqdm
import io
import ssl

import importlib

CELEBRITY_LIST = [
    'dbo:Royalty',
    '<http://dbpedia.org/class/yago/Wikicat21st-centuryActors>',
    '<http://dbpedia.org/class/yago/WikicatEnglishMusicians>',
    '<http://dbpedia.org/class/yago/Wikicat20th-centuryNovelists>',
    '<http://dbpedia.org/class/yago/Honoree110183757>'
]

SPECIAL_CLASSES = {
    'dbo:Person': [
        '<http://dbpedia.org/class/yago/Wikicat21st-centuryActors>',
        '<http://dbpedia.org/class/yago/WikicatEnglishMusicians>',
        '<http://dbpedia.org/class/yago/Wikicat20th-centuryNovelists>',
        '<http://dbpedia.org/class/yago/Honoree110183757>',
        'dbo:LacrossePlayer'
    ],
    'dbo:Athlete': ['dbo:LacrossePlayer'],
    'dbo:SportsTeam': ['dboBasketballTeam']
}

REPLACEMENTS = [
    ['dbo:', 'http://dbpedia.org/ontology/', 'dbo_'],
    ['dbp:', 'http://dbpedia.org/property/', 'dbp_'],
    ['dbc:', 'http://dbpedia.org/resource/Category:', 'dbc_'],
    ['dbr:', 'res:', 'http://dbpedia.org/resource/', 'dbr_'],
    ['dct:', 'dct_'],
    ['geo:', 'geo_'],
    ['georss:', 'georss_'],
    ['rdf:', 'rdf_'],
    ['rdfs:', 'rdfs_'],
    ['foaf:', 'foaf_'],
    ['owl:', 'owl_'],
    ['yago:', 'yago_'],
    ['skos:', 'skos_'],
    [' ( ', '  par_open  '],
    [' ) ', '  par_close  '],
    ['(', ' attr_open '],
    [') ', ')', ' attr_close '],
    ['{', ' brack_open '],
    ['}', ' brack_close '],
    [' . ', ' sep_dot '],
    ['. ', ' sep_dot '],
    ['?', 'var_'],
    ['*', 'wildcard'],
    [' <= ', ' math_leq '],
    [' >= ', ' math_geq '],
    [' < ', ' math_lt '],
    [' > ', ' math_gt ']
]

STANDARDS = {
        'dbo_almaMater': ['dbp_almaMater'],
        'dbo_award': ['dbp_awards'],
        'dbo_birthPlace': ['dbp_birthPlace', 'dbp_placeOfBirth'],
        'dbo_deathPlace': ['dbp_deathPlace', 'dbp_placeOfDeath'],
        'dbo_child': ['dbp_children'],
        'dbo_college': ['dbp_college'],
        'dbo_hometown': ['dbp_hometown'],
        'dbo_nationality': ['dbo_stateOfOrigin'],
        'dbo_relative': ['dbp_relatives'],
        'dbo_restingPlace': ['dbp_restingPlaces', 'dbp_placeOfBurial', 'dbo_placeOfBurial', 'dbp_restingplace'],
        'dbo_spouse': ['dbp_spouse'],
        'dbo_partner': ['dbp_partner']
}

EXAMPLES_PER_TEMPLATE = 600

# Generator utils

def read_template_file(file):
    annotations = list()
    line_number = 1
    with open(file) as f:
        for line in f:
            values = line[:-1].split(';')
            target_classes = [values[0] or None, values[1] or None, values[2] or None]
            question = values[3]
            query = values[4]
            generator_query = values[5]
            id = values[6] if (len(values) >= 7 and values[6]) else line_number
            line_number += 1
            annotation = Annotation(question, query, generator_query, id, target_classes)
            annotations.append(annotation)
    return annotations

class Annotation:
    def __init__(self, question, query, generator_query, id=None, target_classes=None):
        self.question = question
        self.query = query
        self.generator_query = generator_query
        self.id = id
        self.target_classes = target_classes if target_classes != None else []
        self.variables = extract_variables(generator_query)


def extract_variables(query):
    variables = []
    query_form_pattern = r'^.*?where'
    query_form_match = re.search(query_form_pattern, query, re.IGNORECASE)
    if query_form_match:
        letter_pattern = r'\?(\w)'
        variables = re.findall(letter_pattern, query_form_match.group(0))
    return variables

def encode( sparql ):
    encoded_sparql = do_replacements(sparql)
    shorter_encoded_sparql = shorten_query(encoded_sparql)
    normalized = normalize_predicates(shorter_encoded_sparql)
    return normalized

def do_replacements( sparql ):
    for r in REPLACEMENTS:
        encoding = r[-1]
        for original in r[:-1]:
            sparql = sparql.replace(original, encoding)
    return sparql

def shorten_query( sparql ):
    sparql = re.sub(r'order by desc\s+....?_open\s+([\S]+)\s+....?_close', '_obd_ \\1', sparql, flags=re.IGNORECASE)
    sparql = re.sub(r'order by asc\s+....?_open\s+([\S]+)\s+....?_close', '_oba_ \\1', sparql, flags=re.IGNORECASE)
    sparql = re.sub(r'order by\s+([\S]+)', '_oba_ \\1', sparql, flags=re.IGNORECASE)
    return sparql

def normalize_predicates( sparql ):
    for standard in STANDARDS:
        for alternative in STANDARDS[standard]:
            sparql = sparql.replace(alternative, standard)

    return sparql


def save_cache ( file, cache ):
    ordered = collections.OrderedDict(cache.most_common())
    with open(file, 'w') as outfile:
        json.dump(ordered, outfile)

def log_statistics( used_resources, special_classes, not_instanced_templates ):
    total_number_of_resources = len(used_resources)
    total_number_of_filled_placeholder_positions = sum(used_resources.values())
    examples_per_instance = collections.Counter()
    for resource in used_resources:
        count = used_resources[resource]
        examples_per_instance.update([count])

    logging.info('{:6d} used resources in {} placeholder positions'.format(total_number_of_resources, total_number_of_filled_placeholder_positions))
    for usage in examples_per_instance:
        logging.info('{:6d} resources occur \t{:6d} times \t({:6.2f} %) '.format(examples_per_instance[usage], usage, examples_per_instance[usage]*100/total_number_of_resources))
    for cl in special_classes:
        logging.info('{} contains: {}'.format(cl, ', '.join(special_classes[cl])))
    logging.info('{:6d} not instanciated templates:'.format(sum(not_instanced_templates.values())))
    for template in not_instanced_templates:
        logging.info('{}'.format(template))

def build_dataset_pair(template):
    english = getattr(template, 'question')
    sparql = getattr(template, 'query')

    sparql = encode(sparql)
    dataset_pair = {'english': english, 'sparql': sparql}
    return dataset_pair

def generate_dataset(templates, output_dir, file_mode):
    cache = dict()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    it = 0
    with io.open(output_dir + '/data.en', file_mode, encoding="utf-8") as english_questions, io.open(output_dir + '/data.sparql', file_mode, encoding="utf-8") as sparql_queries:
        for template in tqdm(templates):
            it = it + 1
            print("for {}th template".format(it))
            try:
                dataset_pair = build_dataset_pair(template)
                english_questions.write("{}\n".format(dataset_pair['english']))
                sparql_queries.write("{}\n".format(dataset_pair['sparql']))

            except:
                exception = traceback.format_exc()
                # logging.error('template {} caused exception {}'.format(
                #     getattr(template, 'id'), exception))
                # logging.info(
                #     '1. fix problem\n2. remove templates until the exception template in the template file\n3. restart with `--continue` parameter')
                raise Exception()


template_file = 'data/templates/template_qald9test.csv'
output_dir = 'data/qald9_test'
use_resources_dump = False

ssl._create_default_https_context = ssl._create_unverified_context

# print use_resources_dump => False

time = datetime.datetime.today()
logging.basicConfig(
    filename='{}/generator_{:%Y-%m-%d-%H-%M}.log'.format(output_dir, time), level=logging.DEBUG)
resource_dump_file = output_dir + '/resource_dump.json'
resource_dump_exists = os.path.exists(resource_dump_file)


# print resource_dump_file, resource_dump_exists => data/place_v1/resource_dump.json False

if (resource_dump_exists and not use_resources_dump):
    warning_message = 'Warning: The file {} exists which indicates an error. Remove file or continue generation after fixing with --continue'.format(
        resource_dump_file)
    print(warning_message)
    sys.exit(1)

importlib.reload(sys)

not_instanced_templates = collections.Counter()
used_resources = collections.Counter(json.loads(open(
    resource_dump_file).read())) if use_resources_dump else collections.Counter()
file_mode = 'a' if use_resources_dump else 'w'
templates = read_template_file(template_file)

try:
    generate_dataset(templates, output_dir, file_mode)
except:
    print('exception occured, look for error in log file')
    save_cache(resource_dump_file, used_resources)
else:
    save_cache(
        '{}/used_resources_{:%Y-%m-%d-%H-%M}.json'.format(output_dir, time), used_resources)
finally:
    log_statistics(used_resources, SPECIAL_CLASSES,
                    not_instanced_templates)