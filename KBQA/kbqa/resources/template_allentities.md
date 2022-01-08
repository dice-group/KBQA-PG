# Format

class_a; class_b; class_c; question; generator query;id

# http://dbpedia.org/ontology/Company

dbo:Company;;;Who is the founder of <A>?;SELECT DISTINCT ?uri where { <A> dbo:foundedBy ?uri};select distinct ?a where { ?a dbo:foundedBy ?uri};1
dbo:Company;;;Who founded <A>?;SELECT DISTINCT ?uri where { <A> dbo:foundedBy ?uri};select distinct ?a where { ?a dbo:foundedBy ?uri};2
dbo:Company;;;When was <A> founded?;SELECT DISTINCT ?uri where {<A> dbo:foundingYear ?uri};select distinct ?a where { ?a dbo:foundedYear ?uri};3
dbo:Company;;;In which city is <A>'s headquarters?;SELECT DISTINCT ?uri where {<A> dbo:headquarter ?headquarter. ?headquarter dbp:location ?uri};select distinct ?a where {?a dbo:headquarter ?headquarter. ?headquarter dbp:location ?uri};4
dbo:Company;;;In which industry is <A>?;SELECT DISTINCT ?uri where {<A> dbo:industry ?uri};select distinct ?a where {?a dbo:industry ?uri};5
dbo:Company;dbo:Company;;Is <A> a subsidiary of <B>?;ASK where { <A> dbo:parentCompany <B>};select distinct ?a, ?b {?a dbo:parentCompany ?b};6
dbo:Company;;;List all products from <A>.;SELECT DISTINCT ?uri where { <A> dbo:products ?uri};select distinct ?a where {?a dbo:products ?uri};7
dbo:Company;;;What is <A>'s annual revenue?;SELECT DISTINCT ?uri where { <A> dbo:revenue ?uri};select distinct ?a where {?a dbo:revenue ?uri};8

# http://dbpedia.org/ontology/Activity
dbo:Activity;;;What ball is used in <A>?;SELECT DISTINCT ?uri where {<A> dbp:ball ?uri};select distinct ?a where{ ?a dbp:ball ?uri};9
dbo:Activity;;;How large is the team size in <A>?;SELECT DISTINCT ?uri where {<A> dbo:teamSize ?uri};select distinct ?a where {?a dbo:teamSize ?uri};10 
dbo:Activity;;;How long is the playing time of <A>?;SELECT DISTINCT ?uri where {<A> dbp:playingTime ?uri};select distinct ?a where {?a dbp:playingTime ?uri};11

