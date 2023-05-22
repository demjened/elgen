from argparse import ArgumentParser
from elasticsearch import Elasticsearch, helpers
from faker import Faker
import json
import time
import os

fake = Faker()

global OPTIONS

def print_debug(msg: str):
    if OPTIONS.debug:
        print(f"DEBUG: {msg}")

def print_error(msg: str):
    print(f"❗ ERROR: {msg}")

def print_warning(msg: str):
    print(f"⚠️ WARNING: {msg}")


def clear_index(es_client: Elasticsearch):
    if OPTIONS.clear_index:
        print(f"💣 Clearing index {OPTIONS.index}")
        es_client.delete_by_query(index=OPTIONS.index, query={"match_all": {}})


def bulk_index_docs(docs, es_client: Elasticsearch):
    actions = []
    for doc in docs:
        actions.append({
            "_op_type": "index",
            "_index": OPTIONS.index,
            "_id": doc["id"],
            "_source": doc,
            "pipeline": OPTIONS.index,
        })

    print_debug(f"Indexing {len(docs)} documents to {OPTIONS.index}...")

    helpers.bulk(es_client, actions)


def write_docs(docs, out_file):
    print_debug(f"Writing {len(docs)} documents to file...")

    for doc in docs:
        action = {"index": {"_index": OPTIONS.index, "_id": doc["id"]}}
        out_file.write(json.dumps(action) + "\n")
        out_file.write(json.dumps(doc) + "\n")


def generate_doc(size):
    paragraphs = []
    total_size = 300 # Start with approximate size of document without the "text" property
    while total_size < size:
        paragraph = fake.paragraph()
        total_size += len(paragraph)
        paragraphs.append(paragraph)

    doc = {
        "id": fake.uuid4(),
        "title": fake.sentence().replace(".", ""),
        "author": fake.name(),
        "summary": fake.text(max_nb_chars = 200),
        "text": "\n\n".join(paragraphs)
    }

    if not OPTIONS.skip_ml_inference:
        doc["_run_ml_inference"] = True

    return doc


def parse_args():
    global OPTIONS

    parser = ArgumentParser(description="Generate and index documents for benchmarking Elasticsearch.")

    parser.add_argument("-o", "--out-file", help="Output file.", type=str)
    parser.add_argument("-c", "--cloud-id", help="Elastic Cloud ID.",
                        type=str, default=os.getenv("ELASTIC_CLOUD_ID"))
    parser.add_argument("-u", "--elastic-username", help="Elastic username. (Default 'elastic')",
                        type=str, default=os.getenv("ELASTIC_USERNAME", "elastic"))
    parser.add_argument("-p", "--elastic-password", help="Elastic password.",
                        type=str, default=os.getenv("ELASTIC_PASSWORD"))
    parser.add_argument("-i", "--index", help="Target Elasticsearch index.", type=str)
    parser.add_argument("-x", "--clear-index", help="Clear index before indexing documents.",
                        default=False, action="store_true")
    parser.add_argument("-q", "--pipeline", help="Target inference pipeline name. (Default is same as index name)",
                        type=str)
    parser.add_argument("-m", "--skip-ml-inference", help="Skip Machine Learning inference on documents.",
                        default=False, action="store_true")
    parser.add_argument("-l", "--limit", help="Number of documents to generate. (Default 10)",
                        type=int, default=10)
    parser.add_argument("-s", "--size", help="Approximate size of the documents in bytes. (Default 1000)",
                        type=int, default=1000)
    parser.add_argument("-b", "--batch-size", help="Batch size for bulk generation and indexing. (Default 50)",
                        type=int, default=50)
    parser.add_argument("-d", "--debug", help="Enable debug mode.", default=False, action="store_true")

    OPTIONS = parser.parse_args()

    OPTIONS.pipeline = OPTIONS.pipeline or OPTIONS.index


def validate_args():
    if OPTIONS.cloud_id is not None and (OPTIONS.elastic_username is None or OPTIONS.elastic_password is None):
        print_error("Elastic username and password are required when using Elastic Cloud")
        exit(1)

    if OPTIONS.cloud_id is not None and OPTIONS.index is None:
        print_error("Index name is required when using Elastic Cloud")
        exit(1)

    if OPTIONS.size < 300:
        print_error("Minimum document size is 300 bytes")
        exit(1)
    
    if OPTIONS.limit < 1:
        print_error("Limit must be greater than 0")
        exit(1)

    if OPTIONS.batch_size < 1:
        print_error("Batch_size must be greater than 0")
        exit(1)
    elif OPTIONS.batch_size > 100 and OPTIONS.cloud_id is not None:
        print_warning("It is not recommended to set batch_size over 100 when indexing on Elastic Cloud, due to potential timeouts")


def process_batch_of_docs(batch_size, out_file, es_client):
    print(f"⚙️ Generating {batch_size} documents")

    docs = []
    for _ in range(0, batch_size):
        docs.append(generate_doc(OPTIONS.size))

    if out_file is None and es_client is None:
        for doc in docs:
            print(json.dumps(doc, indent=4))
    if out_file is not None:
        write_docs(docs, out_file)
    if es_client is not None:
        bulk_index_docs(docs, es_client)


def process():
    out_file = None
    es_client = None
    if OPTIONS.out_file:
        print(f"💾 Writing documents to {OPTIONS.out_file}")
        out_file = open(OPTIONS.out_file, "w")
    if OPTIONS.cloud_id:
        es_client = Elasticsearch(cloud_id=OPTIONS.cloud_id, basic_auth=(OPTIONS.elastic_username, OPTIONS.elastic_password),
                                  http_compress=True, request_timeout=180, retry_on_timeout=True, max_retries=10)

        clear_index(es_client)

        short_cloud_id = OPTIONS.cloud_id[:OPTIONS.cloud_id.index(":") + 6]
        print(f"📒 Indexing documents to index {OPTIONS.index} on Elastic Cloud {short_cloud_id}(...)")
        if OPTIONS.skip_ml_inference:
            print("✖️ NOT applying Machine Learning inference on documents")

    start_time = time.time()
    total_duration = 0

    remaining = OPTIONS.limit
    while remaining > 0:
        batch_size = min(OPTIONS.batch_size, remaining)
        process_batch_of_docs(batch_size, out_file, es_client)
        remaining -= batch_size

        total_duration = time.time() - start_time
        avg_throughput = (OPTIONS.limit - remaining) / total_duration

        print_debug(f"""Indexed {OPTIONS.limit - remaining}/{OPTIONS.limit} documents
Rolling average throughput: {round(avg_throughput, 3)} docs/sec""")

    print(f"""✅ DONE - Processed {OPTIONS.limit} documents of ~{OPTIONS.size} bytes each
Total duration: {round(total_duration, 3)} seconds
Average throughput: {round(avg_throughput, 3)} docs/sec""")

    if out_file is not None:
        print_debug(f"Closing {OPTIONS.out_file}")
        out_file.close()
    if es_client is not None:
        print_debug("Closing Elasticsearch client")
        es_client.close()


if __name__ == "__main__":
    parse_args()
    validate_args()
    process()
