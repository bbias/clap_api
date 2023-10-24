from pymilvus import (
    connections,
    utility,
)

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

#################################################################################
# 2. delete collection
utility.drop_collection("clap_db")
