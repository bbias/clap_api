from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import time

fmt = "\n=== {:30} ===\n"
search_latency_fmt = "search latency = {:.4f}s"

#################################################################################
# 1. connect to Milvus

print(fmt.format("start connecting to Milvus"))
connections.connect("default", host="localhost", port="19530")

has = utility.has_collection("clap_db")
print(f"Does collection clap_db exist in Milvus: {has}")

#################################################################################
# 2. create collection

fields = [
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="random", dtype=DataType.DOUBLE),
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=8)
]

schema = CollectionSchema(fields, "clap_db is the simplest demo to introduce the APIs")

print(fmt.format("Create collection `clap_db`"))
clap_db = Collection("clap_db", schema, consistency_level="Strong")

#################################################################################
# 3. create index

index = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 256},
}
clap_db.create_index("embeddings", index)

# Before conducting a search or a query, you need to load the data in `hello_milvus` into memory.
print(fmt.format("Start loading"))
clap_db.load()

#################################################################################
# search based on vector similarity
        
def search(vectors_to_search, limit=3):

    print(fmt.format("Start searching based on vector similarity"))
 
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }

    start_time = time.time()
    result = clap_db.search(vectors_to_search, "embeddings", search_params, limit, output_fields=["random"])
    end_time = time.time()

    for hits in result:
        for hit in hits:
            print(f"hit: {hit}, random field: {hit.entity.get('random')}")
    print(search_latency_fmt.format(end_time - start_time))
