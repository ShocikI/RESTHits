# RESTHits

A simple Django + Django REST Framework application for managing musical artists and their hits.  
It ships with:

- **Artists** with `first_name`, `last_name` and creation timestamp  
- **Hits** with `title`, auto-generated `title_url` (slug), timestamps, and a foreign key to **Artist**  
- A custom management command (`seed_data`) to populate the database with sample data  
- Docker support for easy local development

---

## 📚 Tech Stack

- **Python 3.13**  
- **Django 4.x**  
- **Django REST Framework**  
- **PostgreSQL 15** (via Docker)  
- **Docker & Docker Compose**

---

## 🚧 Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)  
- [Docker & Docker Compose](https://docs.docker.com/compose/install/) _(optional, but recommended)_  

---

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/ShocikI/RESTHits.git
cd RESTHits
```

### 2. Create & activate a virtual environment

```bash
python -m venv venv
source venn/bin/activate # Linux IoS
venv/Scripts/activate # Windows
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example and fill in you values:
```bash
cp .env.example .env
# then open .env and set:
#   DJANGO_SECRET_KEY=your_django_secret_key
#   POSTGRES_DB=...
#   POSTGRES_USER=...
#   POSTGRES_PASSWORD=...
#   POSTGRES_HOST=db
#   POSTGRES_PORT=5432
```

---

### 🐋 Docker (recommended)
If you have Docker installed, you can run everything in containers:

```bash
docker-compose up --build
```

This will start:

- A PostgreSQL container (`db`)
- The Django API container (api), which will automatically run:
  1. Migrations 
  2. Seeding data
  3. Serving at `0.0.0.0:8000`

Browse the API at http://localhost:8000/.

---

## 🔌 API Endpoints

- `GET  /api/v1/artists/` — List all artists  
- `POST /api/v1/artists/` — Create a new artist  
- `GET  /api/v1/artists/{id}/` — Retrieve a specific artist by ID  
- `PUT  /api/v1/artists/{id}/` — Update a specific artist  
- `DELETE /api/v1/artists/{id}/` — Delete a specific artist  

- `GET  /api/v1/hits/` — List all hits  
- `POST /api/v1/hits/` — Create a new hit (requires `artist_id` and `title`)  
- `GET  /api/v1/hits/{slug}/` — Retrieve a hit by its slug (`title_url`)  
- `PUT  /api/v1/hits/{slug}/` — Update a hit by slug  
- `DELETE /api/v1/hits/{slug}/` — Delete a hit by slug  

---

### 🧪 Running Tests

```bash
# with your virtualenv active
python manage.py test
```

All tests live in `hits/tests.py` and cover basic CRUD operations on yout models and serializers.