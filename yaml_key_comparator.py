#!/usr/bin/env python3
"""YAML key comparator - finds common keys across multiple YAML files.

Compares keys (content before ':') across multiple YAML files and outputs
only the matching keys to a new file.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Set, List

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_keys(data: any, prefix: str = '') -> Set[str]:
    """Recursively extract all keys from nested YAML structure.
    
    Args:
        data: YAML data structure (dict, list, or scalar)
        prefix: Current key path prefix for nested structures
        
    Returns:
        Set of all keys found in the structure
    """
    keys = set()
    
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            keys.update(extract_keys(value, full_key))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            keys.update(extract_keys(item, f"{prefix}[{idx}]"))
    
    return keys


def load_yaml_keys(file_path: Path) -> Set[str]:
    """Load YAML file and extract all keys.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Set of keys found in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data is None:
                logger.warning(f"Empty YAML file: {file_path}")
                return set()
            return extract_keys(data)
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {file_path}: {e}")
        raise
    except (OSError, IOError) as e:
        logger.error(f"Cannot read {file_path}: {e}")
        raise


def find_common_keys(yaml_files: List[Path]) -> Set[str]:
    """Find keys that exist in all provided YAML files.
    
    Args:
        yaml_files: List of YAML file paths
        
    Returns:
        Set of common keys across all files
    """
    if not yaml_files:
        return set()
    
    # Load keys from first file
    common_keys = load_yaml_keys(yaml_files[0])
    logger.info(f"Loaded {len(common_keys)} keys from {yaml_files[0].name}")
    
    # Intersect with keys from remaining files
    for yaml_file in yaml_files[1:]:
        file_keys = load_yaml_keys(yaml_file)
        logger.info(f"Loaded {len(file_keys)} keys from {yaml_file.name}")
        common_keys &= file_keys
        logger.debug(f"Common keys after {yaml_file.name}: {len(common_keys)}")
    
    return common_keys


def write_output(output_file: Path, common_keys: Set[str], format_type: str = 'list') -> None:
    """Write common keys to output file.
    
    Args:
        output_file: Path to output file
        common_keys: Set of common keys to write
        format_type: Output format ('list', 'yaml', or 'json')
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if format_type == 'yaml':
                # Write as YAML list
                yaml.dump(sorted(common_keys), f, default_flow_style=False)
            elif format_type == 'json':
                # Write as JSON array
                import json
                json.dump(sorted(common_keys), f, indent=2)
            else:
                # Write as plain text list (one key per line)
                for key in sorted(common_keys):
                    f.write(f"{key}\n")
        
        logger.info(f"Wrote {len(common_keys)} common keys to {output_file}")
    except (OSError, IOError) as e:
        logger.error(f"Cannot write to {output_file}: {e}")
        raise


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Compare YAML files and find common keys',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s file1.yaml file2.yaml -o common_keys.txt
  %(prog)s config/*.yaml -o output.txt
  %(prog)s -f yaml app1.yml app2.yml app3.yml -o common.yaml
  %(prog)s --format json *.yaml -o keys.json

Output Formats:
  list  - Plain text, one key per line (default)
  yaml  - YAML list format
  json  - JSON array format
        '''
    )
    
    parser.add_argument(
        'yaml_files',
        nargs='+',
        help='YAML files to compare (minimum 2 files)'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file for common keys'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['list', 'yaml', 'json'],
        default='list',
        help='Output format (default: list)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress info messages'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        # Validate input files
        yaml_files = [Path(f).resolve() for f in args.yaml_files]
        
        if len(yaml_files) < 2:
            logger.error("At least 2 YAML files are required for comparison")
            return 1
        
        for yaml_file in yaml_files:
            if not yaml_file.exists():
                logger.error(f"File not found: {yaml_file}")
                return 1
            if not yaml_file.is_file():
                logger.error(f"Not a file: {yaml_file}")
                return 1
        
        logger.info(f"Comparing {len(yaml_files)} YAML files")
        
        # Find common keys
        common_keys = find_common_keys(yaml_files)
        
        if not common_keys:
            logger.warning("No common keys found across all files")
            # Still create empty output file
            Path(args.output).touch()
            return 0
        
        logger.info(f"Found {len(common_keys)} common keys")
        
        # Write output
        output_file = Path(args.output).resolve()
        write_output(output_file, common_keys, args.format)
        
        return 0
        
    except KeyboardInterrupt:
        logger.error("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
