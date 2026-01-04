#!/usr/bin/env python3
"""
Python script to list or copy DROID data from Google Cloud Storage.

Examples:
    # List first 5 folders:
    python copy_droid_data.py -m list \
        -s "gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/" \
        -n 5

    # Download first 3 folders to 'mydroiddata' dir:
    python copy_droid_data.py -m copy \
        -s "gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/" \
        -d "mydroiddata/dataset/droid_raw/1.0.1/GuptaLab/success/2023-04-20" \
        -n 3
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the output.
    
    Args:
        cmd (str): Shell command to execute, e.g., 'gsutil ls gs://bucket/path/'
        check (bool): Whether to raise exception on non-zero exit code (default: True)
    
    Returns:
        tuple: (stdout, stderr, returncode)
    
    Example:
        stdout, stderr, code = run_command('gsutil ls gs://my-bucket/', check=True)
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error message: {e.stderr}")
        sys.exit(1)


def list_trajectories(source_bucket, count, python_path=None):
    """List the first N trajectories from the source bucket.
    
    Args:
        source_bucket (str): GCS bucket path, e.g., 'gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/'
        count (int): Number of trajectories to list, e.g., 5
    
    Returns:
        list: List of trajectory paths
    
    Example:
        trajectories = list_trajectories(
            'gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/',
            5
        )
    """
    print(f"Listing first {count} items from: {source_bucket}")
    print("-" * 48)
    
    cmd = f'gsutil ls "{source_bucket}" | head -n {count}'
    if python_path:
        cmd = f'CLOUDSDK_PYTHON={python_path} gsutil ls "{source_bucket}" | head -n {count}'
    print(f"Running command: {cmd}")
    stdout, stderr, returncode = run_command(cmd)
    # print("-" * 48)
    # print("stdout:", stdout)
    # print("stderr:", stderr)
    # print("returncode:", returncode)
    if stdout:
        print(stdout)
        return stdout.strip().split('\n')
    else:
        print("No items found.")
        return []


def copy_trajectories(source_bucket, dest_dir, python_path=None):
    """Download trajectories from GCS to local directory.
    
    Args:
        source_bucket (str): GCS bucket path, e.g., 'gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/'
        dest_dir (str): Local destination directory, e.g., 'mydroiddata/dataset/droid_raw/1.0.1/GuptaLab/success/2023-04-20'
    
    Example:
        copy_trajectories(
            'gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/',
            'mydroiddata/dataset/droid_raw/1.0.1/GuptaLab/success/2023-04-20'
        )
    """
    print(f"Preparing to download trajectories...")
    print(f"Source: {source_bucket}")
    print(f"Dest:   {dest_dir}")

    rsync_cmd = f'gsutil -m rsync -r -x ".*\\.svo$" "{source_bucket}" "{dest_dir}"'
    if python_path:
        rsync_cmd = f'CLOUDSDK_PYTHON={python_path} gsutil -m rsync -r -x ".*\\.svo$" "{source_bucket}" "{dest_dir}"'
    print(f"Running command: {rsync_cmd}")

    print("Creating destination directory if it doesn't exist...")
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    stdout, stderr, returncode = run_command(rsync_cmd, check=False)
    if returncode != 0:
        print(f"Warning: Some errors occurred during sync.")
        if stderr:
            print(f"Error details: {stderr}")
    else:
        print("Successfully synced trajectories.")
    print("Sync complete.")



def main():
    """Main function to parse arguments and execute the appropriate mode.
    
    Parses command-line arguments and calls either list_trajectories() or
    copy_trajectories() based on the mode.
    
    Example:
        # Called from command line:
        # python copy_droid_data.py -m list -s gs://bucket/path/ -n 5
        # python copy_droid_data.py -m copy -s gs://bucket/path/ -d ./data -n 3
    """
    parser = argparse.ArgumentParser(
        description="List or copy DROID data from Google Cloud Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  1. List first 5 folders:
     %(prog)s -m list -s gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/ -n 5

  2. Download first 3 folders:
     %(prog)s -m copy -s gs://... -d ./mydroiddata -n 3
        """
    )
    
    parser.add_argument(
        '-m', '--mode',
        required=True,
        choices=['list', 'copy'],
        help="Mode: 'list' (preview files) or 'copy' (download files)"
    )
    
    parser.add_argument(
        '-s', '--source',
        required=True,
        help="Source GCS bucket path (e.g., gs://bucket/path/)"
    )
    
    parser.add_argument(
        '-d', '--dest',
        help="Local destination directory (required for 'copy' mode)"
    )
    
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=5,
        help="Number of trajectories to process (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.mode == 'copy' and not args.dest:
        parser.error("Destination directory (-d/--dest) is required for 'copy' mode.")
    
    # Execute based on mode
    if args.mode == 'list':
        list_trajectories(args.source, args.count)
    elif args.mode == 'copy':
        copy_trajectories(args.source, args.dest, args.count)


if __name__ == "__main__":
    main()
