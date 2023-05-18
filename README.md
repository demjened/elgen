# elgen - Elasticsearch data generator and indexer

**elgen** is a sample data generator and indexer for Elasticsearch.

```
❯ python elgen.py --index my-index --clear-index --limit 200 --size 10000

💣 Clearing index my-index
📒 Indexing documents to index my-index on Elastic Cloud my-cloud:dXMtd(...)
⚙️ Generating 50 documents
⚙️ Generating 50 documents
⚙️ Generating 50 documents
⚙️ Generating 50 documents
✅ DONE - Processed 200 documents of ~10000 bytes each
Total duration: 14.671 seconds
Average throughput: 13.702 docs/sec
```

It uses Faker to create documents that can be used to measure the throughput of Elastic bulk indexing and inference pipelines.

A sample document looks like this:
```json
{
    "id": "5cd32827-2721-4d68-83b8-d1d0157c7501",
    "title": "There record happen charge experience available suggest",
    "author": "Steven Shannon",
    "summary": "Base reduce have affect able southern.\nQuestion sister stuff yet million. Especially few student before.",
    "text": "Stock PM way same green. Down force your total him view.\n\nFear sister word performance. (...) Every example end again live remember way."
}
```

## Requirements
* Python 3.6+
* Elastic Cloud deployment (in case you want to index the data)

## Usage

Generate 10 documents and print them to the console in JSON format:
```sh
python elgen.py
```

Generate 100 documents of approximately 50KB each:
```sh
python elgen.py --size 50000 --limit 100
```

Generate documents and save them to `data.ndjson` for bulk indexing in Elasticsearch:
```sh
python elgen.py --out-file data.ndjson
```

Generate documents and index them in `my-index` in the specified Elastic Cloud deployment:
```sh
python elgen.py --index my-index --elastic-cloud-id my-cloud:... --elastic-username john --elastic-password doe123
```

See further options in [Configuration](#configuration).

## Configuration

```
  -h, --help            show this help message and exit
  -i INDEX, --index INDEX
                        Target Elasticsearch index.
  -q PIPELINE, --pipeline PIPELINE
                        Target inference pipeline name. (Default is same as index name)
  -o OUT_FILE, --out-file OUT_FILE
                        Output file.
  -c CLOUD_ID, --cloud-id CLOUD_ID
                        Elastic Cloud ID.
  -u ELASTIC_USERNAME, --elastic-username ELASTIC_USERNAME
                        Elastic username. (Default 'elastic')
  -p ELASTIC_PASSWORD, --elastic-password ELASTIC_PASSWORD
                        Elastic password.
  -x, --clear-index     Clear index before indexing documents.
  -m, --skip-ml-inference
                        Skip Machine Learning inference on documents.
  -s SIZE, --size SIZE  Approximate size of the documents in bytes. (Default 1000)
  -l LIMIT, --limit LIMIT
                        Number of documents to generate. (Default 10)
  -b BATCH_SIZE, --batch-size BATCH_SIZE
                        Batch size for bulk generation and indexing. (Default 50)
  -d, --debug           Enable debug mode.
```

## Environment variables

* `ELASTIC_CLOUD_ID` - Elastic Cloud ID. If set, it will be automatically passed in `--elastic-cloud-id`.
* `ELASTIC_USERNAME` - Elastic username. If set, it will be automatically passed in `--elastic-username`.
* `ELASTIC_PASSWORD` - Elastic password. If set, it will be automatically passed in `--elastic-password`.

