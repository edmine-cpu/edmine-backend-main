#!/bin/bash

# Script to run tests for Edmine Backend
# Usage: ./run_tests.sh [options]
#
# Options:
#   -v, --verbose       Run tests with verbose output
#   -c, --coverage      Run tests with coverage report
#   -m, --module NAME   Run tests for specific module (blog, company, bids, user, admin)
#   -f, --fast          Run tests without coverage
#   -h, --help          Show this help message

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default options
VERBOSE=""
COVERAGE=""
MODULE=""
FAST=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=. --cov-report=html --cov-report=term"
            shift
            ;;
        -m|--module)
            MODULE="$2"
            shift 2
            ;;
        -f|--fast)
            FAST=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose       Run tests with verbose output"
            echo "  -c, --coverage      Run tests with coverage report"
            echo "  -m, --module NAME   Run tests for specific module (blog, company, bids, user, admin)"
            echo "  -f, --fast          Run tests without coverage"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install dependencies with: pip install -r requirements-dev.txt"
    exit 1
fi

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment is not activated${NC}"
    echo "Consider activating it with: source .venv/bin/activate"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if test database exists
echo -e "${YELLOW}Checking test database...${NC}"
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw makeasap_test; then
    echo -e "${GREEN}Test database 'makeasap_test' exists${NC}"
else
    echo -e "${YELLOW}Test database 'makeasap_test' does not exist${NC}"
    read -p "Create test database? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        createdb -U postgres makeasap_test
        echo -e "${GREEN}Test database created${NC}"
    else
        echo -e "${RED}Cannot run tests without test database${NC}"
        exit 1
    fi
fi

# Build test command
TEST_CMD="pytest"

if [[ -n "$VERBOSE" ]]; then
    TEST_CMD="$TEST_CMD $VERBOSE"
fi

if [[ -n "$COVERAGE" ]] && [[ "$FAST" == false ]]; then
    TEST_CMD="$TEST_CMD $COVERAGE"
fi

if [[ -n "$MODULE" ]]; then
    TEST_FILE="tests/test_${MODULE}.py"
    if [[ ! -f "$TEST_FILE" ]]; then
        echo -e "${RED}Error: Test file '$TEST_FILE' not found${NC}"
        echo "Available modules: blog, company, bids, user, admin"
        exit 1
    fi
    TEST_CMD="$TEST_CMD $TEST_FILE"
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
echo "Command: $TEST_CMD"
echo ""

$TEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"

    if [[ -n "$COVERAGE" ]]; then
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
