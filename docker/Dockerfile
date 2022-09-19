FROM neo4j:4.4.9

ENV NEO4J_AUTH='neo4j/testing123'

COPY ./plugins /plugins

RUN echo "dbms.security.procedures.unrestricted=gds.*" > ./conf/neo4j.conf
RUN echo "dbms.security.procedures.allowlist=gds.*" > ./conf/neo4j.conf

EXPOSE 7474
EXPOSE 7687