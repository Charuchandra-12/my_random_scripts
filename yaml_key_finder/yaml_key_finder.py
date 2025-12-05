#!/usr/bin/env python3
"""
YAML Key Finder - Production-grade script for searching YAML keys across directories.
Supports single key search or batch processing from key files.

USAGE GUIDE:
============

1. BASIC SINGLE KEY SEARCH:
   python yaml_key_finder.py --key "database" --directory ./configs
   python yaml_key_finder.py -k "api_key" -d /path/to/yamls

2. BATCH SEARCH FROM FILE:
   python yaml_key_finder.py --keys-file search_keys.txt --directory ./configs
   python yaml_key_finder.py -f keys.yml -d ./project

3. COMBINED SEARCH (single key + file):
   python yaml_key_finder.py -k "host" -f more_keys.txt -d ./configs

4. VERBOSE OUTPUT:
   python yaml_key_finder.py -k "port" -d ./configs --verbose
   python yaml_key_finder.py -f keys.txt -d ./configs -v

KEY FILE FORMATS:
================

Format 1 - Simple text (one key per line):
---
database
api_key
server.port
config.timeout
---

Format 2 - YAML list:
---
- database
- api_key  
- server.port
- config.timeout
---

Format 3 - YAML dictionary (searches keys only):
---
database: "will search for 'database' key"
api_key: "will search for 'api_key' key"
server:
  port: "will search for 'server' key"
---

SEARCH BEHAVIOR:
===============

• Recursively scans all subdirectories
• Processes .yml and .yaml files only
• Skips hidden directories (starting with .)
• Finds keys at ANY nesting level
• Reports exact path within YAML structure
• Shows value type for each found key

EXAMPLE YAML STRUCTURE:
======================

For this YAML file (config.yml):
---
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
api:
  - name: service1
    endpoint: /api/v1
  - name: service2
    endpoint: /api/v2
---

Searching for "host" will find:
• File: config.yml
• Path: database.host
• Type: str

Searching for "name" will find:
• File: config.yml  
• Path: api[0].name
• Type: str
• File: config.yml
• Path: api[1].name  
• Type: str

COMMAND LINE OPTIONS:
====================

Required:
  -d, --directory PATH    Target directory to search (must exist)

Search Input (at least one required):
  -k, --key STRING        Single key to search for
  -f, --keys-file PATH    File containing multiple keys

Optional:
  -v, --verbose          Enable debug logging with detailed output
  -h, --help            Show help message and exit

EXIT CODES:
===========
0   - Success (keys found or not found)
1   - Error (invalid arguments, file not found, etc.)
130 - Interrupted by user (Ctrl+C)

EXAMPLE SCENARIOS:
=================

1. Find database configuration:
   python yaml_key_finder.py -k "database" -d ./k8s-configs

2. Search for multiple API keys:
   echo -e "api_key\nauth_token\nsecret" > keys.txt
   python yaml_key_finder.py -f keys.txt -d ./helm-charts

3. Debug search with verbose output:
   python yaml_key_finder.py -k "nonexistent" -d ./configs -v

4. Search in current directory:
   python yaml_key_finder.py -k "version" -d .

5. Combine single key with file search:
   python yaml_key_finder.py -k "urgent_key" -f regular_keys.txt -d ./prod-configs
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Union, Optional
import yaml
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored log output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure structured logging with colored output."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

class YAMLKeyFinder:
    """Main class for YAML key searching operations."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.results: Dict[str, List[Dict]] = {}
    
    def load_keys_from_file(self, keys_file: Path) -> Set[str]:
        """Load search keys from file (one per line or YAML format)."""
        try:
            with open(keys_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # Try YAML format first
            try:
                data = yaml.safe_load(content)
                if isinstance(data, list):
                    return set(str(key) for key in data)
                elif isinstance(data, dict):
                    return set(data.keys())
            except yaml.YAMLError:
                pass
            
            # Fallback to line-by-line format
            return set(line.strip() for line in content.splitlines() if line.strip())
            
        except Exception as e:
            self.logger.error(f"Failed to load keys from {keys_file}: {e}")
            sys.exit(1)
    
    def search_yaml_keys(self, yaml_data: Dict, search_keys: Set[str], 
                        file_path: str, current_path: str = "") -> None:
        """Recursively search for keys in YAML data structure."""
        if not isinstance(yaml_data, dict):
            return
        
        for key, value in yaml_data.items():
            full_path = f"{current_path}.{key}" if current_path else key
            
            # Check if current key matches any search key
            if key in search_keys:
                result = {
                    'file': file_path,
                    'key_path': full_path,
                    'key': key,
                    'value_type': type(value).__name__
                }
                
                if key not in self.results:
                    self.results[key] = []
                self.results[key].append(result)
                
                self.logger.debug(f"Found key '{key}' at {file_path}:{full_path}")
            
            # Recursively search nested dictionaries
            if isinstance(value, dict):
                self.search_yaml_keys(value, search_keys, file_path, full_path)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self.search_yaml_keys(item, search_keys, file_path, f"{full_path}[{i}]")
    
    def process_yaml_file(self, file_path: Path, search_keys: Set[str]) -> None:
        """Process a single YAML file for key searches."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                self.logger.debug(f"Empty YAML file: {file_path}")
                return
            
            self.search_yaml_keys(yaml_data, search_keys, str(file_path))
            
        except yaml.YAMLError as e:
            self.logger.warning(f"Invalid YAML in {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
    
    def scan_directory(self, directory: Path, search_keys: Set[str]) -> None:
        """Recursively scan directory for YAML files."""
        yaml_extensions = {'.yml', '.yaml'}
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in yaml_extensions:
                        self.logger.debug(f"Processing: {file_path}")
                        self.process_yaml_file(file_path, search_keys)
                        
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            sys.exit(1)
    
    def print_results(self) -> None:
        """Display search results in formatted output."""
        if not self.results:
            print(f"{Fore.YELLOW}No matching keys found.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}=== YAML Key Search Results ==={Style.RESET_ALL}")
        
        for key, locations in self.results.items():
            print(f"\n{Fore.CYAN}Key: {key}{Style.RESET_ALL}")
            print(f"Found in {len(locations)} location(s):")
            
            for loc in locations:
                print(f"  📁 {loc['file']}")
                print(f"     Path: {loc['key_path']}")
                print(f"     Type: {loc['value_type']}")
        
        print(f"\n{Fore.GREEN}Total keys found: {len(self.results)}{Style.RESET_ALL}")

def validate_inputs(args) -> None:
    """Validate command line arguments."""
    if not args.directory.exists():
        print(f"{Fore.RED}Error: Directory '{args.directory}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)
    
    if not args.directory.is_dir():
        print(f"{Fore.RED}Error: '{args.directory}' is not a directory.{Style.RESET_ALL}")
        sys.exit(1)
    
    if args.keys_file and not args.keys_file.exists():
        print(f"{Fore.RED}Error: Keys file '{args.keys_file}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)
    
    if not args.key and not args.keys_file:
        print(f"{Fore.RED}Error: Either --key or --keys-file must be provided.{Style.RESET_ALL}")
        sys.exit(1)

def main():
    """Main entry point with argument parsing and execution flow."""
    parser = argparse.ArgumentParser(
        description="Search for YAML keys across directories and files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples:
  %(prog)s --key "database" --directory ./configs
  %(prog)s --keys-file keys.txt --directory ./helm-charts --verbose
  %(prog)s -k "api_key" -f more_keys.txt -d /path/to/yamls
  %(prog)s -k "host" -d . -v

For detailed usage guide, see the docstring at the top of this file.
        """
    )
    
    parser.add_argument('-k', '--key', type=str,
                       help='Single YAML key to search for')
    parser.add_argument('-f', '--keys-file', type=Path,
                       help='File containing keys to search (one per line or YAML list)')
    parser.add_argument('-d', '--directory', type=Path, required=True,
                       help='Target directory to search')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Validate inputs
    validate_inputs(args)
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Initialize finder
    finder = YAMLKeyFinder(logger)
    
    # Prepare search keys
    search_keys = set()
    if args.key:
        search_keys.add(args.key)
    if args.keys_file:
        search_keys.update(finder.load_keys_from_file(args.keys_file))
    
    logger.info(f"Searching for {len(search_keys)} key(s) in {args.directory}")
    logger.debug(f"Search keys: {', '.join(search_keys)}")
    
    # Execute search
    try:
        finder.scan_directory(args.directory, search_keys)
        finder.print_results()
        
    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()