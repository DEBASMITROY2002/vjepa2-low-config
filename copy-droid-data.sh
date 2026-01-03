# 1. Create your local destination root
# (Note: Removed trailing slash from DEST_DIR to prevent double-slashes //)
DEST_DIR="mydroiddata/dataset/droid_raw/1.0.1/GuptaLab/success/2023-04-20"
mkdir -p "$DEST_DIR"

# 2. Define the source "Day" folder
SOURCE_BUCKET="gs://gresearch/robotics/droid_raw/1.0.1/GuptaLab/success/2023-04-20/"

# 3. Get the list of the first 5 trajectories
TRAJECTORIES=$(gsutil ls $SOURCE_BUCKET | head -n 5)

# 4. Loop and Sync (Excluding .svo)
for TRAJ in $TRAJECTORIES; do
    # Extract the folder name (e.g., Thu_Apr_20_...)
    FOLDER_NAME=$(basename "$TRAJ")
    
    # Define the specific local target for this trajectory
    TARGET_PATH="$DEST_DIR/$FOLDER_NAME"
    
    echo "Processing: $FOLDER_NAME"
    
    # --- THE FIX: Create the directory explicitly first ---
    mkdir -p "$TARGET_PATH"
    
    # Sync only that folder, filtering out .svo files
    # Note: quoted paths to handle any potential spaces safely
    gsutil -m rsync -r -x ".*\.svo$" "$TRAJ" "$TARGET_PATH"
done