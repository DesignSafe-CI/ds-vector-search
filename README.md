# Demo: DesignSafe Publication Vector Search
## Overview
This is a runnable proof-of-concept to demonstrate semantic search for DesignSafe publications. The tree representation for each publication is converted to a natural-language description, which is embedded using the `nomic-embed-text` model via ollama and stored in a ChromaDB collection. Search is performed by embedding a query string and finding similar vectors in the database.

## Running the Demo
The demo is packaged as a Jupyter notebook with the embedding model and vector database served via docker-compose. To run it:
1. Navigate to the repository root.
2. Run `docker compose build`
3. Run `docker compose up`
4. Navigate to http://localhost:8888/lab/tree/notebook.ipynb in your browser and run the Jupyter notebook that is served.

## References
- nomic-embed-text model: https://ollama.com/library/nomic-embed-text
- ollama docker image: https://hub.docker.com/r/ollama/ollama
- ChromaDB vector database: https://docs.trychroma.com/docs/overview/introduction