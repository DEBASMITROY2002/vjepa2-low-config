#!/bin/bash

# ./manage_data.sh \
#   -m list \
#   -s "gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/" \
#   -n 5


# ./manage_data.sh \
#   -m copy \
#   -s "gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/" \
#   -d "mydroiddata/dataset/droid_raw/1.0.1/GuptaLab/success/2023-04-20" \
#   -n 5

# Default values
MODE=""
SOURCE_BUCKET=""
DEST_DIR=""
COUNT=5  # Default to 5 trajectories if not specified

# Function to display usage help
usage() {
    echo "Usage: $0 -m <mode> -s <source_bucket> [-d <dest_dir>] [-n <count>]"
    echo ""
    echo "Options:"
    echo "  -m  Mode: 'list' (preview files) or 'copy' (download files)"
    echo "  -s  Source GCS bucket path (e.g., gs://bucket/path/)"
    echo "  -d  Local Destination directory (required for 'copy' mode)"
    echo "  -n  Number of trajectories to process (default: 5)"
    echo ""
    echo "Examples:"
    echo "  1. List first 5 folders:"
    echo "     $0 -m list -s gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/"
    echo ""
    echo "  2. Download first 3 folders to 'data' dir:"
    echo "     $0 -m copy -s gs://... -d ./my_data -n 3"
    exit 1
}

# Parse command line arguments
while getopts "m:s:d:n:h" opt; do
    case $opt in
        m) MODE="$OPTARG" ;;
        s) SOURCE_BUCKET="$OPTARG" ;;
        d) DEST_DIR="$OPTARG" ;;
        n) COUNT="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Validation
if [[ -z "$MODE" || -z "$SOURCE_BUCKET" ]]; then
    echo "Error: Mode (-m) and Source (-s) are required."
    usage
fi

# Logic for 'list' mode
if [[ "$MODE" == "list" ]]; then
    echo "Listing first $COUNT items from: $SOURCE_BUCKET"
    echo "------------------------------------------------"
    gsutil ls "$SOURCE_BUCKET" | head -n "$COUNT"
    exit 0
fi

# Logic for 'copy' mode
if [[ "$MODE" == "copy" ]]; then
    if [[ -z "$DEST_DIR" ]]; then
        echo "Error: Destination directory (-d) is required for copy mode."
        exit 1
    fi

    echo "Preparing to download $COUNT trajectories..."
    echo "Source: $SOURCE_BUCKET"
    echo "Dest:   $DEST_DIR"
    
    # 1. Create Destination Root
    mkdir -p "$DEST_DIR"

    # 2. Get list of trajectories
    TRAJECTORIES=$(gsutil ls "$SOURCE_BUCKET" | head -n "$COUNT")

    if [[ -z "$TRAJECTORIES" ]]; then
        echo "Error: No trajectories found at source."
        exit 1
    fi

    # 3. Loop and Sync
    for TRAJ in $TRAJECTORIES; do
        # Extract folder name (removes trailing slash automatically via basename)
        FOLDER_NAME=$(basename "$TRAJ")
        TARGET_PATH="$DEST_DIR/$FOLDER_NAME"

        echo "------------------------------------------------"
        echo "Processing: $FOLDER_NAME"
        
        # Create the specific sub-folder
        mkdir -p "$TARGET_PATH"

        # Sync command: Multi-threaded (-m), Recursive (-r), Exclude .svo (-x)
        # We quote variables to handle paths with spaces safely
        gsutil -m rsync -r -x ".*\.svo$" "$TRAJ" "$TARGET_PATH"
    done
    
    echo "------------------------------------------------"
    echo "Download complete."
    exit 0
fi

# Invalid mode check
echo "Error: Invalid mode '$MODE'. Use 'list' or 'copy'."
usage