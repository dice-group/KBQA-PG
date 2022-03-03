from kb.dbpedia import DBPediaMentionGenerator

texts = ['Who is the     president of the United States of America', 'Bill Clinton is a friend of Barack Obama', 'Who are the parents of Luke Skywalker', 'Barack Obama is Barack Obama and Luke Sykwalker loves Luke Skywalker']

mg = DBPediaMentionGenerator()

for text in texts:
    res = mg.get_mentions_raw_text(text, whitespace_tokenize=True,confidence=0.5)
    print(res)