# http://dbpedia.org/ontology/Person
dbo:Person;;;<A> has how many relatives?;SELECT DISTINCT COUNT(?uri) where { <A> dbp:relatives ?uri };select distinct ?a where { ?a dbp:relatives ?uri };0823c2c40ec44ed38548274caa96984d
dbo:Person;;;<A> has won how many awards?;SELECT DISTINCT COUNT(?uri) where { <A> dbo:award ?uri };select distinct ?a where { ?a dbo:award ?uri };29513d9bf3fb453da72170be9f27bc0d
dbo:Person;;;<A> is from which city?;SELECT DISTINCT ?uri where { <A> dbo:hometown ?uri };select distinct ?a where { ?a dbo:hometown ?uri };1f283dc1bb87433d804608abb6d42fb9;
dbo:Person;;;Count the affiliations of <A>?;SELECT DISTINCT COUNT(?uri) where { <A> dbp:affiliation ?uri };select distinct ?a where { ?a dbp:affiliation ?uri };e18fd4075a914d4a8455c72375bdd4b9
dbo:Person;;;Count the different causes of death of <A>.;SELECT DISTINCT COUNT(?uri) where { ?x dbo:religion <A> . ?x dbo:deathCause ?uri };select distinct ?a where { ?x dbo:religion ?a . ?x dbo:deathCause ?uri };7fc3026611784ca68abe446d974bf7fb
dbo:Person;;;Did <A> did his highschool in <B>?;ASK where { <A> dbp:highSchool <B> };select distinct ?a, ?b where { ?a dbp:highSchool ?b };cbfdaaad592b4ef7b08d5ad4d0d0ac09
dbo:Person;;;Did <A> study at the <B> university?;ASK where { <A> dbp:university <B> };select distinct ?a, ?b where { ?a dbp:university ?b };e3a008c553da49fd876ece5a7c775750
dbo:Person;;;Did <A> study at the <B>?;ASK where { <A> dbo:institution <B> };select distinct ?a, ?b where { ?a dbo:institution ?b };d15fc086b4a342d0a45205ffd6963f8c
dbo:Person;;;Did <A> study at the <B>?;ASK where { <A> dbo:university <B> };select distinct ?a, ?b where { ?a dbo:university ?b };3ae2345e8e8844b1bcdc731a3b106eb9
dbo:Person;;;Did <A> study in <B>?;ASK where { <A> dbp:highSchool <B> };select distinct ?a, ?b where { ?a dbp:highSchool ?b };9c1ea109b00f4f5aba49d87f8fac3deb
dbo:Person;;;Did <A> study in the <B>?;ASK where { <A> dbo:institution <B> };select distinct ?a, ?b where { ?a dbo:institution ?b };bd015efa79cc4cf6ace73ea181c96abd
;dbo:Person;;Did <B> do his highschool in <A>?;ASK where { <B> dbp:highSchool <A> };select distinct ?a, ?b where { ?b dbp:highSchool ?a };0572e71a8200411493afdbc1072f5dc1
;dbo:Person;;Did <B> go to <A> studying?;ASK where { <B> dbo:university <A> };select distinct ?a, ?b where { ?b dbo:university ?a };988903c3f615471fbd0fe2adeafdd518
;dbo:Person;;Did <B> study at the <A>;ASK where { <B> dbo:institution <A> };select distinct ?a, ?b where { ?b dbo:institution ?a };b95b28576f18419c894ce4f86851e7c4
;dbo:Person;;Does <B> have a license of <A>?;ASK where { <B> dbp:license <A> };select distinct ?a, ?b where { ?b dbp:license ?a };d5927c0324be4e2d8fa01205bb38a09e
;dbo:Person;;Does <B> have the <A>?;ASK where { <B> dbp:license <A> };select distinct ?a, ?b where { ?b dbp:license ?a };97e02dcf44aa43c1b7cc7a7c155b118f
;dbo:Person;;Does <B> study <A>?;ASK where { <B> dbo:field <A> };select distinct ?a, ?b where { ?b dbo:field ?a };115415a95f22482aa6e5441ccf0b6f31
;dbo:Person;;Does <B> study <A>?;ASK where { <B> dbp:mainInterests <A> };select distinct ?a, ?b where { ?b dbp:mainInterests ?a };18e1b907a21644199bcf31fb9629f79c
dbo:Person;;;For how many things are <A> famous for?;SELECT DISTINCT COUNT(?uri) where { ?x dbp:placeOfBirth <A> . ?x dbo:knownFor ?uri };select distinct ?a where { ?x dbp:placeOfBirth ?a . ?x dbo:knownFor ?uri };a473965ed74b45298f4f8082bca57f56
dbo:Person;;;For what is <A> known ?;SELECT DISTINCT ?uri where { <A> dbp:knownFor ?uri };select distinct ?a where { ?a dbp:knownFor ?uri };841f3a4e3ade44b1b407f7b1382dc92a
dbo:Person;;;From where did the son of <A> graduate?;SELECT DISTINCT ?uri where { <A> dbo:child ?x . ?x dbp:almaMater ?uri };select distinct ?a where { ?a dbo:child ?x . ?x dbp:almaMater ?uri };ee83374553104e4784b6847dc658c510
dbo:Person;;;How did <A> died ?;SELECT DISTINCT ?uri where { <A> dbo:deathCause ?uri };select distinct ?a where { ?a dbo:deathCause ?uri };d47969ab783e4582a2e2fb7e0f0f5e8e
dbo:Person;;;How did the child of <A> die?;SELECT DISTINCT ?uri where { <A> dbo:child ?x . ?x dbo:deathCause ?uri };select distinct ?a where { ?a dbo:child ?x . ?x dbo:deathCause ?uri };f18825b526744c29b18f7b0a6dc10b80
dbo:Person;;;How many people are there whose children died in <A>?;SELECT DISTINCT COUNT(?uri) where { ?x dbo:deathPlace <A> . ?uri dbo:child ?x . ?uri a dbo:Person };select distinct ?a where { ?x dbo:deathPlace ?a . ?uri dbo:child ?x . ?uri a dbo:Person };bcf6d38828d24556aa001e0484100b31
dbo:Person;;;In how many places did <A> study?;SELECT DISTINCT COUNT(?uri) where { <A> dbp:almaMater ?uri . ?uri a dbo:University };select distinct ?a where { ?a dbp:almaMater ?uri . ?uri a dbo:University };229e4197d78f417ca569f31cb727d19d
dbo:Person;dbo:Person;;In which country did <B> and <A> die?;SELECT DISTINCT ?uri where { <B> dbp:placeOfDeath ?uri . <A> dbp:placeOfDeath ?uri };select distinct ?a, ?b where { ?b dbp:placeOfDeath ?uri . ?a dbp:placeOfDeath ?uri };be2d43507d27490580cef0ab4aca9355
dbo:Person;;;In which state does the university which is the alma mater of <A> lie?;SELECT DISTINCT ?uri where { <A> dbp:almaMater ?x . ?x dbp:state ?uri . ?x a dbo:University };select distinct ?a where { ?a dbp:almaMater ?x . ?x dbp:state ?uri . ?x a dbo:University };a8f9d6667ed44a89b9be3cf80a8d24c6
dbo:Person;dbo:Person;;In which university did <B> study, where <A> went too?;SELECT DISTINCT ?uri where { <B> dbo:almaMater ?uri . <A> dbo:almaMater ?uri };select distinct ?a, ?b where { ?b dbo:almaMater ?uri . ?a dbo:almaMater ?uri };930ba27955d9475587dbbb75ffcae399
dbo:Person;;;Is <A> buried in the <B>?;ASK where { <A> dbp:placeofburial <B> };select distinct ?a, ?b where { ?a dbp:placeofburial ?b };0f64ebf1ec944faa999a799ae051e373
;dbo:Person;;Is <B> buried in <A>?;ASK where { <B> dbp:placeofburial <A> };select distinct ?a, ?b where { ?b dbp:placeofburial ?a };1604b4deca8f4b089da3546474871043
dbo:Person;;;List all the children of <A>?;SELECT DISTINCT ?uri where { <A> dbp:children ?uri };select distinct ?a where { ?a dbp:children ?uri };7c78f74e4f404592838f82e9d563e6e0
dbo:Person;;;List down all notable works of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:notableWork ?uri };select distinct ?a where { ?a dbo:notableWork ?uri };89de2e9950be4d148cceb0f13606223d
dbo:Person;;;List the affiliation of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:affiliation ?uri };select distinct ?a where { ?a dbo:affiliation ?uri };b45a5663ebe3439a9c8032edaa8750b3
dbo:Person;;;List the affiliations of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:affiliations ?uri };select distinct ?a where { ?a dbp:affiliations ?uri };605df0ddfb63418781e9a290359006e5
dbo:Person;;;List the alma mater of the person who is wedded to <A>.;SELECT DISTINCT ?uri where { ?x dbo:spouse <A> . ?x dbp:almaMater ?uri };select distinct ?a where { ?x dbo:spouse ?a . ?x dbp:almaMater ?uri };888a87ee40884a92bb779b4a08e06f63
dbo:Person;;;List the awards given to the relatives of <A>.;SELECT DISTINCT ?uri where { <A> dbo:relative ?x . ?x dbo:award ?uri };select distinct ?a where { ?a dbo:relative ?x . ?x dbo:award ?uri };89b4110b9d064a0fb8feff6aa5aa2ff2
dbo:Person;;;List the awards received of the person whose child is <A>?;SELECT DISTINCT ?uri where { ?x dbp:children <A> . ?x dbo:award ?uri . ?x a dbo:Person };select distinct ?a where { ?x dbp:children ?a . ?x dbo:award ?uri . ?x a dbo:Person };ee1bccf6ccb7409e82df8306828de0c8
dbo:Person;;;List the awards won by the wife of <A>.;SELECT DISTINCT ?uri where { <A> dbp:spouse ?x . ?x dbp:awards ?uri };select distinct ?a where { ?a dbp:spouse ?x . ?x dbp:awards ?uri };ade7e2b4ed804a43a9a124fe2f3e4efc
dbo:Person;;;List the children of the parent of <A>.;SELECT DISTINCT ?uri where { <A> dbo:parent ?x . ?x dbp:children ?uri };select distinct ?a where { ?a dbo:parent ?x . ?x dbp:children ?uri };2145991e2562420284c8984b7f845228
dbo:Person;;;List the honorary title given to the spouse of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:spouse ?x . ?x dbo:award ?uri };select distinct ?a where { ?a dbp:spouse ?x . ?x dbo:award ?uri };3ab803a589804dd8b296cbe19777f8dc
dbo:Person;;;List the places where the relatives of <A> died ?;SELECT DISTINCT ?uri where { <A> dbp:relatives ?x . ?x dbo:deathPlace ?uri };select distinct ?a where { ?a dbp:relatives ?x . ?x dbo:deathPlace ?uri };6f35f83223854b9685bd0d658725f1a7
dbo:Person;;;List the relative of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:relative ?uri };select distinct ?a where { ?a dbo:relative ?uri };06661ab5e6804e1c8206072e2bb02395
dbo:Person;;;List the relatives of <A> ?;SELECT DISTINCT ?uri where { ?uri dbp:relatives <A> };select distinct ?a where { ?uri dbp:relatives ?a };f9b31b5201064d76b7f841959920c37f
dbo:Person;;;List the relatives of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:relatives ?uri };select distinct ?a where { ?a dbp:relatives ?uri };359b620b592a44929007db93e8aecd72
dbo:Person;;;List the relatives of the children of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:children ?x . ?x dbo:relative ?uri };select distinct ?a where { ?a dbp:children ?x . ?x dbo:relative ?uri };c7dbb6a48a8840779ff9be16709df500
dbo:Person;;;List the school of <A>?;SELECT DISTINCT ?uri where { <A> dbp:school ?uri };select distinct ?a where { ?a dbp:school ?uri };05e8ba378fa84157a0c3163e2e5a29bb
dbo:Person;;;List the things for which the relatives of <A> are known?;SELECT DISTINCT ?uri where { <A> dbo:relative ?x . ?x dbp:knownFor ?uri };select distinct ?a where { ?a dbo:relative ?x . ?x dbp:knownFor ?uri };3fbefd4c3d514688b85789042b0b5376
dbo:Person;;;Name a famous relative of <A>;SELECT DISTINCT ?uri where { ?uri dbo:relative <A> };select distinct ?a where { ?uri dbo:relative ?a };418aec71a0ad4d5594d5667a98921501
dbo:Person;;;Name the <A>'s school ?;SELECT DISTINCT ?uri where { <A> dbo:school ?uri };select distinct ?a where { ?a dbo:school ?uri };7acd068884a6483199c2fd7bdd37c988
dbo:Person;;;Name the alma mater of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:almaMater ?uri };select distinct ?a where { ?a dbo:almaMater ?uri };d87c7466bde24cb3a5fcc03dc0c210fe
dbo:Person;;;Name the alma mater of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:almaMater ?uri };select distinct ?a where { ?a dbo:almaMater ?uri };ec64691c6956449cb904adfc2f248e5e
dbo:Person;;;Name the cause of death of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:deathCause ?uri };select distinct ?a where { ?a dbo:deathCause ?uri };278a4dae43ef4c9b888aaf3f0516d0a0
dbo:Person;;;Name the college of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:college ?uri };select distinct ?a where { ?a dbp:college ?uri };b698642c0c4944baad539ca67412e78a
dbo:Person;;;Name the death location of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:deathPlace ?uri };select distinct ?a where { ?a dbp:deathPlace ?uri };9f44883aeb3c401c89e1465ab2006426
dbo:Person;;;Name the home town of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:hometown ?uri };select distinct ?a where { ?a dbo:hometown ?uri };e45dcefc54af4edbbb07b37331ca8f14
dbo:Person;;;Name the person whose child is <A>?;SELECT DISTINCT ?uri where { ?uri dbp:children <A> . ?uri a dbo:Person };select distinct ?a where { ?uri dbp:children ?a . ?uri a dbo:Person };135b3e40d914466e87cc236585e5a2ea
dbo:Person;dbo:Person;;Name the person whose daughter is <A> and also another children named <B> ?;SELECT DISTINCT ?uri where { ?uri dbo:child <A> . ?uri dbp:children <B> . ?uri a dbo:Person };select distinct ?a, ?b where { ?uri dbo:child ?a . ?uri dbp:children ?b . ?uri a dbo:Person };84a295da828b427a813fe17472240251
dbo:Person;dbo:Person;;Name the person whose mother name is <A> and has a son named <B>?;SELECT DISTINCT ?uri where { ?uri dbo:parent <A> . ?uri dbp:children <B> . ?uri a dbo:Person };select distinct ?a, ?b where { ?uri dbo:parent ?a . ?uri dbp:children ?b . ?uri a dbo:Person };fa685bca2d1949fd9aa9c98cb2200dfe
dbo:Person;;;Name the person whose parent is <A>?;SELECT DISTINCT ?uri where { ?uri dbo:parent <A> . ?uri a dbo:Person };select distinct ?a where { ?uri dbo:parent ?a . ?uri a dbo:Person };d50f136d62424735841bbbaf2f071598
dbo:Person;;;Name the resting place of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:restingplace ?uri };select distinct ?a where { ?a dbp:restingplace ?uri };20d4fbedbfba402298cd46213df4550e
dbo:Person;;;Name the university of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:university ?uri };select distinct ?a where { ?a dbp:university ?uri };f0185fa38b024eb1acf082b227049b42
dbo:Person;;;Tell me the school to which <A> went?;SELECT DISTINCT ?uri where { <A> dbp:education ?uri };select distinct ?a where { ?a dbp:education ?uri };cd0e2088c4334a499439865a4b8605d1
dbo:Person;;;To which educational institutions did <A> go for her studies?;SELECT DISTINCT ?uri where { <A> dbo:education ?uri };select distinct ?a where { ?a dbo:education ?uri };8533f08f0f2e439792341591e3b8d82e
dbo:Person;;;To which persons is <A> a relative?;SELECT DISTINCT ?uri where { ?uri dbp:relatives <A> . ?uri a dbo:Person };select distinct ?a where { ?uri dbp:relatives ?a . ?uri a dbo:Person };cec0cca9c76744ca97e1a9740254d40a
dbo:Person;dbo:Person;;Was <A> the mother of <B>?;ASK where { <B> dbp:mother <A> };select distinct ?a, ?b where { ?b dbp:mother ?a };4f1a4374cc27457faacbad707a9ca72f
;dbo:Person;;Was <B> born in <A>?;ASK where { <B> dbp:birthplace <A> };select distinct ?a, ?b where { ?b dbp:birthplace ?a };55fad74c2c62469581f58e7bbe60da52
dbo:Person;;;What  is the Nickname of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:nickname ?uri };select distinct ?a where { ?a dbp:nickname ?uri };a12c261c27154991801e5701a39bdc5b
dbo:Person;dbo:Person;;What are <A> and <B> both affiliated with?;SELECT DISTINCT ?uri where { <A> dbp:affiliation ?uri . <B> dbp:affiliation ?uri };select distinct ?a, ?b where { ?a dbp:affiliation ?uri . ?b dbp:affiliation ?uri };38c50543e2ca4c8ba2f11406ebb1f0c9
dbo:Person;;;What are some other children of the father of <A>?;SELECT DISTINCT ?uri where { ?x dbo:child <A> . ?x dbp:children ?uri };select distinct ?a where { ?x dbo:child ?a . ?x dbp:children ?uri };7fbcd4b51ed446329ea96a577f9cd906
dbo:Person;;;What are some relatives of the spouse of <A>?;SELECT DISTINCT ?uri where { ?x dbo:spouse <A> . ?uri dbo:relative ?x };select distinct ?a where { ?x dbo:spouse ?a . ?uri dbo:relative ?x };9e78a9d215f249178b9f58cab8cb0fd5
dbo:Person;;;What are the awards received by spouse of <A>?;SELECT DISTINCT ?uri where { ?x dbo:spouse <A> . ?x dbp:awards ?uri };select distinct ?a where { ?x dbo:spouse ?a . ?x dbp:awards ?uri };57b3533cb2b741e1a567c34b4ff71b21
dbo:Person;;;What are the notableworks of <A>?;SELECT DISTINCT ?uri where { <A> dbp:notableworks ?uri };select distinct ?a where { ?a dbp:notableworks ?uri };be9459f9eae64f38be49cf3573dc58c6
dbo:Person;;;What are the professions of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:occupation ?uri };select distinct ?a where { ?a dbp:occupation ?uri };8fcd17645d854494af5b6bbf9d11cc54
dbo:Person;;;What are the things <A> known for ?;SELECT DISTINCT ?uri where { <A> dbo:knownFor ?uri };select distinct ?a where { ?a dbo:knownFor ?uri };4988ef2fd0df4d35b243ffe31755c171
dbo:Person;;;What award was won by the father of <A>?;SELECT DISTINCT ?uri where { ?x dbp:children <A> . ?x dbo:award ?uri };select distinct ?a where { ?x dbp:children ?a . ?x dbo:award ?uri };6b9c942fcd1c48aba22c20b5693b249f
dbo:Person;;;what awards have been giving to <A>?;SELECT DISTINCT ?uri where { <A> dbo:award ?uri };select distinct ?a where { ?a dbo:award ?uri };cf3c2cbbbde94259a9b3d4194d90ac28
dbo:Person;dbo:Person;;What city gave birth to <B> and also houses <A>?;SELECT DISTINCT ?uri where { <B> dbo:birthPlace ?uri . <A> dbp:location ?uri };select distinct ?a, ?b where { ?b dbo:birthPlace ?uri . ?a dbp:location ?uri };38e4c90868ed468b94cb549c579f9b57
dbo:Person;;;What did <A>'s father die from?;SELECT DISTINCT ?uri where { ?x dbo:child <A> . ?x dbo:deathCause ?uri };select distinct ?a where { ?x dbo:child ?a . ?x dbo:deathCause ?uri };5fc0f9b047174d33bd4225a3d24e5f30
dbo:Person;dbo:Person;;What do <B> and <A> do for a living?;SELECT DISTINCT ?uri where { <A> dbo:occupation ?uri . <B> dbo:occupation ?uri };select distinct ?a, ?b where { ?a dbo:occupation ?uri . ?b dbo:occupation ?uri };86a47aa322204efb92fe728b58696cf5
dbo:Person;;;What does the famous relative of <A> do for a living?;SELECT DISTINCT ?uri where { ?x dbp:relatives <A> . ?x dbo:occupation ?uri };select distinct ?a where { ?x dbp:relatives ?a . ?x dbo:occupation ?uri };b9d3a2fe75124f64855ddc9e0f97e76d
dbo:Person;;;What faiths are followed by the relatives of <A>?;SELECT DISTINCT ?uri where { <A> dbo:relative ?x . ?x dbo:religion ?uri };select distinct ?a where { ?a dbo:relative ?x . ?x dbo:religion ?uri };6ede8437feee4a37a3076b1deb866abd
dbo:Person;;;What is <A> hometown ?;SELECT DISTINCT ?uri where { <A> dbp:hometown ?uri };select distinct ?a where { ?a dbp:hometown ?uri };30599ffcad334bcc8b320111644de813
dbo:Person;;;What is <A> known for?;SELECT DISTINCT ?uri where { <A> dbp:knownFor ?uri };select distinct ?a where { ?a dbp:knownFor ?uri };3a948631dd8441caa4bea0a1acc65d97
dbo:Person;;;What is the <A> associated with?;SELECT DISTINCT ?uri where { <A> dbp:affiliations ?uri };select distinct ?a where { ?a dbp:affiliations ?uri };d8830ee89d0547a7ba604e685fe17819
dbo:Person;;;What is the affiliation of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:affiliation ?uri };select distinct ?a where { ?a dbp:affiliation ?uri };53ffec1f77474312b866a1ef550836ec
dbo:Person;;;What is the alma mater of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:almaMater ?uri };select distinct ?a where { ?a dbp:almaMater ?uri };05f59024c9ca4d59bc0dd7c19ebdc90c
dbo:Person;dbo:Person;;What is the alma mater of <A> and <B>?;SELECT DISTINCT ?uri where { <A> dbo:college ?uri . <B> dbp:almaMater ?uri };select distinct ?a, ?b where { ?a dbo:college ?uri . ?b dbp:almaMater ?uri };a51285af64f54bbc8cc0e2548ad0b92f
dbo:Person;;;What is the alma mater of <A>?;SELECT DISTINCT ?uri where { <A> dbp:almaMater ?uri };select distinct ?a where { ?a dbp:almaMater ?uri };7383239e8ece464a80a8d5422d4ed3bc
dbo:Person;;;What is the alma mater of the person, whose child is <A>?;SELECT DISTINCT ?uri where { ?x dbp:children <A> . ?x dbp:almaMater ?uri };select distinct ?a where { ?x dbp:children ?a . ?x dbp:almaMater ?uri };428c921bdffa437cab0215a722628dc4
dbo:Person;;;What is the birth name  of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:birthName ?uri };select distinct ?a where { ?a dbp:birthName ?uri };3accaa813d154ec19e1d62b48eb60314
dbo:Person;;;What is the birth place of the children of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:children ?x . ?x dbo:birthPlace ?uri };select distinct ?a where { ?a dbp:children ?x . ?x dbo:birthPlace ?uri };720882e8f33e4b9a8d62b57e24b5c363
dbo:Person;dbo:Person;;What is the birthplace of <B> and <A> ?;SELECT DISTINCT ?uri where { <B> dbo:birthPlace ?uri . <A> dbo:birthPlace ?uri };select distinct ?a, ?b where { ?b dbo:birthPlace ?uri . ?a dbo:birthPlace ?uri };b5dca27ca03b43638ef8c6dddbd21693
dbo:Person;;;What is the burial place of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:placeOfBurial ?uri };select distinct ?a where { ?a dbp:placeOfBurial ?uri };88fe11d131e142dfa0952fca359787eb
dbo:Person;;;What is the career of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:occupation ?uri };select distinct ?a where { ?a dbo:occupation ?uri };3bf7d79605ca4456a79601a892b1ce3a
dbo:Person;;;What is the citizenship of <A>?;SELECT DISTINCT ?uri where { <A> dbo:citizenship ?uri };select distinct ?a where { ?a dbo:citizenship ?uri };c3949eda0f05470ca1d7effadac95392
dbo:Person;dbo:Person;;What is the city of the <B> is also the resting place of <A> ?;SELECT DISTINCT ?uri where { <B> dbo:authority ?uri . <A> dbp:restingplace ?uri };select distinct ?a, ?b where { ?b dbo:authority ?uri . ?a dbp:restingplace ?uri };6d79d046defe4cb683dddbf548a4dbc1
dbo:Person;dbo:Person;;What is the college of <A> is also the college of <B> ?;SELECT DISTINCT ?uri where { <A> dbo:college ?uri . <B> dbp:college ?uri };select distinct ?a, ?b where { ?a dbo:college ?uri . ?b dbp:college ?uri };edd475c6742c46fab9cff4f03715fdc2
dbo:Person;dbo:Person;;What is the common palce of study for <A> and <B> ?;SELECT DISTINCT ?uri where { <A> dbo:education ?uri . <B> dbp:education ?uri };select distinct ?a, ?b where { ?a dbo:education ?uri . ?b dbp:education ?uri };d0c96c44212d47e1b3ebd9752421d1f7
dbo:Person;dbo:Person;;What is the common religious affiliation of the <B> and that of  <A>?;SELECT DISTINCT ?uri where { <B> dbp:religiousAffiliation ?uri . <A> dbo:type ?uri };select distinct ?a, ?b where { ?b dbp:religiousAffiliation ?uri . ?a dbo:type ?uri };df803beedd644f2685bc04e7975727c4
dbo:Person;dbo:Person;;What is the common school of <B> and <A>?;SELECT DISTINCT ?uri where { <B> dbo:school ?uri . <A> dbo:almaMater ?uri };select distinct ?a, ?b where { ?b dbo:school ?uri . ?a dbo:almaMater ?uri };99e4d849107646e78dc70715e92b6f25
dbo:Person;dbo:Person;;What is the common university iof <A> and also the college of <B> ?;SELECT DISTINCT ?uri where { <A> dbo:university ?uri . <B> dbo:college ?uri };select distinct ?a, ?b where { ?a dbo:university ?uri . ?b dbo:college ?uri };f413c412b8084c02a0a9a82589b5c916
dbo:Person;dbo:Person;;What is the craft of the <B> which is also the profession of  <A> ?;SELECT DISTINCT ?uri where { <B> dbp:occupation ?uri . <A> dbo:profession ?uri };select distinct ?a, ?b where { ?b dbp:occupation ?uri . ?a dbo:profession ?uri };c2b204dc4fa14f0fa3e64b8a5e79c362
dbo:Person;;;What is the deathplace of whom who is the relative of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:relatives ?x . ?x dbo:deathPlace ?uri };select distinct ?a where { ?a dbp:relatives ?x . ?x dbo:deathPlace ?uri };96c1a8fa851c4e83b2444ba219f5352b
dbo:Person;;;What is the famous relative of <A> known for?;SELECT DISTINCT ?uri where { ?x dbp:relatives <A> . ?x dbp:knownFor ?uri };select distinct ?a where { ?x dbp:relatives ?a . ?x dbp:knownFor ?uri };7f3a0c2887a7423eb69732bbf1208c88
dbo:Person;;;What is the hometown of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:hometown ?uri };select distinct ?a where { ?a dbp:hometown ?uri };86f65bd1385144dfb07dd940f6dc77de
dbo:Person;dbo:Person;;What is the hometown of <A>, where <B> was born too?;SELECT DISTINCT ?uri where { <B> dbp:birthPlace ?uri . <A> dbo:hometown ?uri };select distinct ?a, ?b where { ?b dbp:birthPlace ?uri . ?a dbo:hometown ?uri };243f95d2144c4b2fadb5a18aa339bd98
dbo:Person;;;What is the nationality of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:nationality ?uri };select distinct ?a where { ?a dbp:nationality ?uri };7750fb1d95a7475ea49813b10023c2ed
dbo:Person;;;What is the nickname of the school where <A> studied  ?;SELECT DISTINCT ?uri where { <A> dbp:highschool ?x . ?x dbp:nickname ?uri . ?x a dbo:School };select distinct ?a where { ?a dbp:highschool ?x . ?x dbp:nickname ?uri . ?x a dbo:School };bb90c58c414a4f819154ecb33586121d
dbo:Person;;;What is the place of birth of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:placeOfBirth ?uri };select distinct ?a where { ?a dbp:placeOfBirth ?uri };5ac4dc8f112e464796c31164eb0f3a64
dbo:Person;dbo:Person;;What is the place of birth of the <A> which is also the  place of death of the <B>;SELECT DISTINCT ?uri where { <A> dbp:placeOfBirth ?uri . <B> dbo:deathPlace ?uri };select distinct ?a, ?b where { ?a dbp:placeOfBirth ?uri . ?b dbo:deathPlace ?uri };0753a6cc55e24b9f8ae248cb0229faf0
dbo:Person;dbo:Person;;What is the place of birth of the <B> and <A>;SELECT DISTINCT ?uri where { <B> dbp:placeOfBirth ?uri . <A> dbp:placeOfBirth ?uri };select distinct ?a, ?b where { ?b dbp:placeOfBirth ?uri . ?a dbp:placeOfBirth ?uri };8a98295e35f9472fbc9b9d7ebb99de74
dbo:Person;;;What is the place of death of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:placeOfDeath ?uri };select distinct ?a where { ?a dbp:placeOfDeath ?uri };f22fef56a0c84c86886dc2dc2243a721
dbo:Person;;;What is the profession of the children of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:children ?x . ?x dbo:profession ?uri };select distinct ?a where { ?a dbp:children ?x . ?x dbo:profession ?uri };affc959256ac4bc191e5dd85460f6a12
dbo:Person;;;What is the religious affiliation of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:religiousAffiliation ?uri };select distinct ?a where { ?a dbp:religiousAffiliation ?uri };418dfe53e2ba43708a7884f5047d9093
dbo:Person;;;What is the religious affiliation of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:religiousAffiliation ?uri };select distinct ?a where { ?a dbp:religiousAffiliation ?uri };b846e29b2bb74db29610cdbbbc7b1740
dbo:Person;;;What is the resting place of the child of <A>?;SELECT DISTINCT ?uri where { <A> dbp:children ?x . ?x dbo:restingPlace ?uri };select distinct ?a where { ?a dbp:children ?x . ?x dbo:restingPlace ?uri };bcaaf472d03649a3b3fe0f04e625219d
dbo:Person;;;What is the resting place of the children of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:children ?x . ?x dbo:restingPlace ?uri };select distinct ?a where { ?a dbp:children ?x . ?x dbo:restingPlace ?uri };e7550728ad6f41acb0ad81d2f95ffb96
dbo:Person;dbo:Person;;What killed <B> and <A>?;SELECT DISTINCT ?uri where { <B> dbo:deathCause ?uri . <A> dbo:deathCause ?uri };select distinct ?a, ?b where { ?b dbo:deathCause ?uri . ?a dbo:deathCause ?uri };a66454f689bf4ec393eef188c8ea0fb6
dbo:Person;dbo:Person;;What made <A> and <B> both famous?;SELECT DISTINCT ?uri where { <A> dbo:knownFor ?uri . <B> dbo:knownFor ?uri };select distinct ?a, ?b where { ?a dbo:knownFor ?uri . ?b dbo:knownFor ?uri };62e9fa82eea7498790e2d5ca5a664a60
dbo:Person;dbo:Person;;What made <A> and <B> famous?;SELECT DISTINCT ?uri where { <A> dbo:field ?uri . <B> dbo:knownFor ?uri };select distinct ?a, ?b where { ?a dbo:field ?uri . ?b dbo:knownFor ?uri };cad47dbadca34d12a26f9f492cee5f29
dbo:Person;;;What prizes have been awarded to the relatives of <A>?;SELECT DISTINCT ?uri where { <A> dbp:relatives ?x . ?x dbp:awards ?uri };select distinct ?a where { ?a dbp:relatives ?x . ?x dbp:awards ?uri };76979737099748f4a8ec2329b9f2a7f0
dbo:Person;;;What was founded by <A> ?;SELECT DISTINCT ?uri where { <A> dbp:founded ?uri };select distinct ?a where { ?a dbp:founded ?uri };b39e52f81f1a4c8db50b35e3a82ebb1d
dbo:Person;;;What were the occupations of <A>?;SELECT DISTINCT ?uri where { <A> dbo:occupation ?uri };select distinct ?a where { ?a dbo:occupation ?uri };a882c7c530ad4e7793896fce0ad1adef
dbo:Person;;;When did <A> die?;SELECT DISTINCT ?uri where { <A> dbp:deathDate ?uri };select distinct ?a where { ?a dbp:deathDate ?uri };51d0d9be06c244229efab43ae8e9d45d
dbo:Person;dbo:Person;;Where are <A> and <B> buried?;SELECT DISTINCT ?uri where { <A> dbp:restingplace ?uri . <B> dbp:restingplace ?uri };select distinct ?a, ?b where { ?a dbp:restingplace ?uri . ?b dbp:restingplace ?uri };b1d14746b41f47459edf2a268414687f
dbo:Person;dbo:Person;;Where are the burial grounds of <B> and <A>?;SELECT DISTINCT ?uri where { <B> dbp:restingplace ?uri . <A> dbp:restingplace ?uri };select distinct ?a, ?b where { ?b dbp:restingplace ?uri . ?a dbp:restingplace ?uri };fe825b7ea80045f19a498f490eb78420
dbo:Person;;;Where did <A> die ?;SELECT DISTINCT ?uri where { <A> dbp:deathPlace ?uri };select distinct ?a where { ?a dbp:deathPlace ?uri };32d100aad346478bbb68b3ce1b5a8520
dbo:Person;;;Where did <A> do his elementary schooling?;SELECT DISTINCT ?uri where { <A> dbp:highSchool ?uri };select distinct ?a where { ?a dbp:highSchool ?uri };321d971403c844f7b7233e28728d227e
dbo:Person;;;Where did <A> do his highschool?;SELECT DISTINCT ?uri where { <A> dbp:highschool ?uri };select distinct ?a where { ?a dbp:highschool ?uri };2704d889b6c741ef8e45357f8e71bbdb
dbo:Person;;;Where did <A> go to high school;SELECT DISTINCT ?uri where { <A> dbo:highschool ?uri };select distinct ?a where { ?a dbo:highschool ?uri };1088fd5c6f2948faa4ca297bf58ca3eb
dbo:Person;;;Where did <A> graduated ?;SELECT DISTINCT ?uri where { <A> dbo:education ?uri };select distinct ?a where { ?a dbo:education ?uri };4c49002c50c740b69b9e310bb96d4c13
dbo:Person;;;Where did <A> study?;SELECT DISTINCT ?uri where { <A> dbo:almaMater ?uri };select distinct ?a where { ?a dbo:almaMater ?uri };44b54ea88b4c437bbca297ca3c04a6d3
dbo:Person;dbo:Person;;Where did <B> and <A> both die?;SELECT DISTINCT ?uri where { <A> dbp:deathPlace ?uri . <B> dbp:deathPlace ?uri };select distinct ?a, ?b where { ?a dbp:deathPlace ?uri . ?b dbp:deathPlace ?uri };f86382f06edd4519acfc00e730f5471e
dbo:Person;dbo:Person;;Where did <B> and <A> die?;SELECT DISTINCT ?uri where { <B> dbp:placeOfDeath ?uri . <A> dbp:deathPlace ?uri };select distinct ?a, ?b where { ?b dbp:placeOfDeath ?uri . ?a dbp:deathPlace ?uri };5953c1ca741b4952bfa7231396751599
dbo:Person;dbo:Person;;Where did <B> and <A> study?;SELECT DISTINCT ?uri where { <A> dbp:almaMater ?uri . <B> dbo:almaMater ?uri };select distinct ?a, ?b where { ?a dbp:almaMater ?uri . ?b dbo:almaMater ?uri };7bc28b110ed544cc8e98bdcf752d9c47
dbo:Person;;;Where did the partner of <A> die?;SELECT DISTINCT ?uri where { <A> dbp:spouse ?x . ?x dbo:deathPlace ?uri };select distinct ?a where { ?a dbp:spouse ?x . ?x dbo:deathPlace ?uri };d03cf8ab9ba54ead94c0ab2b0355b918
dbo:Person;;;Where did the relatives of <A> study?;SELECT DISTINCT ?uri where { ?x dbo:relative <A> . ?x dbp:education ?uri };select distinct ?a where { ?x dbo:relative ?a . ?x dbp:education ?uri };6b5ad23d383444478ce3e8e1acbbc649
dbo:Person;;;Where did the relatives of <A> study?;SELECT DISTINCT ?uri where { ?x dbo:relation <A> . ?x dbp:almaMater ?uri };select distinct ?a where { ?x dbo:relation ?a . ?x dbp:almaMater ?uri };bd4cb94b69084d79b0d1feb1fc8b014d
dbo:Person;;;Where did the spouse of <A> die?;SELECT DISTINCT ?uri where { ?x dbp:spouse <A> . ?x dbo:deathPlace ?uri };select distinct ?a where { ?x dbp:spouse ?a . ?x dbo:deathPlace ?uri };46880d365fbe4d54b1b965e5b5e1bb77
dbo:Person;dbo:Person;;Where do <A> and <B> both live?;SELECT DISTINCT ?uri where { <A> dbo:residence ?uri . <B> dbo:residence ?uri };select distinct ?a, ?b where { ?a dbo:residence ?uri . ?b dbo:residence ?uri };eb285e418d9641bcb6ba0c86c444d355
dbo:Person;;;Where do <A> live?;SELECT DISTINCT ?uri where { ?x dbp:almaMater <A> . ?x dbo:residence ?uri };select distinct ?a where { ?x dbp:almaMater ?a . ?x dbo:residence ?uri };fc455f282c6549adaa1614637ae68991
dbo:Person;;;Where does <A> work?;SELECT DISTINCT ?uri where { <A> dbp:office ?uri };select distinct ?a where { ?a dbp:office ?uri };0c2db5b405ac48dcb16b0ce50df877d1
dbo:Person;dbo:Person;;Where does <B> and <A> both live?;SELECT DISTINCT ?uri where { <A> dbp:residence ?uri . <B> dbp:residence ?uri };select distinct ?a, ?b where { ?a dbp:residence ?uri . ?b dbp:residence ?uri };ab981f539cf94ceea0c6ca6ddf8f673d
dbo:Person;;;Where is <A> from?;SELECT DISTINCT ?uri where { <A> dbo:stateOfOrigin ?uri };select distinct ?a where { ?a dbo:stateOfOrigin ?uri };a0cdc0611f2c4b879e0205a8d1f477ba
dbo:Person;;;Where is <A> from?;SELECT DISTINCT ?uri where { <A> dbo:nationality ?uri };select distinct ?a where { ?a dbo:nationality ?uri };d492192a5490409c9eedf51d1e09b74b
dbo:Person;;;Where is the birthplace of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:birthplace ?uri };select distinct ?a where { ?a dbp:birthplace ?uri };39562e37dcd645e8aa5d083018173381
dbo:Person;;;Where is the grave of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:placeOfBurial ?uri };select distinct ?a where { ?a dbp:placeOfBurial ?uri };3aaf4525a6d24e27be8fe037d5ba28c2
dbo:Person;;;Where is the hometown of <A>?;SELECT DISTINCT ?uri where { <A> dbo:hometown ?uri };select distinct ?a where { ?a dbo:hometown ?uri };3f8ac10edaaa4c4cbbde422c79de3c6d
dbo:Person;;;Where is the spouse of <A> buried?;SELECT DISTINCT ?uri where { ?x dbo:spouse <A> . ?x dbp:placeOfBurial ?uri };select distinct ?a where { ?x dbo:spouse ?a . ?x dbp:placeOfBurial ?uri };b38a612b13ec49d4b8be8365b8a0d89b
dbo:Person;;;Where is the tomb of son of <A>?;SELECT DISTINCT ?uri where { ?x dbo:parent <A> . ?x dbo:restingPlace ?uri };select distinct ?a where { ?x dbo:parent ?a . ?x dbo:restingPlace ?uri };e3f73674fbdd41a38021d60204f7196f
dbo:Person;;;Where is the tombstone of <A>?;SELECT DISTINCT ?uri where { <A> dbp:restingplace ?uri };select distinct ?a where { ?a dbp:restingplace ?uri };7c5f3af257f34d6fa8ea63202db67648
dbo:Person;;;Where was <A> born ?;SELECT DISTINCT ?uri where { <A> dbp:birthplace ?uri };select distinct ?a where { ?a dbp:birthplace ?uri };aca36b0993ba45edb0f0fc957c97ce23
dbo:Person;;;Where was <A> buried ?;SELECT DISTINCT ?uri where { <A> dbp:placeOfBurial ?uri };select distinct ?a where { ?a dbp:placeOfBurial ?uri };e83b9ec4abef418585e8a76f2dae15f4
dbo:Person;;;Where was <A> laid to rest?;SELECT DISTINCT ?uri where { <A> dbo:placeOfBurial ?uri };select distinct ?a where { ?a dbp:placeOfBurial ?uri };311bb63ae12d4dd999e195d827cf60d2
dbo:Person;dbo:Person;;Where were <B> and <A> born?;SELECT DISTINCT ?uri where { <B> dbp:birthPlace ?uri . <A> dbo:birthPlace ?uri };select distinct ?a, ?b where { ?b dbp:birthPlace ?uri . ?a dbo:birthPlace ?uri };18b1a0fcbd154906ad63f1310bcb8356
dbo:Person;;;which award has been won by <A>?;SELECT DISTINCT ?uri where { <A> dbp:title ?uri };select distinct ?a where { ?a dbp:title ?uri };169a1ce1f8ac4c5ba9a92103237113c6
dbo:Person;;;Which awards did the children of <A> won ?;SELECT DISTINCT ?uri where { <A> dbp:children ?x . ?x dbp:awards ?uri };select distinct ?a where { ?a dbp:children ?x . ?x dbp:awards ?uri };db5d49f80c774b80beb208bc62050aca
dbo:Person;;;Which awards did the parents of <A> win ?;SELECT DISTINCT ?uri where { <A> dbo:parent ?x . ?x dbp:awards ?uri };select distinct ?a where { ?a dbo:parent ?x . ?x dbp:awards ?uri };baf5c96273684029beba9ba7d893203e
dbo:Person;;;Which awards have <A> won?;SELECT DISTINCT ?uri where { <A> dbp:awards ?uri };select distinct ?a where { ?a dbp:awards ?uri };f107cdaf5a3b4793ad0a9ba36ca5c01c
dbo:Person;dbo:Person;;Which college has been attended  by both Mr. <B> and Mr. <A>?;SELECT DISTINCT ?uri where { <B> dbo:college ?uri . <A> dbo:college ?uri };select distinct ?a, ?b where { ?b dbo:college ?uri . ?a dbo:college ?uri };90502631e5e7485cb032ce25c7048d48
dbo:Person;dbo:Person;;Which college of <A> is the alma mater of <B>;SELECT DISTINCT ?uri where { <A> dbp:college ?uri . <B> dbp:almaMater ?uri };select distinct ?a, ?b where { ?a dbp:college ?uri . ?b dbp:almaMater ?uri };0645d71c51664c7f98ef83d258d24c5d
dbo:Person;dbo:Person;;Which college of the <A> is the alma mater of the <B> ?;SELECT DISTINCT ?uri where { <A> dbp:college ?uri . <B> dbo:almaMater ?uri };select distinct ?a, ?b where { ?a dbp:college ?uri . ?b dbo:almaMater ?uri };f06758ad9c714bf490f784dcceb3ba90
dbo:Person;dbo:Person;;Which home town of <A> is the death location of the <B> ?;SELECT DISTINCT ?uri where { <A> dbp:hometown ?uri . <B> dbo:deathPlace ?uri };select distinct ?a, ?b where { ?a dbp:hometown ?uri . ?b dbo:deathPlace ?uri };a899e312823543e7b728a2517d29392d
dbo:Person;dbo:Person;;Which home town of <A> is the place of death of <B> ?;SELECT DISTINCT ?uri where { <A> dbo:hometown ?uri . <B> dbp:placeOfDeath ?uri };select distinct ?a, ?b where { ?a dbo:hometown ?uri . ?b dbp:placeOfDeath ?uri };22eeb146aa1f41a4b0db6df5844b3fed
dbo:Person;;;Which school did <A> attend?;SELECT DISTINCT ?uri where { <A> dbp:school ?uri };select distinct ?a where { ?a dbp:school ?uri };d6aaeb41aef44a8b8bffd1a5e90e3d16
;;;Which sports are played in the alma mater of <A>?;SELECT DISTINCT ?uri where { <A> dbp:almaMater ?x . ?x dbo:sport ?uri };select distinct ?a where { ?a dbp:almaMater ?x . ?x dbo:sport ?uri };802bb417e72d4d8a9cb37d8136a0ae07
;;;Which sports are played in the alma mater of <A>?;SELECT DISTINCT ?uri where { <A> dbp:almaMater ?x . ?x dbo:sport ?uri };select distinct ?a where { ?a dbp:almaMater ?x . ?x dbo:sport ?uri };98482e0e16ea482f9030d6b2d9cb000f
dbo:Person;dbo:Person;;Which spouse of <A> a mother named <B> ?;SELECT DISTINCT ?uri where { ?uri dbo:parent <B> . ?uri dbo:spouse <A> };select distinct ?a, ?b where { ?uri dbo:parent ?b . ?uri dbo:spouse ?a };17f767e9a51b4a3d935fa194d0de2f8d
dbo:Person;;;Which things are <A> known for ?;SELECT DISTINCT ?uri where { <A> dbp:knownFor ?uri };select distinct ?a where { ?a dbp:knownFor ?uri };4423f1c8b04e4c438c50790d4c60c722
dbo:Person;;;Which uni did <A> attend ?;SELECT DISTINCT ?uri where { <A> dbp:education ?uri };select distinct ?a where { ?a dbp:education ?uri };2d2934c87b0e4eefa554db84e9abe251
dbo:Person;;;Which university is alma mater to <A>?;SELECT DISTINCT ?uri where { <A> dbp:university ?uri };select distinct ?a where { ?a dbp:university ?uri };d2698d17b3fc4da3b3a659d38d722a13
dbo:Person;dbo:Person;;Which university was attended by both <B> and <A>?;SELECT DISTINCT ?uri where { <B> dbp:education ?uri . <A> dbp:education ?uri };select distinct ?a, ?b where { ?b dbp:education ?uri . ?a dbp:education ?uri };ba2570473e36467c8a631f60944cd2bd
dbo:Person;dbo:Person;;Who are relatives of <A> and <B>?;SELECT DISTINCT ?uri where { ?uri dbp:relatives <A> . ?uri dbp:relatives <B> };select distinct ?a, ?b where { ?uri dbp:relatives ?a . ?uri dbp:relatives ?b };6cb6c4470ec840f9990494c4ecebca5f
dbo:Person;;;Who are the children of <A>?;SELECT DISTINCT ?uri where { <A> dbp:children ?uri };select distinct ?a where { ?a dbp:children ?uri };4ffdaa76aa994139b18edf277f905fed
dbo:Person;dbo:Person;;Who are the parents of  <A> and <B>?;SELECT DISTINCT ?uri where { ?uri dbo:child <A> . ?uri dbo:child <B> };select distinct ?a, ?b where { ?uri dbo:child ?a . ?uri dbo:child ?b };db1c3fdf8d784274b4e27db7dd62b263
dbo:Person;;;Who are the spouse of the parents of <A>?;SELECT DISTINCT ?uri where { <A> dbo:parent ?x . ?x dbo:spouse ?uri };select distinct ?a where { ?a dbo:parent ?x . ?x dbo:spouse ?uri };5574fe2aa59d4b4394e830d098886f3c
dbo:Person;;;Who did <A> marry?;SELECT DISTINCT ?uri where { ?uri dbo:spouse <A> };select distinct ?a where { ?uri dbo:spouse ?a };4b249c6c2fef48e889eb99914a430034
dbo:Person;dbo:Person;;Who has <A> and <B> as relatives?;SELECT DISTINCT ?uri where { ?uri dbo:relative <A> . ?uri dbo:relative <B> };select distinct ?a, ?b where { ?uri dbo:relative ?a . ?uri dbo:relative ?b };c29965dde83947ffa5b1a736dd8ea8bf
dbo:Person;;;Who has a  child named <A> and is resting place as <B>?;SELECT DISTINCT ?uri where { ?uri dbp:children <A> . ?uri dbp:restingPlace <B> };select distinct ?a, ?b where { ?uri dbp:children ?a . ?uri dbp:restingPlace ?b };cf382df024a340a4876a4c3651d44937
dbo:Person;dbo:Person;;Who has been married to both <A> and <B>?;SELECT DISTINCT ?uri where { <A> dbo:spouse ?uri . <B> dbo:spouse ?uri };select distinct ?a, ?b where { ?a dbo:spouse ?uri . ?b dbo:spouse ?uri };3dfd41b5ba22435eb756a1d2034d0ce6
dbo:Person;dbo:Person;;Who have children named <B> and <A>?;SELECT DISTINCT ?uri where { ?uri dbp:children <B> . ?uri dbp:children <A> };select distinct ?a, ?b where { ?uri dbp:children ?b . ?uri dbp:children ?a };73ba87c4b9fb40ee968f00a20022e04f
dbo:Person;dbo:Person;;Who is  related to <A> and <B>?;SELECT DISTINCT ?uri where { ?uri dbp:relatives <A> . ?uri dbp:relatives <B> };select distinct ?a, ?b where { ?uri dbp:relatives ?a . ?uri dbp:relatives ?b };53694c0e5c2548419756478331137c13
dbo:Person;;;Who is a famous relative of <A>?;SELECT DISTINCT ?uri where { ?uri dbo:relative <A> . ?uri a dbo:Person };select distinct ?a where { ?uri dbo:relative ?a . ?uri a dbo:Person };dc1d2cb750ca4e2e9f9a74ccd1c6c5cc
dbo:Person;;;Who is child of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:children ?uri };select distinct ?a where { ?a dbp:children ?uri };fd40821f1b1c4243bc23ef7f91268311
dbo:Person;;;Who is married to <A>?;SELECT DISTINCT ?uri where { ?uri dbp:spouse <A> };select distinct ?a where { ?uri dbp:spouse ?a };6adadd03b3254e5386b3c4bd1680b99d
dbo:Person;;;Who is married to a <A>?;SELECT DISTINCT ?uri where { ?x dbp:title <A> . ?uri dbp:spouse ?x };select distinct ?a where { ?x dbp:title ?a . ?uri dbp:spouse ?x };1f8f6352c2c54ce3b53aba360323d3ed
dbo:Person;;;Who is relative of the people died in <A> ?;SELECT DISTINCT ?uri where { ?x dbp:deathPlace <A> . ?x dbo:relative ?uri };select distinct ?a where { ?x dbp:deathPlace ?a . ?x dbo:relative ?uri };fdc1a6168b3544c294fcb5c5d4bd3de5
dbo:Person;;;Who is the child of <A>?;SELECT DISTINCT ?uri where { <A> dbo:child ?uri };select distinct ?a where { ?a dbo:child ?uri };922da121de7d4c2b94f5704844a63b18
dbo:Person;dbo:Person;;Who is the common parent of <B> and <A> ?;SELECT DISTINCT ?uri where { <B> dbo:parentOrganisation ?uri . <A> dbp:parent ?uri };select distinct ?a, ?b where { ?b dbo:parentOrganisation ?uri . ?a dbp:parent ?uri };b0d14b766ec544f7b6027a2ff2c21705
dbo:Person;;;Who is the employer of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:employer ?uri };select distinct ?a where { ?a dbp:employer ?uri };5347e3d7e51348bb814413a5707b97f3
dbo:Person;;;Who is the famous relative of <A>?;SELECT DISTINCT ?uri where { ?uri dbp:relatives <A> };select distinct ?a where { ?uri dbp:relatives ?a };d8afce1fd4aa4a2580832293b1d0d318
dbo:Person;;;Who is the father of <A>?;SELECT DISTINCT ?uri where { ?uri dbo:child <A> };select distinct ?a where { ?uri dbo:child ?a };8ff0158616ba4528a7ed38a4e45df6bf
dbo:Person;;;Who is the former partner of <A> ?;SELECT DISTINCT ?uri where { <A> dbo:formerPartner ?uri };select distinct ?a where { ?a dbo:formerPartner ?uri };d742a7e01f4c4ee48d60d542ecc2fb42
dbo:Person;;;who is the husband of <A>?;SELECT DISTINCT ?uri where { <A> dbo:partner ?uri };select distinct ?a where { ?a dbo:partner ?uri };6239f50c40b045fb92f0ad0b63792e7b
dbo:Person;;;Who is the parent of <A>?;SELECT DISTINCT ?uri where { ?uri dbp:children <A> };select distinct ?a where { ?uri dbp:children ?a };7f7c3328eb5b44fd9119c85b39285fbf
dbo:Person;;;Who is the partner of <A>?;SELECT DISTINCT ?uri where { ?uri dbp:partner <A> };select distinct ?a where { ?uri dbp:partner ?a };51484b4dd82e47e9838bd6ae4d77c67a
dbo:Person;;;Who is the person whose child performed with <A>?;SELECT DISTINCT ?uri where { ?x dbp:associatedActs <A> . ?uri dbo:child ?x };select distinct ?a where { ?x dbp:associatedActs ?a . ?uri dbo:child ?x };390c756eecd94acfb6335abcaa91832a
dbo:Person;;;Who is the relative of <A> ?;SELECT DISTINCT ?uri where { <A> dbp:relatives ?uri };select distinct ?a where { ?a dbp:relatives ?uri };069c73f4c6c84f3b8bed56b9f7dd229d
dbo:Person;;;Who is the spouse of <A>?;SELECT DISTINCT ?uri where { ?uri dbp:spouse <A> };select distinct ?a where { ?uri dbp:spouse ?a };1f0f16883a764370b8cb9aae06e6d527
dbo:Person;;;who married <A>?;SELECT DISTINCT ?uri where { ?uri dbp:spouse <A> };select distinct ?a where { ?uri dbp:spouse ?a };13fab3852bd645ef8d7c43e3d10a9d2b
dbo:Person;;;Who was the parent of person whose child is <A>?;SELECT DISTINCT ?uri where { ?x dbp:children <A> . ?x dbo:parent ?uri . ?x a dbo:Person };select distinct ?a where { ?x dbp:children ?a . ?x dbo:parent ?uri . ?x a dbo:Person };ce1c25a295524cd3ad8096741360c0a5
dbo:Person;;;Whos a famous relative of <A>?;SELECT DISTINCT ?uri where { ?uri dbo:relation <A> };select distinct ?a where { ?uri dbo:relation ?a };815d064630b3451baa5acb5bedd5e7ad
dbo:Person;;;Whose children are married to <A>?;SELECT DISTINCT ?uri where { ?x dbp:spouse <A> . ?uri dbp:children ?x };select distinct ?a where { ?x dbp:spouse ?a . ?uri dbp:children ?x };57f94e194bbf47d2bc8df0b967c56d74
dbo:Person;;;Whose children died in <A>?;SELECT DISTINCT ?uri where { ?x dbo:deathPlace <A> . ?uri dbo:child ?x };select distinct ?a where { ?x dbo:deathPlace ?a . ?uri dbo:child ?x };db0ceedbcf0e4e1ca708191b92dc2b59
dbo:Person;;;Whose mom is <A>?;SELECT DISTINCT ?uri where { ?uri dbp:mother <A> };select distinct ?a where { ?uri dbp:mother ?a };3230de5fe63a44debe27de6c25e6aedf
dbo:Person;dbo:Person;;Whose relatives are <A> and <B>?;SELECT DISTINCT ?uri where { ?uri dbo:relative <A> . ?uri dbo:relative <B> };select distinct ?a, ?b where { ?uri dbo:relative ?a . ?uri dbo:relative ?b };69451801bb474b41ae95ff1273c0b4d2
;dbo:Person;;Whose resting place is <A> and has kids named <B>?;SELECT DISTINCT ?uri where { ?uri dbp:restingplace <A> . ?uri dbo:child <B> };select distinct ?a, ?b where { ?uri dbp:restingplace ?a . ?uri dbo:child ?b };79debf2d75fe4c2c9651c15e18116af1
dbo:Person;dbo:Person;;Why did <A> and <B> die?;SELECT DISTINCT ?uri where { <A> dbo:deathCause ?uri . <B> dbp:deathCause ?uri };select distinct ?a, ?b where { ?a dbo:deathCause ?uri . ?b dbp:deathCause ?uri };7d39f4c231f744dfb4e0f7f5f4f15b7f

