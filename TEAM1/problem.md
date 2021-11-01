# problem from dbpedia

## doubled dbr

I found a problem while trying building the query for "which German cities have the mayor from CDU?"

in some cities, the country is like:

`
dbo:country dbr:Germany
`

for example, in <https://dbpedia.org/page/Laer>

but in other cities, the country is like:

`
dbo:country dbr:http://dbpedia.org/resource/Germany
`

for example, in <https://dbpedia.org/page/Paderborn>

so in this case, we have to write `<http://dbpedia.org/resource/http://dbpedia.org/resource/Germany>` in a query.
I also tried `dbr:dbr:Germany`. It didn't work.

## Capitalization

The first letter of a country or a name must be capitalized.

## rdf

Query generation doesn't work for other prefixes, e.g. rdf, geo, ...
