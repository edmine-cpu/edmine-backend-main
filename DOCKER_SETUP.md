# PostgreSQL Setup with Docker

## Quick Start

### 1. Start PostgreSQL

```bash
# Start PostgreSQL container in background
docker-compose up -d

# Check if container is running
docker-compose ps

# View logs
docker-compose logs postgres
```

### 2. Update .env file

Make sure your `.env` file has these settings:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_NAME=makeasap_dev
```

**Important:** Change `your_secure_password_here` to match the password in `docker-compose.yml`

### 3. Install Python dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirments.txt
```

### 4. Run migrations

```bash
# Initialize Aerich (only first time)
aerich init -t tortoise_config.TORTOISE_ORM

# Create initial migration (only first time)
aerich init-db

# Or if migrations already exist, just upgrade
aerich upgrade
```

### 5. Start your application

```bash
# Run the FastAPI application
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Useful Commands

### PostgreSQL Container Management

```bash
# Start container
docker-compose up -d

# Stop container
docker-compose down

# Restart container
docker-compose restart

# Stop and remove data (⚠️ WARNING: This deletes all data!)
docker-compose down -v

# View real-time logs
docker-compose logs -f postgres
```

### Database Access

```bash
# Connect to PostgreSQL from host
psql -h localhost -U postgres -d makeasap_dev

# Or connect via Docker
docker exec -it edmine_postgres psql -U postgres -d makeasap_dev

# Run SQL commands
docker exec -it edmine_postgres psql -U postgres -d makeasap_dev -c "SELECT * FROM users LIMIT 5;"
```

### Backup and Restore

```bash
# Create backup
docker exec edmine_postgres pg_dump -U postgres makeasap_dev > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker exec -i edmine_postgres psql -U postgres -d makeasap_dev < backup_20231201_120000.sql
```

## Troubleshooting

### Port already in use

If port 5432 is already taken:

```bash
# Check what's using the port
sudo lsof -i :5432

# Stop local PostgreSQL service
sudo systemctl stop postgresql

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use port 5433 on host instead

# Then update .env
DB_PORT=5433
```

### Container won't start

```bash
# Check logs
docker-compose logs postgres

# Remove old container and volumes
docker-compose down -v
docker-compose up -d
```

### Can't connect from application

1. Make sure container is running: `docker-compose ps`
2. Check DB_HOST in .env is `localhost` (not `0.0.0.0`)
3. Check password matches between .env and docker-compose.yml
4. Try connecting manually: `psql -h localhost -U postgres -d makeasap_dev`

## Production Recommendations

For production, consider:

1. Use environment variables instead of hardcoded passwords
2. Enable SSL connections
3. Set up regular backups
4. Use Docker secrets for sensitive data
5. Configure proper resource limits

Example with environment variables:

```yaml
environment:
  POSTGRES_PASSWORD: ${DB_PASSWORD}
```

Then set in shell before running:
```bash
export DB_PASSWORD=your_secure_password
docker-compose up -d
```
