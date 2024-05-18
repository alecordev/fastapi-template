# FastAPI Template

Example FastAPI.

## Structure

```
.
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── src
    └── api.py

1 directory, 5 files
```

## Usage

1. Create an environment
2. Install `requirements.txt`
3. Run `src/api.py`
4. API docs available in http://localhost:8081/api/v1/docs

## Working with conda?

1. `conda create -n api python=3.10`
2. `conda activate api`
3. `pip install -r requirements.txt`
4. `python src/api.py`

## Docker

1. `docker build -t api-template .`
2. `docker run -p 8081:8081 api-template`

- Force rebuild: `docker build -t api-template . --no-cache`
- Custom name: `docker run -d --name custom-api-template-name api-template`
- Custom name and open port: `docker run --name api-template -p 8081:8081 api-template`

## docker-compose

1. `docker-compose up` or `docker-compose up --build --force-recreate --no-deps`
2. `http://localhost:8081/`
3. `docker-compose down`

### Docker cleanup

- Single command: `docker container prune -f && docker image prune -a -f && docker volume prune -f && docker network prune -f`