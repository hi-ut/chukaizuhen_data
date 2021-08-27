import json
import os

from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

path = "../../chukaizuhen/static/data/index.json"

all = Graph()

prefix = "https://lab.hi.u-tokyo.ac.jp"
p = prefix + "/term/property#"

with open(path) as f:
    index = json.load(f)

for obj in index:
    id = obj["objectID"]
    label = obj["label"]
    image = obj["thumbnail"]
    category = obj["分類"][0]
    member = obj["member"]
    manifest = obj["manifest"]
    modified = obj["_updated"]

    uri = prefix + "/term/keyword/" + label.replace(" ", "_")
    subject = URIRef(uri)

    category_uri = URIRef(prefix + "/term/keyword/" + category)

    all.add((subject, RDFS.label, Literal(label)))
    all.add((subject, RDF.type, URIRef(prefix + "/term/type/Keyword")))
    all.add((subject, URIRef("http://schema.org/about"), category_uri))
    all.add((subject, URIRef("http://schema.org/image"), URIRef(image)))
    all.add((subject, URIRef("http://schema.org/url"), URIRef(manifest)))
    all.add((subject, URIRef("http://schema.org/dateModified"), Literal(modified)))
    all.add((subject, URIRef(p + "member"), URIRef(member)))

    all.add((category_uri, RDFS.label, Literal(category)))
    all.add((category_uri, RDF.type, URIRef(prefix + "/term/type/Keyword")))

all.serialize(destination="data/all.ttl", format='turtle')