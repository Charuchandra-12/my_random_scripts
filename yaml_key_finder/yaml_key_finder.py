#!/usr/bin/env python3
"""Find common keys between two YAML files."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Set

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_keys(data: any, prefix: str = '') -> Set[str]:
    """Extract all keys from YAML structure."""
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
    """Load file and extract keys (supports both YAML and plain text)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # Try to detect if it's plain text (one key per line)
            if not content:
                return set()
                
            # Check if it looks like plain text (no YAML structure indicators)
            if ':' not in content and '{' not in content and '[' not in content:
                # Plain text format - one key per line
                keys = set()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        keys.add(line)
                return keys
            
            # Try YAML parsing
            try:
                data = yaml.safe_load(content)
                return extract_keys(data) if data else set()
            except yaml.YAMLError:
                # If YAML parsing fails, treat as plain text
                keys = set()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        keys.add(line)
                return keys
                
    except (OSError, IOError) as e:
        logger.error(f"Cannot read {file_path}: {e}")
        raise


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description='Find common keys between two YAML files')
    parser.add_argument('file1', help='First YAML file')
    parser.add_argument('file2', help='Second YAML file')
    parser.add_argument('-o', '--output', required=True, help='Output file for common keys')
    
    args = parser.parse_args()
    
    try:
        file1 = Path(args.file1)
        file2 = Path(args.file2)
        output = Path(args.output)
        
        # Validate input files
        for f in [file1, file2]:
            if not f.exists():
                logger.error(f"File not found: {f}")
                return 1
        
        # Load keys from both files
        keys1 = load_yaml_keys(file1)
        keys2 = load_yaml_keys(file2)
        
        logger.info(f"Loaded {len(keys1)} keys from {file1.name}")
        logger.info(f"Loaded {len(keys2)} keys from {file2.name}")
        
        # Find common keys
        common_keys = keys1 & keys2
        
        if not common_keys:
            logger.info("No common keys found")
            output.touch()
            return 0
        
        # Write common keys to output file
        with open(output, 'w', encoding='utf-8') as f:
            yaml.dump(sorted(common_keys), f, default_flow_style=False)
        
        logger.info(f"Found {len(common_keys)} common keys, saved to {output}")
        return 0
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())