# http://dbpedia.org/ontology/Actor

SELECT DISTINCT ?a where {?a gold:hypernym dbr:Actor}

dbr:Actor;;;When did <A> start acting?;SELECT DISTINCT ?uri where {<A> dbo:activeYearsStartYear ?uri};select distinct ?a where {?a dbo:activeYearsStartYear ?uri};12
dbr:Actor;;;What movies did <A> star in?;SELECT DISTINCT ?uri where {?uri dbo:starring <A>};select distinct ?a where {?uri dbo:starring ?a};13
dbr:Actor;dbo:Film;;Did <A> star in <B>?;ASK where {<B> dbo:starring <A>};select distinct ?a,?b where {?b dbo:starring ?a};14
dbr:Actor;;;What is the production Company of <A>?;SELECT DISTINCT ?uri where {?uri dbo:productionCompany <A>};select distinct ?a where {?uri dbo:productionCompany ?a};15

# http://dbpedia.org/ontology/Film

dbo:Film;;;Who are producers of <A>?;SELECT DISTINCT ?uri where {<A> dbo:producer ?uri};select distinct ?a where {?a dbo:producer ?uri};16
dbo:Film;;;How much was the budget of <A>?;SELECT DISTINCT ?uri where {<A> dbo:budget ?uri};select distinct ?a where {?a dbo:budget ?uri};17
dbo:Film;;;Who is the director of <A>?;SELECT DISTINCT ?uri where {dbr:Mission:_Impossible_III dbo:director ?uri};select distinct ?a where {?a dbr:Mission:_Impossible_III dbo:director ?uri};18
dbo:Film;;;Who are the stars in <A>?;SELECT DISTINCT ?uri where {<A> dbo:starring ?uri};select distinct ?a where {?a dbo:starring ?uri};19
dbo:Film;;;How long is <A>?;SELECT DISTINCT ?uri where {<A> dbo:runtime ?uri};select distinct ?a where {?a dbo:runtime ?uri};20
dbo:Film;;;When was <A> released?;SELECT DISTINCT ?uri where {<A> dbp:released ?uri};select distinct ?a where {?a dbp:released ?uri};21


