#!/bin/bash

echo "🚀 Starting PostgreSQL with Docker..."
echo ""

# Start PostgreSQL
docker-compose up -d

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ PostgreSQL is running!"
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "🔗 Connection details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: makeasap_dev"
    echo "  User: postgres"
    echo ""
    echo "💡 Useful commands:"
    echo "  Connect: psql -h localhost -U postgres -d makeasap_dev"
    echo "  Stop: docker-compose down"
    echo "  Logs: docker-compose logs -f postgres"
    echo ""
else
    echo "❌ Failed to start PostgreSQL!"
    echo "Check logs with: docker-compose logs postgres"
    exit 1
fi
