from lib2to3.pgen2 import token
import re
import spacy
from kb.common import WhitespaceTokenizer, MentionGenerator, get_empty_candidates
import requests
from json.decoder import JSONDecodeError
import json
from subprocess import Popen, PIPE

@MentionGenerator.register("dbpedia_mention_generator")
class DBPediaMentionGenerator(MentionGenerator):
    """
    Generate lists of candidate entities. Provides several methods that
    process input text of various format to produce mentions.

    Each text is represented by:
            {'tokenized_text': List[str],
             'candidate_spans': List[List[int]] list of (start, end) indices for candidates,
                    where span is tokenized_text[start:(end + 1)]
             'candidate_entities': List[List[str]] = for each entity,
                    the candidates to link to. value is synset id, e.g
                    able.a.02 or hot_dog.n.01
             'candidate_entity_priors': List[List[float]]
        }
    """
    def __init__(
            self,
            max_entity_length: int = 7,
            max_number_candidates: int = 30,
            count_smoothing: int = 1,
            use_surface_form: bool = False,
            random_candidates: bool = False):

        self.tokenizer = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'ner', 'textcat'])
        self.whitespace_tokenizer = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'ner', 'textcat'])
        self.whitespace_tokenizer.tokenizer = WhitespaceTokenizer(self.whitespace_tokenizer.vocab)

    def get_mentions_raw_text(
                self,
                text: str,
                whitespace_tokenize: bool = False,
                allow_empty_candidates: bool = False,
                confidence: float = 0.8
        ):
        """
        returns:
            {'tokenized_text': List[str],
             'candidate_spans': List[List[int]] list of (start, end) indices for candidates,
                    where span is tokenized_text[start:(end + 1)]
             'candidate_entities': List[List[str]] = for each entity,
                    the candidates to link to
             'candidate_entity_priors': List[List[float]]
        }
        """

        text = ' '.join(list(filter(lambda x: x != '', text.split(' '))))

        if whitespace_tokenize:
            tokenized = self.tokenizer(text)
        else:
            tokenized = self.whitespace_tokenizer(text)

        tokenized_text = [token.text for token in tokenized]

        curr_offset = 0
        token_offsets = []
        for token in tokenized_text:
            token_offsets.append(curr_offset)
            curr_offset += len(token) + 1

        print(tokenized_text)
        print(token_offsets)

        dbpedia_endpoint = "https://api.dbpedia-spotlight.org/en/annotate"
        dbpedia_resp = self._get_annotator_response(dbpedia_endpoint,
                                                    header={"Accept": "application/json"},
                                                    data={"text": text, "confidence": confidence})

        candidate_spans = []
        candidate_entities = []
        candidate_entity_priors = []
        print(dbpedia_resp)
        for res in dbpedia_resp['Resources']:
            res_surface_form_split = res['@surfaceForm'].split(' ')
            res_offset = int(res['@offset'])
            res_candidate = res['@URI']
            print(res_surface_form_split)
            token_idx = token_offsets.index(res_offset)
            span = (token_idx, token_idx + len(res_surface_form_split))
            if span in candidate_spans:
                span_idx = candidate_spans.index(span)
                if res_candidate not in candidate_entities[span_idx]:
                    candidate_entities[span_idx].append(res_candidate)
            else:
                candidate_spans.append(span)
                candidate_entities.append([res_candidate])


        falcon2_endpoint = "https://labs.tib.eu/falcon/falcon2/api?mode=long&db=1"
        falcon2_resp = self._get_annotator_response(falcon2_endpoint,
                                                    header={"Content-Type": "application/json"},
                                                    data=json.dumps({"text": text}))
        print(falcon2_resp)
        dbpedia_entities = falcon2_resp["entities_dbpedia"]
        dbpedia_relations = falcon2_resp["relations_dbpedia"]
        results = dbpedia_entities + dbpedia_relations
        for res in results:
            res_surface_form_split = res[1].split(' ')
            res_candidate = res[0]

            spans = find_spans_for_surface_form(tokenized_text, res_surface_form_split)

            for span in spans:
                if span in candidate_spans:
                    span_idx = candidate_spans.index(span)
                    if res_candidate not in candidate_entities[span_idx]:
                        candidate_entities[span_idx].append(res_candidate)
                else:
                    candidate_spans.append(span)
                    candidate_entities.append([res_candidate])


        #ask question
        summarized_triples = []
        with Popen(["/home/jmenzel/python-envs/kbqa-env/bin/python",
                    "/home/jmenzel/Programs/KBQA-PG/KBQA/appB/summarizers/test_rank.py",
                    "/home/jmenzel/Programs/KBQA-PG/KBQA/datasets/",
                    text],
                    stdout=PIPE) as summarizer_process:
            for line in summarizer_process.stdout:
                line = line.decode('utf-8')
                line = line.replace('\n', '')
                if line.startswith('<'):
                    s, p, o = line.split(' ', maxsplit=2)
                    if not o.startswith('<'):
                        print("Discarding: ", s, p, o)
                    else:
                        summarized_triples.append((s, p, o))
        #relate entities to triples


        candidate_triples = []
        for candidates in candidate_entities:
            candidate_triples.append([])
            for candidate in candidates:
                for triple in summarized_triples:
                    print("Comparing: ", candidate, " to ", triple[0])
                    candidate_formated = '<' + candidate + '>'
                    if candidate_formated == triple[0] and len(candidate_triples[-1]) < 5:
                        candidate_triples[-1].append(triple)
        
        print(candidate_triples)


        #remove entities/relations with no triples

        final_candidate_spans = []
        final_candidate_triples = []
        for span in candidate_spans:
            span_idx = candidate_spans.index(span)
            if candidate_triples[span_idx]:
                final_candidate_spans.append(span)
                final_candidate_triples.append(candidate_triples[span_idx])

        #generate priors from ranks

        for cands in final_candidate_triples:
            candidate_entity_priors.append([1/len(cands)]*len(cands))

        ret = {'tokenized_text': tokenized_text,
               'candidate_spans': final_candidate_spans,
               'candidate_entities': final_candidate_triples,
               'candidate_entity_priors': candidate_entity_priors}

        if not allow_empty_candidates and len(candidate_spans) == 0:
            # no candidates found, substitute the padding entity id
            ret.update(get_empty_candidates())

        return ret

    def _get_annotator_response(self, endpoint, header, data):
        try:
            response = requests.post(
                endpoint,
                headers=header,
                data=data,
            ).json()
        except JSONDecodeError as jsonE:
            print(f"[ERROR]: Exception: {jsonE}.")
            response = None
        return response

def find_spans_for_surface_form(tokenized_text, tokenized_surface_form):
    tt = tokenized_text
    tsf = tokenized_surface_form
    spans = []
    for i, token in enumerate(tt):
        if token == tsf[0] and tt[i:i+len(tsf)] == tsf:
            spans.append((i,i+len(tsf)))
    return spans