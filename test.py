from tornado import gen
from tornado.ioloop import IOLoop
from gremlinclient.tornado_client import submit
from pymongo import MongoClient

client_52 = MongoClient('192.168.102.52')
db_word_net = client_52['WordNet']
coll_words = db_word_net['Words']
coll_nodes = db_word_net['Nodes']
coll_edges = db_word_net['Edges']
coll_relative_edges = db_word_net['RelativeEdges']
coll_synonym_edges = db_word_net['SynonymEdges']

host = 'ws://pro-ha-worker04.five9.local:8182/gremlin'

loop = IOLoop.current()

#########

vertices = []


@gen.coroutine
def get_all_words():
    query_get_all_vertices = 'def g=ConfiguredGraphFactory.open(\"wordnet\").traversal(); g.V();'
    while True:
        resp = yield submit(host, query_get_all_vertices)
        msg = yield resp.read()
        if msg is None:
            break
        else:
            data = msg[1]
            for d in data:
                print(d)
                vertices.append(d)


loop.run_sync(get_all_words)

#########

vertice = []
word = 'tháng này'
label = 1000000
english_word = 'instant.s.02'


@gen.coroutine
def get_vertice():
    query_get_vertice = 'def g=ConfiguredGraphFactory.open(\"wordnet\").traversal(); g.V().has(\"name\", \"' + word + '\");'
    resp = yield submit(host, query_get_vertice)
    while True:
        msg = yield resp.read()
        print(msg)
        if msg is None:
            break


loop.run_sync(get_vertice)

#########

data = list(
    coll_nodes.find({}, {'_id': 1, 'id': 1, 'vietnamese_word': 1, 'english_word': 1, 'word_type': 1}))

j = 0


@gen.coroutine
def go():
    while True:
        query_add_vertices = 'def graph=ConfiguredGraphFactory.open(\"wordnet\");'
        global j
        if j < len(data):
            doc = data[j]
            query_add_vertices += 'graph.addVertex(T.label, "' + str(doc['_id']) \
                                  + '", "id", "' + str(doc['id']) \
                                  + '", "name", "' + str(doc['vietnamese_word']) \
                                  + '", "english_word", "' + str(doc['english_word']) \
                                  + '", "word_type", "' + str(doc['word_type']) + '");'
            print(j)
            j += 1
        else:
            break
        resp = yield submit(host, query_add_vertices)
        msg = yield resp.read()
        print(msg)
        if msg is None:
            break


loop.run_sync(go)

########

data = list(coll_edges.find({}, {'source': 1, 'target': 1, 'name': 1}))
i = 0


@gen.coroutine
def go():
    while True:
        query_add_edges = 'def graph=ConfiguredGraphFactory.open(\"wordnet\"); def g=graph.traversal();'
        global i
        if i < len(data):
            doc = data[i]
            query_add_edges += 'def v1 = g.V().has(T.label, "' \
                               + str(doc['source']) + '").next(); def v2 = g.V().has(T.label, "' + str(doc[
                                                                                                           'target']) + '").next(); v1.addEdge("' + \
                               doc['name'] + '", v2, "weight", 0.4f);'
            print(i)
            i += 1
        else:
            break
        resp = yield submit(host, query_add_edges)
        msg = yield resp.read()
        print(msg)
        if msg is None:
            break


loop.run_sync(go)

######

query_count_vertices = 'def graph=ConfiguredGraphFactory.open(\"vfm\"); g=graph.traversal(); g.V().count();'
query_add_vertice = 'def graph=ConfiguredGraphFactory.open(\"vfm\"); graph.addVertex(T.label, "person", "name", "test");'
query_find_vertice = 'def graph=ConfiguredGraphFactory.open(\"wordnet\"); g=graph.traversal(); g.V().has("name", "test1");'


@gen.coroutine
def go():
    resp = yield submit(host, query_add_vertice)
    while True:
        msg = yield resp.read()
        print(msg)
        if msg is None:
            break


loop.run_sync(go)

query_build_index = 'def graph=ConfiguredGraphFactory.open(\"wordnet\"); graph.tx().rollback(); mgmt=graph.openManagement(); ' \
                    + 'name=mgmt.getPropertyKey(\"name\"); ' \
                    + 'mgmt.buildIndex(\"byNameUnique\", Vertex.class).addKey(name).unique().buildCompositeIndex(); ' \
                    + 'mgmt.commit();'
# + 'mgmt.awaitGraphIndexStatus(\"wordnet\", \"byNameUnique\").call(); ' \
# + 'mgmt.updateIndex(mgmt.getGraphIndex(\"byNameUnique\"), SchemaAction.REINDEX).get(); ' \
# + 'mgmt.commit();'


@gen.coroutine
def go():
    resp = yield submit(host, query_build_index)
    while True:
        msg = yield resp.read()
        print(msg)
        if msg is None:
            break


loop.run_sync(go)

db_vfm = client_52['VFM']
coll_vfm_nodes = db_vfm['Nodes_Viet']

host = 'ws://pro-ha-worker04.five9.local:8182/gremlin'

loop = IOLoop.current()

cursor = coll_vfm_nodes.find({}, no_cursor_timeout=True)

j = 0


@gen.coroutine
def go():
    query_add_vertices = 'def graph=ConfiguredGraphFactory.open(\"vfm\");'
    while True:
        global j
        if j < 6078294:
            doc = cursor.next()
            query_add_vertices += 'graph.addVertex(T.label, "person", "id", "' + str(doc['_id']) \
                                  + '", "name", "' + str(doc['name']) \
                                  + '", "age", "' + str(doc['age']) \
                                  + '", "work", "' + str(doc['work']) \
                                  + '", "gender", "' + str(doc['gender']) \
                                  + '", "location", "' + str(doc['location']) + '");'
            print(j)
            j += 1

        else:
            break
        if j % 200 == 0:
            query_add_vertices += 'graph.tx().commit();'
            print(query_add_vertices)
            resp = yield submit(host, query_add_vertices)
            msg = yield resp.read()
            query_add_vertices = 'def graph=ConfiguredGraphFactory.open(\"vfm\");'
            print(msg)
            if msg is None:
                break


loop.run_sync(go)
