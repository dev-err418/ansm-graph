# Medicaments API

A GraphQL API for accessing and querying French medication data from the public database (base-donnees-publique.medicaments.gouv.fr).

## Features

- GraphQL API for querying medication data
- Automatic data download and parsing from the official source
- Support for various filters and pagination
- ANSM content scraping
- Data indexing for efficient queries

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
├── app.py              # Main GraphQL API application
├── autocomplete.py     # Autocomplete functionality
├── bdm_client.py      # Client for downloading medication data
├── bdm_file_parser.py # Parser for medication data files
├── bdm_files.py       # File definitions and schemas
├── filters.py         # Query filters implementation
├── index_builder.py   # Data indexing functionality
├── scrapper.py        # ANSM content scraper
└── utils.py           # Utility functions
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Access the GraphQL playground at `http://localhost:8000`

## API Endpoints

The API provides the following main queries:

- `medicaments`: Query medication information
- `substances`: Query active substances
- `presentations`: Query medication presentations
- `groupes_generiques`: Query generic groups
- `ansmContent`: Get ANSM content for a specific medication

### Example Query

```graphql
query {
  medicaments(
    limit: 10
    denomination: "PARACETAMOL"
  ) {
    CIS
    denomination
    forme_pharmaceutique
    substances {
      denomination
    }
  }
}
```

## Data Sources

The application uses data from:
- base-donnees-publique.medicaments.gouv.fr
- ANSM (Agence nationale de sécurité du médicament et des produits de santé)

## Dependencies

- ariadne: GraphQL implementation
- aiohttp: Async HTTP client
- beautifulsoup4: HTML parsing
- uvicorn: ASGI server

## Development

To modify the GraphQL schema, edit the `schema.graphql` file and update the corresponding resolvers in `app.py`.
