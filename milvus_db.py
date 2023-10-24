from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import time
import numpy as np

fmt = "\n=== {:30} ===\n"
latency_fmt = "latency = {:.4f}s"
search_latency_fmt = "search latency = {:.4f}s"
DIM = 512

#################################################################################
# 1. connect to Milvus

print(fmt.format("start connecting to Milvus"))
connections.connect("default", host="localhost", port="19530")

has = utility.has_collection("clap_db")
print(f"Does collection clap_db exist in Milvus: {has}")

#utility.drop_collection("clap_db")

#################################################################################
# 2. create collection

fields = [
    FieldSchema(name="uuid", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
    FieldSchema(name="upid", dtype=DataType.VARCHAR, max_length=36),
    FieldSchema(name="product", dtype=DataType.VARCHAR, max_length=52),
    FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=70),
    FieldSchema(name="preview", dtype=DataType.VARCHAR, max_length=196),
    FieldSchema(name="vendor", dtype=DataType.VARCHAR, max_length=96, default_value=""),
    FieldSchema(name="bank1", dtype=DataType.VARCHAR, max_length=96, default_value=""),
    FieldSchema(name="bank2", dtype=DataType.VARCHAR, max_length=96, default_value=""),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64),
    FieldSchema(name="subcategory", dtype=DataType.VARCHAR, max_length=64),  
    FieldSchema(name="mode", dtype=DataType.VARCHAR, max_length=196),  
  
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=512),
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


#################################################################################
# insert data

def insert_items(entities):

    print(fmt.format("Start inserting entities"))

    start_time = time.time()
    insert_result = clap_db.insert(entities)
    clap_db.flush()
    end_time = time.time()

    print(latency_fmt.format(end_time - start_time))
    print(f"Number of entities in Milvus: {clap_db.num_entities}")  # check the num_entites
    print()

#################################################################################
# search based on vector similarity
        
def search_milvus_db(vectors_to_search, limit=10):

    print(fmt.format("Start searching based on vector similarity"))
 
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }

    start_time = time.time()
    search_result = clap_db.search(vectors_to_search, "embeddings", search_params, limit, output_fields=["uuid","upid","product","name","preview","vendor","bank1","bank2","category","subcategory","mode"])
    end_time = time.time()

    print(search_latency_fmt.format(end_time - start_time))

    result = []
    for hits in search_result:
        items = []
        for hit in hits:
            items.append ({ 'name': hit.entity.get('name'), 
                            'uuid': hit.entity.get('uuid'), 
                            'product': hit.entity.get('product'), 
                            'upid': hit.entity.get('upid'), 
                            'preview': hit.entity.get('preview'), 
                            'vendor': hit.entity.get('vendor'), 
                            'bank1': hit.entity.get('bank1'), 
                            'bank2': hit.entity.get('bank2'), 
                            'category': hit.entity.get('category'), 
                            'subcategory': hit.entity.get('subcategory'), 
                            'mode': hit.entity.get('mode'), 
                            'score':hit.score})
        result.append(items)

    return result

