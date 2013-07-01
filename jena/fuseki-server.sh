#!/usr/bin/env bash

export FUSEKI_HOME="/Users/howard/dev/jena-fuseki-0.2.7"

java -Xmx1200M -cp "/Users/howard/dev/jena-fuseki-0.2.7/lib/*:/Users/howard/dev/jena-fuseki-0.2.7/fuseki-server.jar" org.apache.jena.fuseki.FusekiCmd --config=/Users/howard/dev/catalogit/cataloger/jena/cit.ttl