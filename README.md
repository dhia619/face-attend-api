# Face-Attend-API

Backend API for face attendance that:

* Provides the main application API
* Uses PostgreSQL with `pgvector` as the database
* Uses DeepFace for face recognition
* Uses Alembic for database migrations

## Prerequisites

* Docker

* Docker Compose

## Setup

### 1. Configure environment variables

Rename `.env.example` to `.env` and fill in the required values.

```bash

cp  .env.example  .env

```

The `.env.example` file contains the variables required by the application, including database configuration and initial admin credentials.

### 2. Start the services 

```bash

docker  compose  up  --build

```

Services:
  
* API: `http://localhost:8000`

* DeepFace: `http://localhost:5005`

* PostgreSQL: `localhost:5432`

### 3. Apply database migrations

```bash

docker  compose  exec  api  alembic  upgrade  head

``` 

If this is a new project with no migration files yet, create the initial migration first:

```bash

docker  compose  exec  api  alembic  revision  --autogenerate  -m  "initial migration"

docker  compose  exec  api  alembic  upgrade  head

```

### 4. Seed the database

```bash

docker  compose  exec  api  python  -m  src.scripts.seed

```

This creates the default permissions, roles, and initial super admin if they do not already exist.
