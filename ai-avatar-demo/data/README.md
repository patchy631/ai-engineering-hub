# Zep Documentation Data Directory

This directory contains the (sample) data used for the Zep knowledge graph.

## Files

- **chunked-docs.json** - Sample chunked data provided for ingestion into the Zep knowledge graph.

## Using Your Own Data

If you want to use your own data, you must generate a `chunked-docs.json` file with a similar structure to the provided sample. Ensure the file is formatted correctly for ingestion.

## Ingesting the Data

To ingest the `chunked-docs.json` file into the Zep knowledge graph:

```bash
python scripts/ingest_to_graph.py
```

After running the script, make sure to check the Zep dashboard and wait a few minutes for the data to be fully processed and available for use.
