# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of utility scripts and tools for various development tasks, with a focus on:

- System installation and configuration scripts (Docker, MySQL, Python environments)
- Web scraping utilities (Korean online bookstore ranking scraper)
- Database utilities (MySQL to YAML dump tool)
- Git workflow automation scripts
- Infrastructure management scripts

## Python Environment

늘 가상환경을 활성화 하세요.

```
source .venv/bin/activate
```

### Project Configuration

- **Package Manager**: Uses `uv` for dependency management (pyproject.toml + uv.lock)
- **Python Version**: Requires Python >= 3.12
- **Key Dependencies**: httpx, beautifulsoup4

### Running Python Code

```bash
# Install dependencies
uv sync

# Run the main script
python main.py

# Run specific utilities
python py/scrap_books.py
python utils/dump_to_yaml.py <table_name>
```

## Key Components

### Web Scraping (py/scrap_books.py)

- **BookRankingScraper**: Comprehensive scraper for Korean bookstore rankings
- Targets: 교보문고 (Kyobobook), YES24, 알라딘 (Aladin)
- Features: Async HTTP requests, robust pattern matching, JSON output
- Usage: Modify URLs in main() function for different books

### Database Utilities (utils/dump_to_yaml.py)

- **MySQL to YAML converter**: Exports database table data to YAML format
- Requires PyMySQL connection configuration at line 12
- Usage: `python utils/dump_to_yaml.py <database.table> [where_clause]`

### Installation Scripts (install/)

- Collection of system setup scripts for Ubuntu/macOS
- Includes: Docker, MySQL, Python environments, development tools
- Each script is standalone and can be executed directly

## Common Development Tasks

### Adding New Scripts

- Place standalone scripts in appropriate subdirectories (install/, git/, docker/, etc.)
- For Python utilities, use the py/ directory
- Follow existing patterns for error handling and user feedback

### Working with the Book Scraper

- URLs are hardcoded in main() function - modify for different books
- Debug mode available via BookRankingScraper(debug=True)
- Results automatically saved as timestamped JSON files

### Database Operations

- Update MySQL connection parameters in utils/dump_to_yaml.py:12 before use
- Script handles both full table dumps and conditional exports

## Repository Structure

```
scripts/
├── py/                    # Python utilities and scrapers
├── utils/                 # Database and data processing tools
├── install/               # System installation scripts
├── git/                   # Git workflow automation
├── docker/                # Docker-related utilities
├── aws/                   # AWS deployment documentation
├── remove/                # System cleanup scripts
└── secure/                # Security and certificate tools
```