# http://dbpedia.org/ontology/Place

dbo:Place;;;Where is <A>?;SELECT DISTINCT ?uri where {<A> dbo:country ?uri};select distinct ?a where {?a dbo:country ?uri};22
dbo:Place;;;Where is <A>?;SELECT DISTINCT ?uri where {<A> dbp:country ?uri};select distinct ?a where {?a dbp:country ?uri};23
dbo:Place;;;How many people live in <A>?;SELECT DISTINCT ?uri where {<A> dbp:populationTotal ?uri};select distinct ?a where {?a dbp:populationTotal ?uri};24
dbo:Place;;;What is the population of <A>?;SELECT DISTINCT ?uri where {<A> dbp:populationTotal ?uri};select distinct ?awhere {?a dbp:populationTotal ?uri};25
dbo:Place;;;When was <A> established;SELECT DISTINCT ?uri where {<A> dbp:establishedDate ?uri};select distinct ?a where {?a dbp:establishedDate ?uri};26

# http://dbpedia.org/ontology/Publisher
# http://dbpedia.org/ontology/Genre
  
# http://dbpedia.org/ontology/Language

dbo:Language;;;In which region do people speak <A>?;SELECT DISTINCT ?uri where {<A> dbp:region ?uri};select distinct ?a where {?a dbp:region ?uri};27
dbo:Language;;;Which language family does <A> belong to?;SELECT DISTINCT ?uri where {<A> dbo:languageFamily ?uri};select distinct ?a where {?a dbo:languageFamily ?uri};28


