#!/usr/bin/env python3
"""DOS to Unix line ending converter script.

Converts Windows line endings (CRLF) to Unix line endings (LF) for files and directories.
Supports recursive processing and multiple file/folder arguments.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Common text file extensions to process
DEFAULT_EXTENSIONS = {
    '.txt', '.py', '.js', '.html', '.css', '.xml', '.json', '.yaml', '.yml',
    '.md', '.rst', '.sh', '.bat', '.ps1', '.sql', '.csv', '.log', '.conf',
    '.cfg', '.ini', '.properties', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.scala', '.pl', '.r'
}


def is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file based on extension and content."""
    if file_path.suffix.lower() in DEFAULT_EXTENSIONS:
        return True
    
    # Check if file appears to be text by reading first few bytes
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:  # Binary files often contain null bytes
                return False
            # Check if most bytes are printable ASCII or common UTF-8
            text_chars = sum(1 for byte in chunk if byte < 128 and (byte >= 32 or byte in [9, 10, 13]))
            return text_chars / len(chunk) > 0.75 if chunk else False
    except (OSError, IOError):
        return False


def convert_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Convert a single file from DOS to Unix line endings.
    
    Args:
        file_path: Path to the file to convert
        dry_run: If True, only check what would be converted
        
    Returns:
        Tuple of (success, message)
    """
    try:
        if not file_path.is_file():
            return False, f"Not a file: {file_path}"
            
        if not is_text_file(file_path):
            return False, f"Skipping binary file: {file_path}"
            
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Check if conversion is needed
        if b'\r\n' not in content:
            return True, f"No conversion needed: {file_path}"
            
        if dry_run:
            crlf_count = content.count(b'\r\n')
            return True, f"Would convert {crlf_count} CRLF sequences in: {file_path}"
            
        # Convert CRLF to LF
        converted_content = content.replace(b'\r\n', b'\n')
        
        # Write back the converted content
        with open(file_path, 'wb') as f:
            f.write(converted_content)
            
        crlf_count = content.count(b'\r\n')
        return True, f"Converted {crlf_count} CRLF sequences in: {file_path}"
        
    except (OSError, IOError) as e:
        return False, f"Error processing {file_path}: {e}"
    except Exception as e:
        return False, f"Unexpected error processing {file_path}: {e}"


def process_directory(dir_path: Path, recursive: bool = True, dry_run: bool = False) -> Tuple[int, int]:
    """Process all files in a directory.
    
    Args:
        dir_path: Path to directory
        recursive: Process subdirectories recursively
        dry_run: If True, only show what would be processed
        
    Returns:
        Tuple of (successful_files, failed_files)
    """
    successful = 0
    failed = 0
    
    try:
        if recursive:
            pattern = '**/*'
        else:
            pattern = '*'
            
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                success, message = convert_file(file_path, dry_run)
                if success:
                    successful += 1
                    logger.info(message)
                else:
                    failed += 1
                    logger.warning(message)
                    
    except Exception as e:
        logger.error(f"Error processing directory {dir_path}: {e}")
        failed += 1
        
    return successful, failed


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Convert DOS line endings (CRLF) to Unix line endings (LF)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s file.txt                    # Convert single file
  %(prog)s dir1/ file.txt dir2/        # Convert multiple files and directories
  %(prog)s -r project/                 # Convert directory recursively
  %(prog)s --dry-run -r project/       # Show what would be converted
  %(prog)s --extensions .py,.js src/   # Only process Python and JavaScript files
        '''
    )
    
    parser.add_argument(
        'paths',
        nargs='+',
        help='Files and/or directories to process'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process directories recursively (default: True for directories)'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not process directories recursively'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be converted without making changes'
    )
    
    parser.add_argument(
        '--extensions',
        help='Comma-separated list of file extensions to process (e.g., .py,.js,.txt)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress info messages, show only warnings and errors'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Handle custom extensions
    if args.extensions:
        global DEFAULT_EXTENSIONS
        custom_extensions = {ext.strip() for ext in args.extensions.split(',')}
        # Ensure extensions start with dot
        DEFAULT_EXTENSIONS = {ext if ext.startswith('.') else f'.{ext}' for ext in custom_extensions}
        logger.debug(f"Using custom extensions: {DEFAULT_EXTENSIONS}")
    
    # Determine recursive behavior
    recursive = not args.no_recursive if args.no_recursive else True
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be modified")
    
    total_successful = 0
    total_failed = 0
    
    try:
        for path_str in args.paths:
            path = Path(path_str).resolve()
            
            if not path.exists():
                logger.error(f"Path does not exist: {path}")
                total_failed += 1
                continue
                
            if path.is_file():
                success, message = convert_file(path, args.dry_run)
                if success:
                    total_successful += 1
                    logger.info(message)
                else:
                    total_failed += 1
                    logger.error(message)
                    
            elif path.is_dir():
                logger.info(f"Processing directory: {path} (recursive: {recursive})")
                successful, failed = process_directory(path, recursive, args.dry_run)
                total_successful += successful
                total_failed += failed
                
            else:
                logger.error(f"Unknown path type: {path}")
                total_failed += 1
        
        # Summary
        logger.info(f"Processing complete: {total_successful} successful, {total_failed} failed")
        
        if total_failed > 0:
            return 1
        return 0
        
    except KeyboardInterrupt:
        logger.error("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())