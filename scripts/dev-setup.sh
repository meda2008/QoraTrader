#!/bin/bash
# QoraTrader Development Setup Script
# This script sets up a complete development environment

set -e  # Exit immediately if a command exits with a non-zero status

# Default configuration
ENVIRONMENT="development"
DOCKER_COMPOSE_FILE="docker/docker-compose.dev.yml"
ENV_FILE=".env.development"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Function to load environment variables
load_environment() {
    print_status "Loading environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE does not exist. Creating from template..."
        cat << EOF > "$ENV_FILE"
# QoraTrader Development Environment Configuration
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://qoratrader:qoratrader@localhost:5432/qoratrader
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=your-org
INFLUXDB_BUCKET=trading_data
REDIS_URL=redis://localhost:6379
DEBUG_MODE=true
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
EXCHANGE_API_KEY=your-exchange-api-key
EXCHANGE_API_SECRET=your-exchange-api-secret
EOF
        print_status "Environment file created: $ENV_FILE"
    fi
}

# Function to build services
build_services() {
    print_status "Building services..."
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" build
    else
        # If dev compose file doesn't exist, create a basic one
        print_warning "Development Docker Compose file does not exist. Creating a basic one..."
        cat << EOF > "$DOCKER_COMPOSE_FILE"
version: '3.8'

services:
  backend:
    build:
      context: ..
      dockerfile: docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://qoratrader:qoratrader@db:5432/qoratrader
      - INFLUXDB_URL=http://influxdb:8086
      - INFLUXDB_TOKEN=influxdb_token
      - INFLUXDB_ORG=org
      - INFLUXDB_BUCKET=bucket
      - DEBUG_MODE=true
    depends_on:
      - db
      - influxdb
    volumes:
      - ./backend:/app  # Mount for development
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ..
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app  # Mount for development
      - /app/node_modules  # Don't mount node_modules

  db:
    image: postgres:15
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data/
      - ./db/init:/docker-entrypoint-initdb.d
    environment:
      - POSTGRES_DB=qoratrader
      - POSTGRES_USER=qoratrader
      - POSTGRES_PASSWORD=qoratrader
    ports:
      - "5432:5432"

  influxdb:
    image: influxdb:2.7
    volumes:
      - influxdb_data_dev:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=influxdb_password
      - DOCKER_INFLUXDB_INIT_ORG=org
      - DOCKER_INFLUXDB_INIT_BUCKET=bucket
    ports:
      - "8086:8086"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data_dev:
  influxdb_data_dev:
EOF
        print_status "Development Docker Compose file created: $DOCKER_COMPOSE_FILE"
    fi
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    else
        print_error "Docker Compose file $DOCKER_COMPOSE_FILE does not exist."
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # For backend
    if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
    fi
    
    # For frontend
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        npm install
        cd ..
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait for database to be ready
    sleep 10
    
    # Run migrations
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python -m db.migrate || {
        print_warning "Could not run migrations. Database might already be initialized."
    }
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Check if backend is running
    local max_attempts=30
    local attempt=1
    local backend_ready=false
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_status "Backend service is ready"
            backend_ready=true
            break
        else
            print_status "Backend not ready, attempt $attempt/$max_attempts"
            sleep 10
        fi
        ((attempt++))
    done
    
    if [ "$backend_ready" = false ]; then
        print_error "Backend service did not start properly"
        exit 1
    fi
    
    print_status "Health checks completed successfully"
}

# Function to setup hot-reload for strategies
setup_hot_reload() {
    print_status "Setting up strategy hot-reload..."
    
    # In the development environment, strategies are mounted as volumes
    # This function would set up file watching for strategy changes in a real implementation
    print_status "Hot-reload is configured via Docker volume mounts"
}

# Main setup function
setup_dev_environment() {
    print_status "Starting QoraTrader development environment setup"
    
    check_prerequisites
    load_environment
    install_dependencies
    build_services
    start_services
    run_migrations
    run_health_checks
    setup_hot_reload
    
    print_status "Development environment setup completed successfully!"
    print_status "Services are available at:"
    print_status "  Backend API: http://localhost:8000"
    print_status "  Frontend UI: http://localhost:3000"
    print_status "  Database: http://localhost:5432"
    print_status "  InfluxDB: http://localhost:8086"
    print_status ""
    print_status "To access the services:"
    print_status "  - Backend container: docker-compose -f $DOCKER_COMPOSE_FILE exec backend bash"
    print_status "  - Frontend container: docker-compose -f $DOCKER_COMPOSE_FILE exec frontend bash"
    print_status "  - View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
}

# Function to stop development environment
stop_dev_environment() {
    print_warning "Stopping development environment..."
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        print_status "Development environment stopped"
    else
        print_error "Docker Compose file $DOCKER_COMPOSE_FILE does not exist."
        exit 1
    fi
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" restart
        print_status "Services restarted"
    else
        print_error "Docker Compose file $DOCKER_COMPOSE_FILE does not exist."
        exit 1
    fi
}

# Parse command line arguments
case "${1:-setup}" in
    setup)
        setup_dev_environment
        ;;
    stop)
        stop_dev_environment
        ;;
    restart)
        restart_services
        ;;
    *)
        echo "Usage: $0 [setup|stop|restart]"
        echo "  setup: Create and start the development environment"
        echo "  stop: Stop the development environment"
        echo "  restart: Restart all services"
        exit 1
        ;;
esac