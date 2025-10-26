# Country Currency & Exchange API

This is a Django REST Framework API that fetches country data from an external API, stores it in a database, and provides CRUD operations.

## Features

- Fetches country data from [REST Countries API](https://restcountries.com/)
- Fetches currency exchange rates from [ExchangeRate-API](https://www.exchangerate-api.com/)
- Caches the fetched data in a SQLite database
- Provides CRUD operations for the cached country data
- Generates and serves a summary image of the cached data

## Project Structure

```
.
├── Pipfile
├── Pipfile.lock
├── README.md
├── country_api
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── renderers.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── country_service
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

## Models

### `Country`

| Field               | Type        | Description                                                              |
| ------------------- | ----------- | ------------------------------------------------------------------------ |
| `name`              | `CharField` | The name of the country.                                                 |
| `capital`           | `CharField` | The capital of the country.                                              |
| `region`            | `CharField` | The region where the country is located.                                 |
| `population`        | `IntegerField`| The population of the country.                                           |
| `currency_code`     | `CharField` | The currency code of the country.                                        |
| `exchange_rate`     | `FloatField`  | The exchange rate of the country's currency against the USD.            |
| `estimated_gdp`     | `FloatField`  | The estimated GDP of the country.                                        |
| `flag_url`          | `URLField`    | The URL of the country's flag.                                          |
| `last_refreshed_at` | `DateTimeField`| The timestamp when the country data was last refreshed.                  |

### `Status`

| Field             | Type        | Description                                         |
| ----------------- | ----------- | --------------------------------------------------- |
| `last_refreshed_at` | `DateTimeField`| The timestamp when the country data was last refreshed. |
| `total_countries` | `IntegerField`| The total number of countries in the database.      |

## API Endpoints

### `POST /countries/refresh`

Fetches all countries and exchange rates from the external APIs and caches them in the database.

- **Method:** `POST`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:** `{"message": "Countries refreshed successfully"}`
- **Error Response:**
  - **Code:** 503 Service Unavailable
  - **Content:** `{"error": "External data source unavailable", "details": "<error-details>"}`

### `GET /countries`

Get a list of all countries from the database. Supports filtering and sorting.

- **Method:** `GET`
- **Query Parameters:**
  - `region` (optional): Filter by region (e.g., `?region=Africa`).
  - `currency` (optional): Filter by currency code (e.g., `?currency=NGN`).
  - `sort` (optional): Sort by GDP in descending order (e.g., `?sort=gdp_desc`).
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    [
      {
        "id": 1,
        "name": "Nigeria",
        "capital": "Abuja",
        "region": "Africa",
        "population": 206139589,
        "currency_code": "NGN",
        "exchange_rate": 1600.23,
        "estimated_gdp": 25767448125.2,
        "flag_url": "https://flagcdn.com/ng.svg",
        "last_refreshed_at": "2025-10-22T18:00:00Z"
      }
    ]
    ```

### `GET /countries/:name`

Get a single country by name.

- **Method:** `GET`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "id": 1,
      "name": "Nigeria",
      "capital": "Abuja",
      "region": "Africa",
      "population": 206139589,
      "currency_code": "NGN",
      "exchange_rate": 1600.23,
      "estimated_gdp": 25767448125.2,
      "flag_url": "https://flagcdn.com/ng.svg",
      "last_refreshed_at": "2025-10-22T18:00:00Z"
    }
    ```
- **Error Response:**
  - **Code:** 404 Not Found
  - **Content:** `{"detail": "No Country matches the given query."}`

### `DELETE /countries/:name`

Delete a country record from the database.

- **Method:** `DELETE`
- **Success Response:**
  - **Code:** 204 No Content
- **Error Response:**
  - **Code:** 404 Not Found
  - **Content:** `{"detail": "No Country matches the given query."}`

### `GET /status`

Show the total number of countries in the database and the last refresh timestamp.

- **Method:** `GET`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "total_countries": 250,
      "last_refreshed_at": "2025-10-22T18:00:00Z"
    }
    ```

### `GET /countries/image`

Serve a summary image of the cached data.

- **Method:** `GET`
- **Success Response:**
  - **Code:** 200 OK
  - **Content-Type:** `image/png`
  - **Content:** The summary image in PNG format.
- **Error Response:**
  - **Code:** 404 Not Found
  - **Content:** `{"error": "Summary image not found"}`

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    ```

2.  **Install dependencies:**

    ```bash
    pipenv install
    ```

3.  **Run migrations:**

    ```bash
    pipenv run python manage.py migrate
    ```

4.  **Start the development server:**

    ```bash
    pipenv run python manage.py runserver
    ```

## Running the API

1.  **Refresh the data:**

    Send a `POST` request to `/countries/refresh` to fetch and cache the data from the external APIs.

    ```bash
    curl -X POST http://127.0.0.1:8000/countries/refresh
    ```

2.  **Get all countries:**

    Send a `GET` request to `/countries` to get a list of all countries.

    ```bash
    curl http://127.0.0.1:8000/countries
    ```

3.  **Get a specific country:**

    Send a `GET` request to `/countries/:name` to get a single country by name.

    ```bash
    curl http://127.0.0.1:8000/countries/Nigeria
    ```

4.  **Delete a country:**

    Send a `DELETE` request to `/countries/:name` to delete a country.

    ```bash
    curl -X DELETE http://127.0.0.1:8000/countries/Nigeria
    ```

5.  **Get the status:**

    Send a `GET` request to `/status` to get the status of the database.

    ```bash
    curl http://127.0.0.1:8000/status
    ```

6.  **Get the summary image:**

    Send a `GET` request to `/countries/image` to get the summary image.

    ```bash
    curl http://127.0.0.1:8000/countries/image -o summary.png
    ```