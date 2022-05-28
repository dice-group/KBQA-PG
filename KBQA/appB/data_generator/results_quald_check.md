Unanswered questions were mostly marked as out of scope for DBpedia in the first place (QUALD dataset).
Or SPARQLS gave the wrong answer to the question.

## updated-qald-9-train

total 407  
answerd 381  
unanswerd 25  
errored 1

(-) Which other weapons did the designer of the Uzi develop?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX dbp: <http://dbpedia.org/property/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type dbo:Weapon ; dbp:designer ?x . res:Uzi dbp:designer ?x FILTER ( ?uri != res:Uzi ) }
(-) Which state of the USA has the highest population density?
PREFIX yago: <http://dbpedia.org/class/yago/> PREFIX dbp: <http://dbpedia.org/property/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type yago:WikicatStatesOfTheUnitedStates ; dbp:densityrank ?rank } ORDER BY ASC(?rank) LIMIT 1
(-) Which monarchs were married to a German?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type dbo:Monarch ; dbo:spouse ?spouse { ?spouse dbo:birthPlace res:Germany } UNION { ?spouse dbo:birthPlace ?p . ?p dbo:country res:Germany } }
(-) Who is the daughter of Ingrid Bergman married to?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Ingrid_Bergman dbo:child ?child . ?child <http://dbpedia.org/property/spouse> ?uri }
(-) How heavy is Jupiter's lightest moon?
SELECT DISTINCT ?n WHERE { ?uri <http://dbpedia.org/property/satelliteOf> <http://dbpedia.org/resource/Jupiter> ; <http://dbpedia.org/ontology/mass> ?n } ORDER BY ASC(?n) OFFSET 0 LIMIT 1
(#) SPARQLWrapperException QueryBadFormed: a bad request has been sent to the endpoint, probably the sparql query is bad formed.
Response:
b"Virtuoso 37000 Error SP030: SPARQL compiler, line 2: syntax error at '{' before 'res:Universal_Pictures'\n\nSPARQL query:\n#output-format:application/sparql-results+json\nPREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Universal_Studios dbo:owner ?uri } { res:Universal_Pictures dbo:parentCompany ?owner. }"
(-) Who is the tallest player of the Atlanta Falcons?
SELECT DISTINCT ?uri WHERE { ?uri <http://dbpedia.org/ontology/team> <http://dbpedia.org/resource/Atlanta_Falcons> ; <http://dbpedia.org/ontology/height> ?h } ORDER BY DESC(?h) OFFSET 0 LIMIT 1
(-) How many inhabitants does Maribor have?
SELECT DISTINCT ?num WHERE { <http://dbpedia.org/resource/Maribor> <http://dbpedia.org/ontology/populationBlank> ?num }
(-) Which beer originated in Ireland?
SELECT DISTINCT ?uri WHERE { ?uri <http://dbpedia.org/property/type> <http://dbpedia.org/resource/Beer> ; <http://dbpedia.org/ontology/origin> <http://dbpedia.org/resource/Ireland> }
(-) How many employees does Google have?
SELECT DISTINCT ?num WHERE { <http://dbpedia.org/resource/Google> <http://dbpedia.org/ontology/numberOfEmployees> ?num }
(-) Give me all B-sides of the Ramones.
SELECT DISTINCT ?string WHERE { ?x <http://dbpedia.org/ontology/musicalArtist> <http://dbpedia.org/resource/Ramones> ; <http://dbpedia.org/ontology/bSide> ?string }
(-) when was the founding date of french fifth republic?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT ?ff WHERE { dbr:French_Fifth_Republic dbo:foundingDate ?ff }
(-) Which species does an elephant belong?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { res:Burj_Khalifa dbo:floorCount ?burj . ?uri rdf:type dbo:Building ; dbo:floorCount ?proj FILTER ( ?proj < ?burj ) } ORDER BY DESC(?proj) LIMIT 1
(-) Who is the mayor of Tel Aviv?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Tel_Aviv dbo:leaderName ?uri }
(-) How tall is Amazon Eve?PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?height WHERE { res:Amazon_Eve dbo:height ?height }
(-) Give me all Swedish oceanographers.
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { ?uri dbo:field res:Oceanography ; dbo:birthPlace res:Sweden }
(-) Who was buried in the Great Pyramid of Giza?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT ?uri WHERE { ?uri dbo:restingPlace dbr:Great_Pyramid_of_Giza }
(-) What did Bruce Carver die from?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Bruce_Carver dbo:deathCause ?uri }
(-) Which subsidiary of Lufthansa serves both Dortmund and Berlin Tegel?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Lufthansa dbo:subsidiary ?uri . ?uri dbo:targetAirport res:Dortmund_Airport ; dbo:targetAirport res:Berlin_Tegel_Airport }
(-) In which city does Sylvester Stallone live?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type dbo:City . res:Sylvester_Stallone dbo:residence ?uri }
(-) Give me all actors called Baldwin.
PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT DISTINCT ?uri WHERE { ?uri foaf:surname "Baldwin"@en { ?uri <http://dbpedia.org/ontology/occupation> <http://dbpedia.org/resource/Actor> } UNION { ?uri a <http://dbpedia.org/ontology/Actor> } }
(-) What is the ruling party in Lisbon?
SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Lisbon> <http://dbpedia.org/property/leaderParty> ?uri }
(-) In which U.S. state is Area 51 located?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT DISTINCT ?uri WHERE { res:Area_51 dbo:location ?uri . ?uri dbo:country res:United_States }
(-) What are the official languages of the Philippines?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Philippines dbo:officialLanguage ?uri }

---

## updated-qald-9-test

total 150  
answerd 127  
unanswerd 23  
errored 0

(-) Give me all American presidents of the last 20 years.
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbp: <http://dbpedia.org/property/> PREFIX dct: <http://purl.org/dc/terms/> PREFIX dbc: <http://dbpedia.org/resource/Category:> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type dbo:Person ; dct:subject dbc:Presidents_of_the_United_States ; dbo:activeYearsEndDate ?termEnd FILTER ( ( year(now()) - year(?termEnd) ) <= 20 ) }
(-) Which subsidiary of TUI Travel serves both Glasgow and Dublin?
SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/TUI_Travel> <http://dbpedia.org/ontology/subsidiary> ?uri . ?uri <http://dbpedia.org/ontology/targetAirport> <http://dbpedia.org/resource/Glasgow_International_Airport> ; <http://dbpedia.org/ontology/targetAirport> <http://dbpedia.org/resource/Dublin_Airport> }
(-) Give me all B-sides of the Ramones.
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX dbp: <http://dbpedia.org/property/> SELECT DISTINCT ?string WHERE { ?x dbo:musicalArtist res:Ramones ; dbo:bSide ?string }
(-) Butch Otter is the governor of which U.S. state?
SELECT DISTINCT ?uri WHERE { ?uri a <http://dbpedia.org/class/yago/WikicatStatesOfTheUnitedStates> ; <http://dbpedia.org/property/governor> <http://dbpedia.org/resource/Butch_Otter> }
(-) Who is the mayor of Berlin?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Berlin dbp:leader ?uri }
(-) Give me all professional skateboarders from Sweden.
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbp: <http://dbpedia.org/property/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { ?uri dbo:occupation dbr:Skateboarder { ?uri dbo:birthPlace dbr:Sweden } UNION { ?uri dbo:birthPlace ?place . ?place dbo:country dbr:Sweden } }
(-) Which monarchs of the United Kingdom were married to a German?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX yago: <http://dbpedia.org/class/yago/> PREFIX res: <http://dbpedia.org/resource/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type yago:WikicatMonarchsOfTheUnitedKingdom ; dbo:spouse ?spouse . ?spouse dbo:birthPlace res:Germany }
(-) Give me the homepage of Forbes.
PREFIX res: <http://dbpedia.org/resource/> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT DISTINCT ?string WHERE { res:Forbes foaf:homepage ?string }
(-) When did Finland join the EU?
PREFIX res: <http://dbpedia.org/resource/> PREFIX dbp: <http://dbpedia.org/property/> SELECT DISTINCT ?date WHERE { res:Finland dbp:accessioneudate ?date }
(-) Which computer scientist won an oscar?
SELECT DISTINCT ?uri WHERE { ?uri <http://dbpedia.org/ontology/field> <http://dbpedia.org/resource/Computer_science> ; <http://dbpedia.org/ontology/award> <http://dbpedia.org/resource/Academy_Award> }
(-) Which U.S. state has the highest population density?
SELECT ?uri WHERE { ?uri <http://dbpedia.org/ontology/country> <http://dbpedia.org/resource/United_States> ; <http://dbpedia.org/ontology/capital> ?capital ; <http://dbpedia.org/property/densityrank> ?density OPTIONAL { ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?string FILTER ( lang(?string) = "en" ) } } ORDER BY ASC(?density) LIMIT 1
(-) Which professional surfers were born in Australia?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { { ?uri dbo:occupation res:Surfer ; dbo:birthPlace res:Australia } UNION { ?uri dbo:occupation res:Surfer ; dbo:birthPlace ?place . ?place dbo:country res:Australia } }
(-) Sean Parnell was the governor of which U.S. state?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Sean_Parnell dbo:region ?uri }
(-) Through which countries does the Yenisei river flow?
PREFIX res: <http://dbpedia.org/resource/> PREFIX dbp: <http://dbpedia.org/property/> SELECT DISTINCT ?uri WHERE { res:Yenisei_River <http://dbpedia.org/ontology/country> ?uri }  
(-) Which companies work in the aerospace industry as well as in medicine?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { ?uri a dbo:Company ; dbo:industry dbr:Aerospace ; dbo:industry dbr:Medical }
(-) Which professional surfers were born on the Philippines?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX dbr: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { ?uri dbo:occupation res:Surfer ; dbo:birthPlace res:Philippines }
(-) Which countries are connected by the Rhine?
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX dbp: <http://dbpedia.org/property/> PREFIX dbo: <http://dbpedia.org/ontology/> SELECT DISTINCT ?uri WHERE { {<http://dbpedia.org/resource/Rhine> dbo:country ?uri } UNION {dbr:Rhine dbp:country ?uri} }
(-) Who was the father of Queen Elizabeth II?
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT \* WHERE { res:Elizabeth_II dbo:parent ?uri . ?uri <http://xmlns.com/foaf/0.1/gender> "male"@en }
(-) What are the names of the Teenage Mutant Ninja Turtles?
PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT DISTINCT ?s WHERE { <http://dbpedia.org/resource/Teenage_Mutant_Ninja_Turtles> <http://dbpedia.org/property/members> ?x . ?x foaf:givenName ?s }
(-) When did Paraguay proclaim its independence?
SELECT DISTINCT ?date WHERE { <http://dbpedia.org/resource/Paraguay> <http://dbpedia.org/ontology/foundingDate> ?date }
(-) Which U.S. state has the abbreviation MN?
SELECT DISTINCT ?uri WHERE { ?uri a yago:WikicatStatesOfTheUnitedStates ; <http://dbpedia.org/property/postalabbreviation> "MN"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> }
(-) Give me the official websites of actors of the television show Charmed.
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX onto: <http://dbpedia.org/ontology/> SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Charmed> onto:starring ?actors . ?actors foaf:homepage ?uri }
(-) Who was called Rodzilla?
SELECT DISTINCT ?uri WHERE { ?uri <http://xmlns.com/foaf/0.1/nick> "Rodzilla"@en }

---

## qald-9-train

total 408  
answered 396  
unanswered 12
errored 0

(-) Which monarchs were married to a German?  
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type dbo:Monarch ; dbo:spouse ?spouse { ?spouse dbo:birthPlace res:Germany } UNION { ?spouse dbo:birthPlace ?p . ?p dbo:country res:Germany } }
(-) Who is the daughter of Ingrid Bergman married to?  
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Ingrid*Bergman dbo:child ?child . ?child <http://dbpedia.org/property/spouse> ?uri FILTER(lang(?uri)='en')}
(-) How many employees of google are on DBpedia?  
SELECT DISTINCT ?num WHERE { <http://dbpedia.org/resource/Google> <http://dbpedia.org/ontology/numberOfEmployees> ?num }
(-) Which instruments does Cat Stevens play?  
SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Cat_Stevens> <http://dbpedia.org/ontology/instrument> ?uri }
(-) How heavy is Jupiter's lightest moon?  
SELECT DISTINCT ?n WHERE { ?uri <http://dbpedia.org/property/satelliteOf> <http://dbpedia.org/resource/Jupiter> ; <http://dbpedia.org/ontology/mass> ?n } ORDER BY ASC(?n) OFFSET 0 LIMIT 1
(-) List all episodes of the first season of the HBO television series The Sopranos!  
SELECT ?uri WHERE { ?uri <https://dbpedia.org/resource/The_Sopranos*(season_1)> <http://dbpedia.org/ontology/numberOfEpisodes> }
(-) Who is the owner of Facebook?  
SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Facebook,_Inc.> <http://dbpedia.org/property/owner> ?uri }
(-) Give me all cities in New Jersey with more than 100000 inhabitants.  
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX dbp: <http://dbpedia.org/property/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type dbo:City ; dbo:isPartOf res:New_Jersey ; dbo:populationTotal ?inhabitants FILTER ( ?inhabitants > 100000 ) }
(-) Who created Wikipedia?  
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Wikipedia dbo:author ?uri }
(-) In which country does the Nile start?  
PREFIX dbp: <http://dbpedia.org/property/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Nile dbp:source1Location ?uri }
(-) In which city did Nikos Kazantzakis die?  
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { res:Nikos_Kazantzakis dbo:deathPlace ?uri . ?uri rdf:type dbo:Town }
(-) Who composed the music for Harold and Maude?  
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Harold_and_Maude dbo:musicComposer ?uri }

---

## qald-9-test

total 150  
answered 138
unanswered 12
errored 0

(-) Give me the homepage of Forbes.  
PREFIX res: <http://dbpedia.org/resource/> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT DISTINCT ?string WHERE { res:Forbes foaf:homepage ?string }
(-) How many students does the Free University of Amsterdam have?  
SELECT DISTINCT ?num WHERE { dbr:Vrije_Universiteit_Amsterdam <http://dbpedia.org/ontology/numberOfStudents> ?num }
(-) Who created English Wikipedia?  
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX onto: <http://dbpedia.org/ontology/> SELECT ?uri WHERE { <http://dbpedia.org/resource/Wikipedia> onto:author ?uri }
(-) Which professional surfers were born on the Philippines?  
PREFIX dbr: <http://dbpedia.org/resource/> PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { ?uri dbo:occupation dbr:Surfer ; dbo:birthPlace res:Philippines }
(-) Give me all American presidents of the last 20 years.  
PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX dbp: <http://dbpedia.org/property/> PREFIX dct: <http://purl.org/dc/terms/> PREFIX dbc: <http://dbpedia.org/resource/Category:> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT DISTINCT ?uri WHERE { ?uri rdf:type dbo:Person ; dct:subject dbc:Presidents_of_the_United_States ; dbo:activeYearsEndDate ?termEnd FILTER ( ( year(now()) - year(?termEnd) ) <= 20 ) }
(-) Which subsidiary of TUI Travel serves both Glasgow and Dublin?  
SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/TUI_Travel> <http://dbpedia.org/ontology/subsidiary> ?uri . ?uri <http://dbpedia.org/ontology/targetAirport> <http://dbpedia.org/resource/Glasgow_International_Airport> ; <http://dbpedia.org/ontology/targetAirport> <http://dbpedia.org/resource/Dublin_Airport> }
(-) What are the names of the Teenage Mutant Ninja Turtles?  
PREFIX foaf:<http://xmlns.com/foaf/0.1/> SELECT DISTINCT ?s WHERE { <http://dbpedia.org/resource/Teenage_Mutant_Ninja_Turtles> <http://dbpedia.org/property/members> ?x . ?x foaf:givenName ?s }
(-) Which U.S. state has the abbreviation MN?  
SELECT DISTINCT ?uri WHERE { ?uri a yago:WikicatStatesOfTheUnitedStates ; <http://dbpedia.org/property/postalabbreviation> "MN"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> }
(-) Give me the official websites of actors of the television show Charmed.  
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX onto: <http://dbpedia.org/ontology/> SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Charmed> onto:starring ?actors . ?actors foaf:homepage ?uri }
(-) Who became president after JFK died?  
SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/John_F._Kennedy> <http://dbpedia.org/property/presidentEnd> ?x . ?uri <http://dbpedia.org/property/presidentStart> ?x; a <http://dbpedia.org/ontology/Person>. }  
(-) Which instruments does Cat Stevens play?  
SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Cat_Stevens> <http://dbpedia.org/ontology/instrument> ?uri }
(-) Who was called Rodzilla?  
SELECT DISTINCT ?uri WHERE { ?uri <http://xmlns.com/foaf/0.1/nick> "Rodzilla"@en }
