# elgen - Elasticsearch data generator and indexer

**elgen** is a sample data generator and indexer for Elasticsearch on Elastic Cloud.

```
❯ python elgen.py --index my-index --clear-index --limit 200 --size 10000

💣 Clearing index my-index
📒 Indexing documents to index my-index on Elastic Cloud my-cloud:dXMtd(...)
🪄 Generating 50 documents
🪄 Generating 50 documents
🪄 Generating 50 documents
🪄 Generating 50 documents
✅ DONE - Processed 200 documents of ~10000 bytes each
Total duration: 4.018 seconds
Average throughput: 49.772 docs/sec
```

It uses [Faker](https://faker.readthedocs.io/) to create random documents that contain realistic data. The resulting dataset can be used to measure the throughput of Elastic bulk indexing and Machine Learning inference process.

A sample document looks like this:
```json
{
    "id": "5cd32827-2721-4d68-83b8-d1d0157c7501",
    "title": "There record happen charge experience available suggest",
    "author": "Steven Shannon",
    "summary": "Base reduce have affect able southern.\nQuestion sister stuff yet million. Especially few student before.",
    "text": "Stock PM way same green. (...) Every example end again live remember way."
}
```

## Requirements
* Python 3.6+
* [Elastic Cloud](https://www.elastic.co/cloud/) deployment (if you also want to index the data)

## Usage

Generate 10 documents and print them to the console in JSON format:
```sh
python elgen.py
```

Generate 100 documents of approximately 50 KB each:
```sh
python elgen.py --limit 100 --size 50000
```

Generate documents and index them in `my-index` in the specified Elastic Cloud deployment:
```sh
python elgen.py --index my-index --elastic-cloud-id my-cloud:... --elastic-username john --elastic-password doe123
```

Same as above, also run the documents through the `my-pipeline` ingest pipeline before indexing (see [Ingest pipeline](#ingest-pipeline)):
```sh
python elgen.py --index my-index --pipeline my-pipeline --elastic-cloud-id my-cloud:... --elastic-username john --elastic-password doe123
```

Generate documents and save them to `data.ndjson` for [bulk indexing](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) in Elasticsearch:
```sh
python elgen.py --out-file data.ndjson
```

See further options in [Configuration](#configuration).

## Ingest pipeline

By default elgen bulk indexes documents into the specified index. If an ingest pipeline is attached to the index, it can be applied during the indexing process by specifying it with the `--pipeline` option. It will also set the `_run_ml_inference` flag, which will run any Machine Learning inference pipelines.

To learn more about ingest and inference pipelines please refer to the [Enterprise Search guide](https://www.elastic.co/guide/en/enterprise-search/current/ingest-pipelines.html).

## Configuration

Optional arguments:

| Argument | Effect | Notes |
|---|---|---|
| `-o`, `--out-file` | Output file | NDJSON file containing [bulk index actions](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) ||
| `-c`, `--cloud-id` | Elastic Cloud ID | See also [Environment variables](#environment-variables) |
| `-u`, `--elastic-username` | Elastic username | Default: elastic<br/>See also [Environment variables](#environment-variables) |
| `-p`, `--elastic-password` | Elastic password | See also [Environment variables](#environment-variables) |
| `-i`, `--index` | Target Elasticsearch index ||
| `-x`, `--clear-index` | Clear index before indexing documents |
| `-l`, `--limit` | Number of documents to generate | Default: 10 |
| `-q`, `--pipeline` | Ingest pipeline name | See [Ingest pipeline](#ingest-pipeline) |
| `-s`, `--size` | Approximate size of the documents in bytes | Default: 1000 |
| `-b`, `--batch-size` | Batch size for bulk generation and indexing | Default: 50 |
| `-d`, `--debug` | Enable debug logging ||
| `-h`, `--help` | Show help message and exit ||

## Environment variables

* `ELASTIC_CLOUD_ID` - Elastic Cloud ID. If set, it will be automatically passed in `--elastic-cloud-id`.
* `ELASTIC_USERNAME` - Elastic username. If set, it will be automatically passed in `--elastic-username`.
* `ELASTIC_PASSWORD` - Elastic password. If set, it will be automatically passed in `--elastic-password`.

