# Sales Analytics Agent

This project demonstrates how to connect **MongoDB** and **HubSpot** in MindsDB, query across them with SQL, and use an **AI agent** over the same data. The full workflow — from creating datasources and running cross-database queries to creating and querying a sales analytics agent via SQL or the Python SDK — is covered in `QUERY.md` and `main.py`.

---

## Setup and installations

**Get API Keys / credentials**:

- **HubSpot** — access token for the HubSpot integration. Used when creating the `hubspot_data` database.
- **OpenAI** — API key for the AI agent. Used in the `CREATE AGENT` step.
- **MongoDB** — a demo connection string is used in `QUERY.md` for the MongoDB datasource; replace with your own if needed.

Note: We have provided HubSpot and MongoDB datasources from our end, so you can skip from creating them. Just use the ones we have provided.

**Install dependencies**:

- **Docker** — required to run MindsDB. See [Get Docker](https://docs.docker.com/get-docker/).
- **Python** (optional, for SDK example) — Python 3.8 or later and `mindsdb_sdk`:
  ```bash
  pip install mindsdb_sdk
  ```

**Run the demo**:

1. Start MindsDB (HTTP API on port 47334, MySQL on 47335):
   ```bash
   docker run --name mindsdb_container \
     -e MINDSDB_APIS=http,mysql \
     -p 47334:47334 -p 47335:47335 \
     mindsdb/mindsdb:latest
   ```
2. Follow **`QUERY.md`** step-by-step. It covers:
   - Creating MongoDB and HubSpot databases in MindsDB
   - Displaying and querying data (single- and cross-database SQL)
   - Creating the `sales_agent` and querying it via SQL
3. Optionally run **`python main.py`** to stream agent completions using the MindsDB Python SDK.

---

## Stay updated with our newsletter

**Get a FREE Data Science eBook** with 150+ essential lessons in Data Science when you subscribe to our newsletter. Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now →](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