# http://dbpedia.org/ontology/Department
# http://dbpedia.org/ontology/Software

dbo:Software;;;Who developed <A>?;SELECT DISTINCT ?uri where {<A> dbp:developer ?uri};select distinct ?a where {?a dbp:developer ?uri};29
dbo:Software;;;Who developed <A>?;SELECT DISTINCT ?uri where {<A> dbo:releaseDate ?uri};elect distinct ?a where {?a dbo:releaseDate ?uri};30
dbo:Software;;;What operating system can <A> run on?;SELECT DISTINCT ?uri where {<A> dbo:operatingSystem ?uri};select distinct ?a where {?a dbo:operatingSystem ?uri};31
dbo:Software;;;Who is the designer of <A>?;SELECT DISTINCT ?uri where {<A> dbp:designer ?uri};select distinct ?a where {?a dbp:designer ?uri;32

# http://dbpedia.org/ontology/School
dbo:School;;;When is <A> founded?;SELECT DISTINCT ?uri where { <A> dbo:founded ?uri};select distinct ?a where {?a rdf:type dbo:School. ?a dbp:founded ?uri};33
dbo:School;;;Who is the chairman of <A>?;SELECT DISTINCT ?uri where { <A> dbp:chairman ?uri};select distinct ?a where {?a rdf:type dbo:School. ?a dbp:chairman ?uri};34
dbo:School;;;How many students study in <A>?;SELECT DISTINCT ?uri where { <A> dbp:enrollment ?uri};select distinct ?a where {?a rdf:type dbo:School. ?a dbp:enrollment ?uri};35
dbo:School;;;How many staffs works in <A>?;SELECT DISTINCT ?uri where { <A> dbp:staff ?uri};select distinct ?a where {?a rdf:type dbo:School. ?a dbp:staff ?uri };36
dbo:School;;;Does <A> have a sport team?;ASK where { <A> dbp:teamName ?uri};select distinct ?a where {?a rdf:type dbo:School};37

# http://dbpedia.org/ontology/Cinema

dbo:Cinema;;;How many seats are there in <A>?;SELECT DISTINCT ?uri where { <A> dbo:seatingCapacity ?uri};select distinct ?a where {?a rdf:type dbo:Cinema. ?a dbo:seatingCapacity ?uri };37
dbo:Cinema;;;Which cinema is in the same city of <A>?;SELECT DISTINCT ?uri where { <A> dbo:location ?l. ?uri dbo:location ?l. ?uri rdf:type dbo:Cinema};select distinct ?a where {?a rdf:type dbo:Cinema. ?a dbo:location ?uri};38
dbo:Cinema;;;When is <A> opened?;SELECT DISTINCT ?uri where { <A> dbp:opened ?l};select distinct ?a where {?a rdf:type dbo:Cinema. ?a dbo:opened ?uri};39
dbo:Cinema;;;How many screens does <A> have?;SELECT DISTINCT ?uri where { <A> dbp:screens ?l};select distinct ?a where {?a rdf:type dbo:Cinema. ?a dbp:screen ?uri};40

# http://dbpedia.org/ontology/University

dbo:University;;;Where is <A>?;SELECT DISTINCT ?uri where { <A> dbo:city ?uri};select distinct ?a where {?a rdf:type dbo:University. ?a dbo:city ?uri };38
dbo:University;;;When is <A> founded?;SELECT DISTINCT ?uri where { <A> dbp:established ?uri};select distinct ?a where {?a rdf:type dbo:University. ?a dbp:established ?uri };39
dbo:University;;;How many students study in <A>?;SELECT DISTINCT ?uri where { <A> dbo:numberOfStudents ?uri};select distinct ?a where {?a rdf:type dbo:University. ?a dbo:numberOfStudents ?uri };40
dbo:Software;dbo:University;;Is <A> developed by <B>?;ASK where { <A> dbp:developer <B>};select distinct ?a, ?b where { ?a dbp:developer ?b. ?b rdf:type dbo:University};41
dbo:University;;;Who is the founder of <A>?;SELECT DISTINCT ?uri where { <A> dbp:founder ?uri};select distinct ?a where {?a rdf:type dbo:University. ?a dbo:founder ?uri };42

# http://dbpedia.org/ontology/Airline
# http://dbpedia.org/ontology/Bank
# http://dbpedia.org/ontology/BasketballLeague
# http://dbpedia.org/ontology/Anime
# http://dbpedia.org/ontology/City
http://dbpedia.org/ontology/City;;;What products are made by <A> based companies?;SELECT DISTINCT ?uri where { ?x dbp:location <A> . ?x dbo:product ?uri . ?x a dbo:Company };select distinct ?a where { ?x dbp:location ?a . ?x dbo:product ?uri . ?x a dbo:Company };0ad9954f309c496ab4dfbd8056a58187
http://dbpedia.org/ontology/City;;;Where can i find companies which were started in <A>?;SELECT DISTINCT ?uri where { ?x dbo:foundationPlace <A> . ?x dbp:locations ?uri . ?x a dbo:Company };select distinct ?a where { ?x dbo:foundationPlace ?a . ?x dbp:locations ?uri . ?x a dbo:Company };72d5cb491ec94f14b8d9683a64782b9c
http://dbpedia.org/ontology/City;;;Which companies makes cars assembled in <A>, Pakistan?;SELECT DISTINCT ?uri where { ?x dbp:assembly <A> . ?x dbp:parentCompany ?uri . ?x a dbo:Automobile };select distinct ?a where { ?x dbp:assembly ?a . ?x dbp:parentCompany ?uri . ?x a dbo:Automobile };4790db09b5954a87831e282bd16265df
http://dbpedia.org/ontology/City;;;Which sports are played at institues in <A>?;SELECT DISTINCT ?uri where { ?x dbo:city <A> . ?x dbo:sport ?uri . ?x a dbo:EducationalInstitution };select distinct ?a where { ?x dbo:city ?a . ?x dbo:sport ?uri . ?x a dbo:EducationalInstitution };38c688a1da544a7fb79c1a239732903f
http://dbpedia.org/ontology/City;;;Count the cities whihch are on the same sea as that of <A> ?;SELECT DISTINCT COUNT(?uri) where { ?x dbp:cities <A> . ?x dbp:cities ?uri };select distinct ?a where { ?x dbp:cities ?a . ?x dbp:cities ?uri };e2916bd3eb4a49159537f5a32218b829
http://dbpedia.org/ontology/City;;;How many buildings are located in <A> ?;SELECT DISTINCT COUNT(?uri) where { ?uri dbp:location <A> . ?uri a dbo:Building };select distinct ?a where { ?uri dbp:location ?a . ?uri a dbo:Building };6a6a9694fbb44140ada81d7a8c89aa0f

# http://dbpedia.org/ontology/Planet
# http://dbpedia.org/ontology/CricketTeam
# http://dbpedia.org/ontology/Film
# http://dbpedia.org/ontology/Game
# http://dbpedia.org/ontology/Mountain
# http://dbpedia.org/ontology/Museum
# http://dbpedia.org/ontology/Olympics
# http://dbpedia.org/ontology/Hotel
# http://dbpedia.org/ontology/TennisTournament
# http://dbpedia.org/ontology/Song
# http://dbpedia.org/ontology/Manga
# http://dbpedia.org/ontology/BasketballTeam
# http://dbpedia.org/ontology/Band
# http://dbpedia.org/ontology/Artist
# http://dbpedia.org/ontology/Aircraft
# http://dbpedia.org/ontology/Airport
# http://dbpedia.org/ontology/Album
# http://dbpedia.org/ontology/AmericanFootballPlayer
# http://dbpedia.org/ontology/Lake
http://dbpedia.org/ontology/Lake;;;How many cities are close to <A>?;SELECT DISTINCT COUNT(?uri) where { <A> dbo:nearestCity ?uri };select distinct ?a where { ?a dbo:nearestCity ?uri };209c460e684848fe9572d27a98ecbfea
http://dbpedia.org/ontology/Lake;;;In how many countries do the rivers start which end at the <A>?;SELECT DISTINCT COUNT(?uri) where { ?x dbo:riverMouth <A> . ?x dbo:sourceCountry ?uri . ?uri a dbo:Country };select distinct ?a where { ?x dbo:riverMouth ?a . ?x dbo:sourceCountry ?uri . ?uri a dbo:Country };c5e369b698d4499a92beac8371b73491
http://dbpedia.org/ontology/Lake;;;Name the nearest city to  <A>?;SELECT DISTINCT ?uri where { <A> dbo:nearestCity ?uri };select distinct ?a where { ?a dbo:nearestCity ?uri };a622cb449bde410c8c3e8c5c11a18ebb
http://dbpedia.org/ontology/Lake;http://dbpedia.org/ontology/City;;Name the river with source as <A> and its mouth is located in <B>?;SELECT DISTINCT ?uri where { ?uri dbo:source <A> . ?uri dbp:mouthLocation <B> . ?uri a dbo:River };select distinct ?a, ?b where { ?uri dbo:source ?a . ?uri dbp:mouthLocation ?b . ?uri a dbo:River };a08bb500ab2240118a0e3c00ed317f0b
http://dbpedia.org/ontology/Lake;;;what does the <A> flow into?;SELECT DISTINCT ?uri where { <A> dbp:inflow ?uri };select distinct ?a where { ?a dbp:inflow ?uri };84d8ee90740d450784488c785a892205

# http://dbpedia.org/ontology/MusicalArtist
# http://dbpedia.org/ontology/Writer
# http://dbpedia.org/ontology/Animal
# http://dbpedia.org/ontology/Browser
# http://dbpedia.org/ontology/Camera
# http://dbpedia.org/ontology/Arena



# http://dbpedia.org/ontology/ClubMoss
# http://dbpedia.org/ontology/AustralianFootballTeam

# http://dbpedia.org/ontology/FieldHockeyLeague
# http://dbpedia.org/ontology/MilitaryPerson
# http://dbpedia.org/ontology/VolleyballLeague
# http://dbpedia.org/ontology/Ambassador
# http://dbpedia.org/ontology/Amphibian
# http://dbpedia.org/ontology/Archaea
# http://dbpedia.org/ontology/BeachVolleyballPlayer
# http://dbpedia.org/ontology/Bone
# http://dbpedia.org/ontology/Canal
# http://dbpedia.org/ontology/Canoeist
# http://dbpedia.org/ontology/Cardinal
# http://dbpedia.org/ontology/Castle
# http://dbpedia.org/ontology/Cave
# http://dbpedia.org/ontology/ChristianPatriarch
# http://dbpedia.org/ontology/College
# http://dbpedia.org/ontology/Colour
# http://dbpedia.org/ontology/ComedyGroup
# http://dbpedia.org/ontology/ComicStrip
# http://dbpedia.org/ontology/ConcentrationCamp
# http://dbpedia.org/ontology/Conifer
# http://dbpedia.org/ontology/Continent
# http://dbpedia.org/ontology/Crustacean
# http://dbpedia.org/ontology/Entomologist
# http://dbpedia.org/ontology/Fashion
# http://dbpedia.org/ontology/Fern
# http://dbpedia.org/ontology/FormerMunicipality
# http://dbpedia.org/ontology/FormulaOneRacer
# http://dbpedia.org/ontology/Fungus
# http://dbpedia.org/ontology/Garden
# http://dbpedia.org/ontology/GolfCourse
# http://dbpedia.org/ontology/GreenAlga
# http://dbpedia.org/ontology/Guitarist
# http://dbpedia.org/ontology/Ligament
# http://dbpedia.org/ontology/Lighthouse
# http://dbpedia.org/ontology/Lymph
# http://dbpedia.org/ontology/Mineral
# http://dbpedia.org/ontology/NationalCollegiateAthleticAssociationAthlete
# http://dbpedia.org/ontology/Racecourse
# http://dbpedia.org/ontology/Rower
# http://dbpedia.org/ontology/Sea
# http://dbpedia.org/ontology/Senator
# http://dbpedia.org/ontology/SumoWrestler
# http://dbpedia.org/ontology/Vein
# http://dbpedia.org/ontology/VoiceActor
# http://dbpedia.org/ontology/Volcano
# http://dbpedia.org/ontology/AnimangaCharacter
# http://dbpedia.org/ontology/WaterwayTunnel
# http://dbpedia.org/ontology/Image

# http://dbpedia.org/ontology/HandballLeague
# http://dbpedia.org/ontology/IceHockeyLeague
# http://dbpedia.org/ontology/Locomotive
# http://dbpedia.org/ontology/MusicGenre
# http://dbpedia.org/ontology/ReligiousBuilding
# http://dbpedia.org/ontology/RoadTunnel
# http://dbpedia.org/ontology/Saint
# http://dbpedia.org/ontology/Single
# http://dbpedia.org/ontology/SpaceShuttle

# http://dbpedia.org/ontology/AmericanFootballLeague
# http://dbpedia.org/ontology/MusicFestival
# http://dbpedia.org/ontology/SpeedwayTeam
# http://dbpedia.org/ontology/LaunchPad
# http://dbpedia.org/ontology/SoftballLeague
# http://dbpedia.org/ontology/SpaceStation
# http://dbpedia.org/ontology/TennisLeague
# http://dbpedia.org/ontology/Gnetophytes
# http://dbpedia.org/ontology/BritishRoyalty
# http://dbpedia.org/ontology/AcademicJournal
# http://dbpedia.org/ontology/AdministrativeRegion

# http://dbpedia.org/ontology/AmusementParkAttraction


# http://dbpedia.org/ontology/ArtistDiscography
# http://dbpedia.org/ontology/Artwork
# http://dbpedia.org/ontology/Asteroid
# http://dbpedia.org/ontology/Athlete
# http://dbpedia.org/ontology/Automobile
# http://dbpedia.org/ontology/AutomobileEngine
# http://dbpedia.org/ontology/Award

# http://dbpedia.org/ontology/BaseballSeason

# http://dbpedia.org/ontology/Beverage
# http://dbpedia.org/ontology/BodyOfWater
# http://dbpedia.org/ontology/Book
# http://dbpedia.org/ontology/Bridge
# http://dbpedia.org/ontology/BroadcastNetwork
# http://dbpedia.org/ontology/Building
# http://dbpedia.org/ontology/BusCompany
# http://dbpedia.org/ontology/ChemicalCompound

# http://dbpedia.org/ontology/CityDistrict
# http://dbpedia.org/ontology/ClassicalMusicComposition
# http://dbpedia.org/ontology/Cleric
# http://dbpedia.org/ontology/Comic
# http://dbpedia.org/ontology/ComicsCharacter
# http://dbpedia.org/ontology/Convention
# http://dbpedia.org/ontology/Criminal
# http://dbpedia.org/ontology/CultivatedVariety
# http://dbpedia.org/ontology/CyclingRace
# http://dbpedia.org/ontology/CyclingTeam
# http://dbpedia.org/ontology/Device
# http://dbpedia.org/ontology/Disease
# http://dbpedia.org/ontology/Drug
# http://dbpedia.org/ontology/Earthquake
# http://dbpedia.org/ontology/Election
# http://dbpedia.org/ontology/Engine
# http://dbpedia.org/ontology/Enzyme
# http://dbpedia.org/ontology/EthnicGroup
# http://dbpedia.org/ontology/EurovisionSongContestEntry
# http://dbpedia.org/ontology/Event

# http://dbpedia.org/ontology/FilmFestival
# http://dbpedia.org/ontology/Food
# http://dbpedia.org/ontology/FootballLeagueSeason
# http://dbpedia.org/ontology/FootballMatch

# http://dbpedia.org/ontology/GolfTournament
# http://dbpedia.org/ontology/GovernmentAgency
# http://dbpedia.org/ontology/GrandPrix
# http://dbpedia.org/ontology/HistoricBuilding
# http://dbpedia.org/ontology/HistoricPlace
# http://dbpedia.org/ontology/HockeyTeam
# http://dbpedia.org/ontology/Holiday
# http://dbpedia.org/ontology/HollywoodCartoon
# http://dbpedia.org/ontology/HorseRace
# http://dbpedia.org/ontology/Hospital

# http://dbpedia.org/ontology/HumanGene
# http://dbpedia.org/ontology/InformationAppliance

# http://dbpedia.org/ontology/Legislature
# http://dbpedia.org/ontology/Library
# http://dbpedia.org/ontology/Magazine

# http://dbpedia.org/ontology/MilitaryConflict
# http://dbpedia.org/ontology/MilitaryStructure
# http://dbpedia.org/ontology/MilitaryUnit
# http://dbpedia.org/ontology/MixedMartialArtsEvent
# http://dbpedia.org/ontology/Monument
# http://dbpedia.org/ontology/MotorsportSeason

# http://dbpedia.org/ontology/Musical

# http://dbpedia.org/ontology/NCAATeamSeason
# http://dbpedia.org/ontology/NationalFootballLeagueSeason
# http://dbpedia.org/ontology/Newspaper

# http://dbpedia.org/ontology/Organisation
# http://dbpedia.org/ontology/Outbreak
# http://dbpedia.org/ontology/Pandemic
# http://dbpedia.org/ontology/Park
# http://dbpedia.org/ontology/PersonFunction
# http://dbpedia.org/ontology/Philosopher

# http://dbpedia.org/ontology/Plant
# http://dbpedia.org/ontology/Play
# http://dbpedia.org/ontology/PoliticalFunction
# http://dbpedia.org/ontology/PoliticalParty
# http://dbpedia.org/ontology/Politician
# http://dbpedia.org/ontology/PowerStation
# http://dbpedia.org/ontology/ProgrammingLanguage
# http://dbpedia.org/ontology/ProtectedArea
# http://dbpedia.org/ontology/Protein
# http://dbpedia.org/ontology/RacingDriver
# http://dbpedia.org/ontology/RadioHost
# http://dbpedia.org/ontology/RadioProgram
# http://dbpedia.org/ontology/RadioStation
# http://dbpedia.org/ontology/RailwayLine
# http://dbpedia.org/ontology/RecordLabel
# http://dbpedia.org/ontology/Religious
# http://dbpedia.org/ontology/Reptile
# http://dbpedia.org/ontology/ResearchProject
# http://dbpedia.org/ontology/Restaurant
# http://dbpedia.org/ontology/Road
# http://dbpedia.org/ontology/RoadJunction
# http://dbpedia.org/ontology/RollerCoaster
# http://dbpedia.org/ontology/Royalty
# http://dbpedia.org/ontology/RugbyClub
# http://dbpedia.org/ontology/RugbyLeague
# http://dbpedia.org/ontology/RugbyPlayer
# http://dbpedia.org/ontology/Sales
# http://dbpedia.org/ontology/Settlement
# http://dbpedia.org/ontology/Ship
# http://dbpedia.org/ontology/ShoppingMall
# http://dbpedia.org/ontology/SoccerClub
# http://dbpedia.org/ontology/SoccerClubSeason
# http://dbpedia.org/ontology/SoccerLeague
# http://dbpedia.org/ontology/SoccerTournament

# http://dbpedia.org/ontology/Sound
# http://dbpedia.org/ontology/SpaceMission
# http://dbpedia.org/ontology/SportsEvent
# http://dbpedia.org/ontology/SportsSeason
# http://dbpedia.org/ontology/SportsTeam
# http://dbpedia.org/ontology/SportsTeamMember
# http://dbpedia.org/ontology/Star
# http://dbpedia.org/ontology/Station
# http://dbpedia.org/ontology/SupremeCourtOfTheUnitedStatesCase
# http://dbpedia.org/ontology/TelevisionEpisode
# http://dbpedia.org/ontology/TelevisionSeason
# http://dbpedia.org/ontology/TelevisionShow
# http://dbpedia.org/ontology/TelevisionStation

# http://dbpedia.org/ontology/Tenure
# http://dbpedia.org/ontology/Theatre
# http://dbpedia.org/ontology/TopLevelDomain
# http://dbpedia.org/ontology/Town
# http://dbpedia.org/ontology/TradeUnion
# http://dbpedia.org/ontology/Train
# http://dbpedia.org/ontology/Venue
# http://dbpedia.org/ontology/VideoGame
# http://dbpedia.org/ontology/Village
# http://dbpedia.org/ontology/Weapon
# http://dbpedia.org/ontology/Website
# http://dbpedia.org/ontology/WomensTennisAssociationTournament
# http://dbpedia.org/ontology/WrestlingEvent

# http://dbpedia.org/ontology/WrittenWork
# http://dbpedia.org/ontology/Year
# http://dbpedia.org/ontology/YearInSpaceflight
# http://dbpedia.org/ontology/InlineHockeyLeague
# http://dbpedia.org/ontology/RaceTrack
# http://dbpedia.org/ontology/Tower
# http://dbpedia.org/ontology/GovernmentalAdministrativeRegion
# http://dbpedia.org/ontology/Instrumentalist
# http://dbpedia.org/ontology/Municipality
# http://dbpedia.org/ontology/BoxingLeague
# http://dbpedia.org/ontology/BowlingLeague
# http://dbpedia.org/ontology/CurlingLeague
# http://dbpedia.org/ontology/Agent

# http://dbpedia.org/ontology/ArchitecturalStructure
# http://dbpedia.org/ontology/Biomolecule
# http://dbpedia.org/ontology/Broadcaster
# http://dbpedia.org/ontology/Cartoon
# http://dbpedia.org/ontology/Case
# http://dbpedia.org/ontology/CelestialBody
# http://dbpedia.org/ontology/ChemicalSubstance
# http://dbpedia.org/ontology/Document
# http://dbpedia.org/ontology/EducationalInstitution
# http://dbpedia.org/ontology/Eukaryote
# http://dbpedia.org/ontology/FictionalCharacter
# http://dbpedia.org/ontology/Gene
# http://dbpedia.org/ontology/GridironFootballPlayer
# http://dbpedia.org/ontology/Group
# http://dbpedia.org/ontology/Identifier
# http://dbpedia.org/ontology/Infrastructure
# http://dbpedia.org/ontology/LegalCase
# http://dbpedia.org/ontology/MeanOfTransportation
# http://dbpedia.org/ontology/MotorsportRacer
# http://dbpedia.org/ontology/MusicalWork
# http://dbpedia.org/ontology/NaturalEvent
# http://dbpedia.org/ontology/NaturalPlace
# http://dbpedia.org/ontology/OrganisationMember
# http://dbpedia.org/ontology/PeriodicalLiterature
# http://dbpedia.org/ontology/PopulatedPlace
# http://dbpedia.org/ontology/Presenter
# http://dbpedia.org/ontology/Project
# http://dbpedia.org/ontology/PublicTransitSystem
# http://dbpedia.org/ontology/Race
# http://dbpedia.org/ontology/Region
# http://dbpedia.org/ontology/RouteOfTransportation
# http://dbpedia.org/ontology/SocietalEvent
# http://dbpedia.org/ontology/Species
# http://dbpedia.org/ontology/SportsClub
# http://dbpedia.org/ontology/SportsLeague
# http://dbpedia.org/ontology/SportsTeamSeason
# http://dbpedia.org/ontology/TimePeriod
# http://dbpedia.org/ontology/Tournament
# http://dbpedia.org/ontology/UnitOfWork
# http://dbpedia.org/ontology/Work
# http://dbpedia.org/ontology/AcademicConference
# http://dbpedia.org/ontology/AdultActor
# http://dbpedia.org/ontology/AmateurBoxer
# http://dbpedia.org/ontology/AnatomicalStructure
# http://dbpedia.org/ontology/Arachnid
# http://dbpedia.org/ontology/Archbishop
# http://dbpedia.org/ontology/Architect
# http://dbpedia.org/ontology/Artery
# http://dbpedia.org/ontology/Astronaut
# http://dbpedia.org/ontology/AustralianFootballLeague
# http://dbpedia.org/ontology/AustralianRulesFootballPlayer
# http://dbpedia.org/ontology/AutoRacingLeague
# http://dbpedia.org/ontology/Bacteria
# http://dbpedia.org/ontology/BadmintonPlayer
# http://dbpedia.org/ontology/BaseballPlayer
# http://dbpedia.org/ontology/BasketballPlayer
# http://dbpedia.org/ontology/BeautyQueen
# http://dbpedia.org/ontology/BiologicalDatabase
# http://dbpedia.org/ontology/Bodybuilder
# http://dbpedia.org/ontology/Boxer
# http://dbpedia.org/ontology/Brain
# http://dbpedia.org/ontology/Brewery
# http://dbpedia.org/ontology/BusinessPerson
# http://dbpedia.org/ontology/CareerStation
# http://dbpedia.org/ontology/Cheese
# http://dbpedia.org/ontology/Chef
# http://dbpedia.org/ontology/ChessPlayer
# http://dbpedia.org/ontology/ChristianBishop
# http://dbpedia.org/ontology/ClassicalMusicArtist
# http://dbpedia.org/ontology/CollegeCoach
# http://dbpedia.org/ontology/CombinationDrug
# http://dbpedia.org/ontology/Comedian
# http://dbpedia.org/ontology/ComicsCreator
# http://dbpedia.org/ontology/Congressman
# http://dbpedia.org/ontology/Country
# http://dbpedia.org/ontology/Crater
# http://dbpedia.org/ontology/CricketGround
# http://dbpedia.org/ontology/Cricketer
# http://dbpedia.org/ontology/Curler
# http://dbpedia.org/ontology/Currency
# http://dbpedia.org/ontology/Cyclist
# http://dbpedia.org/ontology/Dam
# http://dbpedia.org/ontology/DartsPlayer
# http://dbpedia.org/ontology/Economist
# http://dbpedia.org/ontology/Engineer
# http://dbpedia.org/ontology/FashionDesigner
# http://dbpedia.org/ontology/FigureSkater
# http://dbpedia.org/ontology/Fish
# http://dbpedia.org/ontology/FormulaOneTeam
# http://dbpedia.org/ontology/GaelicGamesPlayer
# http://dbpedia.org/ontology/Galaxy
# http://dbpedia.org/ontology/GivenName
# http://dbpedia.org/ontology/Glacier
# http://dbpedia.org/ontology/GolfPlayer
# http://dbpedia.org/ontology/Governor
# http://dbpedia.org/ontology/Grape
# http://dbpedia.org/ontology/Gymnast
# http://dbpedia.org/ontology/HandballPlayer
# http://dbpedia.org/ontology/HandballTeam
# http://dbpedia.org/ontology/Historian
# http://dbpedia.org/ontology/HistoricalEvent
# http://dbpedia.org/ontology/Horse
# http://dbpedia.org/ontology/HorseTrainer
# http://dbpedia.org/ontology/IceHockeyPlayer
# http://dbpedia.org/ontology/Insect
# http://dbpedia.org/ontology/Island
# http://dbpedia.org/ontology/Jockey
# http://dbpedia.org/ontology/Journalist
# http://dbpedia.org/ontology/LacrossePlayer
# http://dbpedia.org/ontology/LawFirm
# http://dbpedia.org/ontology/Mammal
# http://dbpedia.org/ontology/MartialArtist
# http://dbpedia.org/ontology/Mayor
# http://dbpedia.org/ontology/Medician
# http://dbpedia.org/ontology/MemberOfParliament
# http://dbpedia.org/ontology/MilitaryService
# http://dbpedia.org/ontology/MixedMartialArtsLeague
# http://dbpedia.org/ontology/Model
# http://dbpedia.org/ontology/Mollusca
# http://dbpedia.org/ontology/MonoclonalAntibody
# http://dbpedia.org/ontology/Motorcycle
# http://dbpedia.org/ontology/MotorcycleRacingLeague
# http://dbpedia.org/ontology/MotorcycleRider
# http://dbpedia.org/ontology/MountainPass
# http://dbpedia.org/ontology/Muscle
# http://dbpedia.org/ontology/MythologicalFigure
# http://dbpedia.org/ontology/NascarDriver
# http://dbpedia.org/ontology/NationalFootballLeagueEvent
# http://dbpedia.org/ontology/Nerve
# http://dbpedia.org/ontology/NetballPlayer
# http://dbpedia.org/ontology/Noble
# http://dbpedia.org/ontology/Painter
# http://dbpedia.org/ontology/Photographer
# http://dbpedia.org/ontology/Poem
# http://dbpedia.org/ontology/Poet
# http://dbpedia.org/ontology/PokerPlayer
# http://dbpedia.org/ontology/PoloLeague
# http://dbpedia.org/ontology/President
# http://dbpedia.org/ontology/Priest
# http://dbpedia.org/ontology/PrimeMinister
# http://dbpedia.org/ontology/Prison
# http://dbpedia.org/ontology/RailwayStation
# http://dbpedia.org/ontology/RailwayTunnel
# http://dbpedia.org/ontology/River
# http://dbpedia.org/ontology/Rocket
# http://dbpedia.org/ontology/Scientist
# http://dbpedia.org/ontology/ScreenWriter
# http://dbpedia.org/ontology/SiteOfSpecialScientificInterest
# http://dbpedia.org/ontology/Skater
# http://dbpedia.org/ontology/SkiArea
# http://dbpedia.org/ontology/Skier
# http://dbpedia.org/ontology/Skyscraper
# http://dbpedia.org/ontology/SnookerPlayer
# http://dbpedia.org/ontology/SoapCharacter
# http://dbpedia.org/ontology/SoccerManager
# http://dbpedia.org/ontology/SoccerPlayer
# http://dbpedia.org/ontology/SpeedwayRider
# http://dbpedia.org/ontology/Sport
# http://dbpedia.org/ontology/SquashPlayer
# http://dbpedia.org/ontology/Stadium
# http://dbpedia.org/ontology/Swimmer
# http://dbpedia.org/ontology/TableTennisPlayer
# http://dbpedia.org/ontology/TelevisionHost
# http://dbpedia.org/ontology/TennisPlayer
# http://dbpedia.org/ontology/Tunnel
# http://dbpedia.org/ontology/VolleyballPlayer
# http://dbpedia.org/ontology/WineRegion
# http://dbpedia.org/ontology/Winery
# http://dbpedia.org/ontology/WorldHeritageSite
# http://dbpedia.org/ontology/Wrestler
# http://dbpedia.org/ontology/Youtuber
# http://dbpedia.org/ontology/Battery
# http://dbpedia.org/ontology/Bird
# http://dbpedia.org/ontology/Chancellor
# http://dbpedia.org/ontology/CricketLeague
# http://dbpedia.org/ontology/GolfLeague
# http://dbpedia.org/ontology/Judge
# http://dbpedia.org/ontology/LacrosseLeague
# http://dbpedia.org/ontology/OlympicEvent
# http://dbpedia.org/ontology/PlayboyPlaymate
# http://dbpedia.org/ontology/SpeedwayLeague
# http://dbpedia.org/ontology/WaterRide
# http://dbpedia.org/ontology/ClericalAdministrativeRegion
# http://dbpedia.org/ontology/AmericanFootballCoach
# http://dbpedia.org/ontology/BaseballLeague
# http://dbpedia.org/ontology/Bay
# http://dbpedia.org/ontology/CanadianFootballLeague
# http://dbpedia.org/ontology/Diocese
# http://dbpedia.org/ontology/Embryology
# http://dbpedia.org/ontology/HorseRider
# http://dbpedia.org/ontology/SnookerChamp
# http://dbpedia.org/ontology/Surname
# http://dbpedia.org/ontology/VolleyballCoach
# http://dbpedia.org/ontology/MedicalSpecialty
# http://dbpedia.org/ontology/Constellation
# http://dbpedia.org/ontology/TopicalConcept
# http://dbpedia.org/ontology/Moss
# http://dbpedia.org/ontology/VideogamesLeague
# http://dbpedia.org/ontology/Vaccine
# http://dbpedia.org/ontology/AmericanFootballTeam
# http://dbpedia.org/ontology/Baronet
# http://dbpedia.org/ontology/BaseballTeam
# http://dbpedia.org/ontology/Novel
# http://dbpedia.org/ontology/Pope
# http://dbpedia.org/ontology/Cycad
# http://dbpedia.org/ontology/FloweringPlant
# http://dbpedia.org/ontology/Database
# http://dbpedia.org/ontology/SportFacility
# http://dbpedia.org/ontology/Stream
# http://dbpedia.org/ontology/Coach
# http://dbpedia.org/ontology/SportsManager
# http://dbpedia.org/ontology/WinterSportPlayer
# http://dbpedia.org/ontology/Ginkgo
# http://dbpedia.org/ontology/SnookerWorldRanking
# http://dbpedia.org/ontology/SolarEclipse
# http://dbpedia.org/ontology/SportCompetitionResult
# http://dbpedia.org/ontology/Non-ProfitOrganisation
# http://dbpedia.org/ontology/ArtificialSatellite
# http://dbpedia.org/ontology/Monarch
# http://dbpedia.org/ontology/MountainRange
# http://dbpedia.org/ontology/OfficeHolder
# http://dbpedia.org/ontology/Spacecraft
# http://dbpedia.org/ontology/Valley
# http://dbpedia.org/ontology/Academic
# http://dbpedia.org/ontology/AcademicSubject
# http://dbpedia.org/ontology/Agglomeration
# http://dbpedia.org/ontology/Algorithm
# http://dbpedia.org/ontology/Altitude
# http://dbpedia.org/ontology/AmericanLeader
# http://dbpedia.org/ontology/Annotation
# http://dbpedia.org/ontology/Archeologist
# http://dbpedia.org/ontology/ArcherPlayer
# http://dbpedia.org/ontology/Archipelago
# http://dbpedia.org/ontology/Area

# http://dbpedia.org/ontology/Aristocrat
# http://dbpedia.org/ontology/Arrondissement
# http://dbpedia.org/ontology/Article
# http://dbpedia.org/ontology/ArtisticGenre
# http://dbpedia.org/ontology/AthleticsPlayer
# http://dbpedia.org/ontology/Atoll
# http://dbpedia.org/ontology/Attack
# http://dbpedia.org/ontology/BackScene
# http://dbpedia.org/ontology/Beach
# http://dbpedia.org/ontology/Beer
# http://dbpedia.org/ontology/Biathlete
# http://dbpedia.org/ontology/Biologist
# http://dbpedia.org/ontology/Blazon
# http://dbpedia.org/ontology/BloodVessel
# http://dbpedia.org/ontology/BoardGame
# http://dbpedia.org/ontology/BobsleighAthlete
# http://dbpedia.org/ontology/BrownDwarf

# http://dbpedia.org/ontology/BullFighter

# http://dbpedia.org/ontology/CanadianFootballPlayer
# http://dbpedia.org/ontology/CanadianFootballTeam
# http://dbpedia.org/ontology/Canton
# http://dbpedia.org/ontology/Cape
# http://dbpedia.org/ontology/Capital
# http://dbpedia.org/ontology/CapitalOfRegion
# http://dbpedia.org/ontology/CardGame
# http://dbpedia.org/ontology/CardinalDirection
# http://dbpedia.org/ontology/Casino
# http://dbpedia.org/ontology/Cat
# http://dbpedia.org/ontology/Caterer
# http://dbpedia.org/ontology/Cemetery
# http://dbpedia.org/ontology/ChartsPlacements
# http://dbpedia.org/ontology/ChemicalElement
# http://dbpedia.org/ontology/ChristianDoctrine
# http://dbpedia.org/ontology/Church
# http://dbpedia.org/ontology/Cipher
# http://dbpedia.org/ontology/ClericalOrder
# http://dbpedia.org/ontology/CoalPit
# http://dbpedia.org/ontology/CollectionOfValuables
# http://dbpedia.org/ontology/Community
# http://dbpedia.org/ontology/Competition
# http://dbpedia.org/ontology/Contest
# http://dbpedia.org/ontology/ControlledDesignationOfOriginWine
# http://dbpedia.org/ontology/ConveyorSystem
# http://dbpedia.org/ontology/CountrySeat
# http://dbpedia.org/ontology/Covid19
# http://dbpedia.org/ontology/CrossCountrySkier
# http://dbpedia.org/ontology/CyclingCompetition
# http://dbpedia.org/ontology/CyclingLeague
# http://dbpedia.org/ontology/DBpedian
# http://dbpedia.org/ontology/DTMRacer
# http://dbpedia.org/ontology/Dancer
# http://dbpedia.org/ontology/Deanery
# http://dbpedia.org/ontology/Decoration
# http://dbpedia.org/ontology/Deity
# http://dbpedia.org/ontology/Demographics
# http://dbpedia.org/ontology/Deputy
# http://dbpedia.org/ontology/Desert
# http://dbpedia.org/ontology/DigitalCamera
# http://dbpedia.org/ontology/Dike
# http://dbpedia.org/ontology/Diploma
# http://dbpedia.org/ontology/DisneyCharacter
# http://dbpedia.org/ontology/District
# http://dbpedia.org/ontology/DistrictWaterBoard
# http://dbpedia.org/ontology/Drama
# http://dbpedia.org/ontology/ElectionDiagram
# http://dbpedia.org/ontology/ElectricalSubstation
# http://dbpedia.org/ontology/Escalator
# http://dbpedia.org/ontology/Forest
# http://dbpedia.org/ontology/FormulaOneRacing
# http://dbpedia.org/ontology/Fort
# http://dbpedia.org/ontology/GatedCommunity
# http://dbpedia.org/ontology/GeneLocation
# http://dbpedia.org/ontology/GeologicalPeriod
# http://dbpedia.org/ontology/GeopoliticalOrganisation
# http://dbpedia.org/ontology/Globularswarm
# http://dbpedia.org/ontology/GovernmentCabinet
# http://dbpedia.org/ontology/GovernmentType
# http://dbpedia.org/ontology/GraveMonument
# http://dbpedia.org/ontology/GrossDomesticProduct
# http://dbpedia.org/ontology/GrossDomesticProductPerCapita
# http://dbpedia.org/ontology/HighDiver
# http://dbpedia.org/ontology/HistoricalAreaOfAuthority
# http://dbpedia.org/ontology/HistoricalCountry
# http://dbpedia.org/ontology/HistoricalDistrict
# http://dbpedia.org/ontology/HistoricalPeriod
# http://dbpedia.org/ontology/HistoricalProvince
# http://dbpedia.org/ontology/HistoricalRegion
# http://dbpedia.org/ontology/HistoricalSettlement
# http://dbpedia.org/ontology/HockeyClub
# http://dbpedia.org/ontology/Hormone
# http://dbpedia.org/ontology/HotSpring
# http://dbpedia.org/ontology/HumanGeneLocation
# http://dbpedia.org/ontology/Humorist
# http://dbpedia.org/ontology/Ideology
# http://dbpedia.org/ontology/Infrastucture
# http://dbpedia.org/ontology/Instrument
# http://dbpedia.org/ontology/Intercommunality
# http://dbpedia.org/ontology/InternationalFootballLeagueEvent
# http://dbpedia.org/ontology/InternationalOrganisation
# http://dbpedia.org/ontology/JewishLeader
# http://dbpedia.org/ontology/LatterDaySaint
# http://dbpedia.org/ontology/Law
# http://dbpedia.org/ontology/Lawyer
# http://dbpedia.org/ontology/Letter
# http://dbpedia.org/ontology/Lieutenant
# http://dbpedia.org/ontology/LifeCycleEvent
# http://dbpedia.org/ontology/LightNovel
# http://dbpedia.org/ontology/LineOfFashion
# http://dbpedia.org/ontology/Linguist
# http://dbpedia.org/ontology/Lipid
# http://dbpedia.org/ontology/List
# http://dbpedia.org/ontology/LiteraryGenre
# http://dbpedia.org/ontology/Locality
# http://dbpedia.org/ontology/Lock
# http://dbpedia.org/ontology/LunarCrater
# http://dbpedia.org/ontology/Man
# http://dbpedia.org/ontology/Manhua
# http://dbpedia.org/ontology/Manhwa
# http://dbpedia.org/ontology/Manor
# http://dbpedia.org/ontology/MathematicalConcept
# http://dbpedia.org/ontology/Media
# http://dbpedia.org/ontology/Medicine
# http://dbpedia.org/ontology/Meeting
# http://dbpedia.org/ontology/MemberResistanceMovement
# http://dbpedia.org/ontology/Memorial
# http://dbpedia.org/ontology/MetroStation
# http://dbpedia.org/ontology/MicroRegion
# http://dbpedia.org/ontology/MilitaryAircraft
# http://dbpedia.org/ontology/MilitaryVehicle
# http://dbpedia.org/ontology/Mill
# http://dbpedia.org/ontology/Mine
# http://dbpedia.org/ontology/Minister
# http://dbpedia.org/ontology/MobilePhone
# http://dbpedia.org/ontology/Monastery
# http://dbpedia.org/ontology/Mosque
# http://dbpedia.org/ontology/MotocycleRacer
# http://dbpedia.org/ontology/MotorRace
# http://dbpedia.org/ontology/MouseGene
# http://dbpedia.org/ontology/MouseGeneLocation
# http://dbpedia.org/ontology/MovieDirector
# http://dbpedia.org/ontology/MovieGenre
# http://dbpedia.org/ontology/MovingImage
# http://dbpedia.org/ontology/MovingWalkway
# http://dbpedia.org/ontology/MultiVolumePublication
# http://dbpedia.org/ontology/Murderer
# http://dbpedia.org/ontology/MusicComposer
# http://dbpedia.org/ontology/MusicDirector
# http://dbpedia.org/ontology/NarutoCharacter
# http://dbpedia.org/ontology/NationalAnthem
# http://dbpedia.org/ontology/NationalSoccerClub
# http://dbpedia.org/ontology/NaturalRegion
# http://dbpedia.org/ontology/Nebula
# http://dbpedia.org/ontology/NobelPrize
# http://dbpedia.org/ontology/NobleFamily
# http://dbpedia.org/ontology/NordicCombined
# http://dbpedia.org/ontology/NuclearPowerStation
# http://dbpedia.org/ontology/Ocean
# http://dbpedia.org/ontology/OldTerritory
# http://dbpedia.org/ontology/OlympicResult
# http://dbpedia.org/ontology/On-SiteTransportation
# http://dbpedia.org/ontology/Openswarm
# http://dbpedia.org/ontology/Opera
# http://dbpedia.org/ontology/Organ
# http://dbpedia.org/ontology/OverseasDepartment
# http://dbpedia.org/ontology/PaintballLeague
# http://dbpedia.org/ontology/Painting
# http://dbpedia.org/ontology/Parish
# http://dbpedia.org/ontology/Parliament
# http://dbpedia.org/ontology/PenaltyShootOut
# http://dbpedia.org/ontology/PeriodOfArtisticStyle
# http://dbpedia.org/ontology/PersonalEvent
# http://dbpedia.org/ontology/Pharaoh
# http://dbpedia.org/ontology/PhilosophicalConcept
# http://dbpedia.org/ontology/Pilot
# http://dbpedia.org/ontology/PlayWright
# http://dbpedia.org/ontology/PoliceOfficer
# http://dbpedia.org/ontology/PoliticalConcept
# http://dbpedia.org/ontology/PoliticianSpouse
# http://dbpedia.org/ontology/Polysaccharide
# http://dbpedia.org/ontology/Population
# http://dbpedia.org/ontology/Port
# http://dbpedia.org/ontology/Prefecture
# http://dbpedia.org/ontology/PrehistoricalPeriod
# http://dbpedia.org/ontology/Pretender
# http://dbpedia.org/ontology/Producer
# http://dbpedia.org/ontology/Profession
# http://dbpedia.org/ontology/Professor
# http://dbpedia.org/ontology/Protocol
# http://dbpedia.org/ontology/ProtohistoricalPeriod
# http://dbpedia.org/ontology/Province
# http://dbpedia.org/ontology/Psychologist
# http://dbpedia.org/ontology/PublicService
# http://dbpedia.org/ontology/Pyramid
# http://dbpedia.org/ontology/Quote
# http://dbpedia.org/ontology/RadioControlledRacingLeague
# http://dbpedia.org/ontology/RallyDriver
# http://dbpedia.org/ontology/Rebbe
# http://dbpedia.org/ontology/Rebellion
# http://dbpedia.org/ontology/RecordOffice
# http://dbpedia.org/ontology/Referee
# http://dbpedia.org/ontology/Reference
# http://dbpedia.org/ontology/Regency
# http://dbpedia.org/ontology/Reign
# http://dbpedia.org/ontology/Relationship
# http://dbpedia.org/ontology/ReligiousOrganisation
# http://dbpedia.org/ontology/RestArea
# http://dbpedia.org/ontology/Resume
# http://dbpedia.org/ontology/Robot
# http://dbpedia.org/ontology/RocketEngine
# http://dbpedia.org/ontology/RomanEmperor
# http://dbpedia.org/ontology/RouteStop
# http://dbpedia.org/ontology/Sailor
# http://dbpedia.org/ontology/SambaSchool
# http://dbpedia.org/ontology/Satellite
# http://dbpedia.org/ontology/ScientificConcept
# http://dbpedia.org/ontology/Sculptor
# http://dbpedia.org/ontology/Sculpture
# http://dbpedia.org/ontology/SerialKiller
# http://dbpedia.org/ontology/Shrine
# http://dbpedia.org/ontology/Singer
# http://dbpedia.org/ontology/SkiResort
# http://dbpedia.org/ontology/Ski_jumper
# http://dbpedia.org/ontology/SoccerLeagueSeason
# http://dbpedia.org/ontology/SongWriter
# http://dbpedia.org/ontology/SpeedSkater
# http://dbpedia.org/ontology/Spreadsheet
# http://dbpedia.org/ontology/Spy
# http://dbpedia.org/ontology/Square
# http://dbpedia.org/ontology/Standard
# http://dbpedia.org/ontology/StarCluster
# http://dbpedia.org/ontology/State
# http://dbpedia.org/ontology/StatedResolution
# http://dbpedia.org/ontology/Statistic
# http://dbpedia.org/ontology/StillImage
# http://dbpedia.org/ontology/StormSurge
# http://dbpedia.org/ontology/Street
# http://dbpedia.org/ontology/SubMunicipality
# http://dbpedia.org/ontology/Surfer
# http://dbpedia.org/ontology/Swarm
# http://dbpedia.org/ontology/Synagogue
# http://dbpedia.org/ontology/SystemOfLaw
# http://dbpedia.org/ontology/Tank
# http://dbpedia.org/ontology/Tax
# http://dbpedia.org/ontology/Taxon
# http://dbpedia.org/ontology/TeamMember
# http://dbpedia.org/ontology/TeamSport
# http://dbpedia.org/ontology/TelevisionDirector
# http://dbpedia.org/ontology/Temple
# http://dbpedia.org/ontology/TermOfOffice
# http://dbpedia.org/ontology/Territory
# http://dbpedia.org/ontology/TheatreDirector
# http://dbpedia.org/ontology/TheologicalConcept
# http://dbpedia.org/ontology/TrackList
# http://dbpedia.org/ontology/TrainCarriage
# http://dbpedia.org/ontology/Tram
# http://dbpedia.org/ontology/TramStation
# http://dbpedia.org/ontology/Treadmill
# http://dbpedia.org/ontology/Treaty
# http://dbpedia.org/ontology/UndergroundJournal
# http://dbpedia.org/ontology/Unknown
# http://dbpedia.org/ontology/VaccinationStatistics
# http://dbpedia.org/ontology/Vicar
# http://dbpedia.org/ontology/VicePresident
# http://dbpedia.org/ontology/VicePrimeMinister
# http://dbpedia.org/ontology/Vodka
# http://dbpedia.org/ontology/WaterPoloPlayer
# http://dbpedia.org/ontology/WaterTower
# http://dbpedia.org/ontology/Watermill
# http://dbpedia.org/ontology/WikimediaTemplate
# http://dbpedia.org/ontology/WindMotor
# http://dbpedia.org/ontology/Windmill
# http://dbpedia.org/ontology/Wine
# http://dbpedia.org/ontology/Woman
# http://dbpedia.org/ontology/Zoo
