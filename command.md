# Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

# Install the required dependencies by running:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

# Running Docker
```bash 
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  agnohq/pgvector:16
```

# Install pgadmin4
```bash
brew install --cask pgadmin4
```

# Running
```bash
source .env
uvicorn main:app --reload    
```