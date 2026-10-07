# Student Management System

Flask + MySQL + HTML/CSS app with CRUD (add, view, edit, delete) and search.

## Run with Docker (recommended)
```bash
cp .env.example .env      # then edit passwords in .env
docker compose up --build
```
Open http://localhost:5000

Stop: `docker compose down` (add `-v` to wipe the database).

## Build / run the image manually
```bash
docker build -t student-management-system .
docker network create sms-net
docker run -d --name sms-db --network sms-net --env-file .env \
  -e MYSQL_DATABASE=studentdb -e MYSQL_USER=student \
  -e MYSQL_PASSWORD=$(grep DB_PASSWORD .env | cut -d= -f2) mysql:8.0
docker run -d --name sms-web --network sms-net --env-file .env -p 5000:5000 student-management-system
```

## Run locally (no Docker)
```bash
pip install -r requirements.txt
export DB_HOST=localhost DB_USER=root DB_PASSWORD=yourpass DB_NAME=studentdb
python app.py
```
(Create the `studentdb` database first; the table is created automatically.)

Secrets live in `.env`, which is git-ignored.
