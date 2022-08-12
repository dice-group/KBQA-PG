# Datasets

This folder contains all of our datasets.

## Content

### lc-quad, qald-8, qald-9

The respectively named datasets. They also contain updated versions, see
[here](#insights-from-dataset-updating-using-quant) for information on the update.
We also note some information on the difference between qald-8 and -9 at [Comparison of QALD 8 and 9](#comparison-of-qald-8-and-9).

### qald-8-9-merged

Duplicate free merge of updated versions of qald-8 and qald-9 with the intent to test on qald-9-test after training
with the merged dataset.

### qtq

qtq (question-triple-query) datasets. Given a dataset with questions and queries (SPARQLs) e.g. qald-9, we generate
triples with one of our [summarizers](../appB/summarizers/README.md) in `KBQA/appB/summarizers`. These triples are
added to the datasets. These new kind of dataset we name qtq-datasets.

### preprocessed

Preprocessors of the App B models often take time. Here we store the preprocessed datasets. For more information, see
[/preprocessed](preprocessed/README.md).

## Insights from dataset updating using QUANT:

Object or property not existent (What are the official languages of the Philippines?)
Entity of list does not match with dbpedia page (Which movies starring Brad Pitt were directed by Guy Ritchie?)
Property is not specific (number instead of name) (Give me the grandchildren of Bruce Lee.)
Wikipage / Company was renamed. Maybe redirect? (Who is the owner of Universal Studios?)
Sparql incomplete (Which state of the United States of America has the highest density?)
Incomplete answer list / dbpeadia knowledge is missing (Give me a list of all trumpet players that were bandleaders.)  
Answer type is wrong (When was the Statue of Liberty built?)  
Language (@en) oder type tag (@int) is added (Who is the governor of Wyoming?)  
Fixed dates in SPARQL instead of relative (Give me all world heritage sites designated within the past two years.)  
Old SPARQL format used e.g. filtering (Give me all actors who were born in Paris after 1950.)  
Property is missing for some pages (What is the highest mountain?)

## Comparison of QALD 8 and 9:

Number of Questions in:

### Train Set

#QALD 8 Train: 219  
#QALD 9 Train: 408

26 Questions from QALD 8 Train, which are not included in QALD 9 Train:

Which museum exhibits The Scream by Munch? (id 15)  
Which movies did Kurosawa direct? (id 105)  
Give me a list of all critically endangered birds. (id 112)  
Which book has the most pages? (id 115)  
What is the area code of Berlin? (id 123)  
When was Jack Wolfskin founded? (id 147)  
Who are the parents of the wife of Juan Carlos I? (id 151)  
Who were the parents of Queen Victoria? (id 156)  
Are there any castles in the United States? (id 180)  
Can you find frescoes in Crete? (id 181)  
How many years was the Ford Model T manufactured? (id 184)  
Give me all gangsters from the prohibition era. (id 185)  
Give me all Seven Wonders of the Ancient World. (id 186)  
Give me all chemical elements. (id 187)  
How many rivers and lakes are in South Carolina? (id 188)  
Is Pluto really a planet? (id 192)  
What is the largest state in the United States? (id 195)  
What is the wavelength of indigo? (id 198)  
What was the name of the famous battle in 1836 in San Antonio? (id 199)  
What were the names of the three ships used by Columbus? (id 200)  
When did Muhammad die? (id 201)  
When was the De Beers company founded? (id 202)  
Which American presidents were in office during the Vietnam War? (id 204)  
Who assassinated President McKinley? (id 207)  
Who killed Caesar? (id 209)  
How big is the earth's diameter? (id 214)

### Test Set

#QALD 8 Test: 41  
#QALD 9 Test: 150

38 Questions from QALD 8 Test, which are not included in QALD 9 Test:

What is the alma mater of the chancellor of Germany Angela Merkel? (id 1)  
How large is the area of UK? (id 2)  
Who is the author of the interpretation of dreams? (id 3)  
What is the birth name of Adele? (id 4)  
What are the top selling luxury vehicle brands in Germany? (id 5)  
Who is Dan Jurafsky? (id 7)  
When will start the final match of the football world cup 2018? (id 8)  
how much is the elevation of Düsseldorf Airport ? (id 10)  
how much is the total population of european union? (id 11)  
when was the founding date of french fifth republic? (id 12)  
Who are the founders of BlaBlaCar? (id 13)  
how many foreigners speak German? (id 15)  
Where is the birthplace of Goethe? (id 16)  
Where is the origin of Carolina reaper? (id 17)  
How much is the population of Mexico City ? (id 18)  
What is the percentage of area water in Brazil? (id 21)  
How much is the population of Iraq? (id 22)  
What is the population of Cairo? (id 24)  
How much is the population density rank of Germany? (id 25)  
What is the relation between Resource Description Framework and Web Ontology Language? (id 26)  
How large is the total area of North Rhine-Westphalia? (id 27)  
What is the original title of the interpretation of dreams? (id 28)  
Who are the writers of the Wall album of Pink Floyd? (id 30)  
When was the death of Shakespeare? (id 31)  
With how many countries Iran has borders? (id 32)  
What is the smallest city by area in Germany? (id 34)  
Which beer brewing comapnies are located in North-Rhine Westphalia? (id 35)  
What is the largest city in america? (id 36)  
Who is the current federal minister of finance in Germany? (id 37)  
What is the highest mountain in the Bavarian Alps? (id 38)  
Who is 8th president of US? (id 40)  
Where is the most deep point in the ocean? (id 41)  
In which state Penn State University is located? (id 42)  
Which species does an elephant belong? (id 43)  
What is Donald Trump's main business? (id 44)  
What is the last work of Dan Brown? (id 45)  
What other books have been written by the author of The Fault in Our Stars? (id 46)  
When was the last episode of the TV series Friends aired? (id 47)
