#!/bin/bash

# CallQualityHub Quickstart Script
# Bu script projeyi hızlı bir şekilde kurmak için kullanılır

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "🚀 CallQualityHub Quickstart"
    echo "=================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python version
    if ! python3 --version >/dev/null 2>&1; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
        print_error "Python 3.9+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    # Check PostgreSQL
    if ! command -v psql >/dev/null 2>&1; then
        print_warning "PostgreSQL client not found. Please install PostgreSQL."
        echo "Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
        echo "macOS: brew install postgresql"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check Git
    if ! command -v git >/dev/null 2>&1; then
        print_error "Git is required but not installed."
        exit 1
    fi
}

setup_environment() {
    print_step "Setting up virtual environment..."
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_step "Virtual environment created and activated"
}

install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Install requirements
    pip install -r requirements.txt
    
    print_step "Dependencies installed successfully"
}

setup_env_file() {
    print_step "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        cp .env-sample .env
        
        # Generate a secret key
        SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        
        # Update .env file
        sed -i.bak "s/django-insecure-key-replace-in-production-with-strong-random-key/$SECRET_KEY/" .env
        
        print_step "Environment file created with generated SECRET_KEY"
        print_warning "Please update database credentials in .env file"
    else
        print_warning ".env file already exists, skipping..."
    fi
}

setup_database() {
    print_step "Setting up database..."
    
    # Load environment variables
    source .env
    
    # Create database if PostgreSQL is available
    if command -v createdb >/dev/null 2>&1; then
        createdb ${DB_NAME:-qualityhub} 2>/dev/null || echo "Database may already exist"
    fi
    
    # Run migrations
    python manage.py migrate
    
    print_step "Database setup completed"
}

create_superuser() {
    print_step "Creating superuser..."
    
    echo "Please create an admin user:"
    python manage.py createsuperuser
    
    print_step "Superuser created successfully"
}

setup_static_files() {
    print_step "Collecting static files..."
    
    python manage.py collectstatic --noinput
    
    print_step "Static files collected"
}

final_setup() {
    print_step "Final setup steps..."
    
    # Create media directories
    mkdir -p media/call_records
    mkdir -p logs
    
    # Set permissions
    chmod 755 media/call_records
    chmod 755 logs
    
    print_step "Directory structure created"
}

show_completion_message() {
    echo
    echo -e "${GREEN}"
    echo "🎉 CallQualityHub setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Start the development server:"
    echo "   python manage.py runserver"
    echo
    echo "2. Open your browser and visit:"
    echo "   http://127.0.0.1:8000"
    echo
    echo "3. Login with your admin credentials"
    echo
    echo "4. Start using CallQualityHub!"
    echo -e "${NC}"
}

# Main execution
main() {
    print_header
    
    check_requirements
    setup_environment
    install_dependencies
    setup_env_file
    setup_database
    create_superuser
    setup_static_files
    final_setup
    show_completion_message
}

# Check if running in CI environment
if [[ "${CI}" == "true" ]]; then
    print_warning "Running in CI environment, skipping interactive setup"
    exit 0
fi

# Run main function
main 