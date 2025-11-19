import os
import csv
import yaml
import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from tqdm import tqdm
import gc
import glob

def locate_videos_folder(base_path):
    videos_folder = os.path.join(base_path, "Videos")
    if not os.path.isdir(videos_folder):
        raise FileNotFoundError("The 'Videos' folder was not found within the specified base path.")
    return videos_folder

def load_or_create_yaml(yaml_path, child_name, camera_names):
    print(yaml_path)
    if os.path.isfile(yaml_path):
        print(f"YAML file found at {yaml_path}. Loading...")
        with open(yaml_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
    else:
        print("No YAML file found. Creating a new YAML file...")
        yaml_data = {}
        yaml_data["Name"] = input("Enter the project name (e.g., Child_1_Handwriting): ")
        yaml_data["Date of creation"] = input("Enter the date of creation (YYYY-MM-DD): ")
        yaml_data["Recordings"] = {"annotation_dataset": None}
        yaml_data["Cameras"] = camera_names
        entities_input = input("Enter entity: ").strip()
        yaml_data["Entities"] = [entity.strip() for entity in entities_input.split(",")]
        keypoints_input = input("Enter keypoints separated by '; ' (e.g., Pinky_T; Pinky_D; Wrist): ").strip()
        yaml_data["Keypoints"] = [keypoint.strip() for keypoint in keypoints_input.split("; ")]
        with open(yaml_path, 'w') as file:
            yaml.dump(
                yaml_data,
                file,
                sort_keys=False,
                default_flow_style=False,
                width=72,
                indent=2
            )
        print(f"YAML file created and saved at: {yaml_path}")
    return yaml_data

def create_annotation_folders(base_path, camera_names):
    annotation_folder = os.path.join(base_path, "annotation_dataset")
    os.makedirs(annotation_folder, exist_ok=True)
    camera_dirs = []
    for camera_name in camera_names:
        camera_dir = os.path.join(annotation_folder, camera_name)
        os.makedirs(camera_dir, exist_ok=True)
        camera_dirs.append(camera_dir)
    print(f"Annotation folders created under: {annotation_folder}")
    return annotation_folder, camera_dirs

def get_total_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total_frames

def extract_specific_frames(video_path, frame_indices):
    """Extract only specific frames from a video."""
    cap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Extracting {len(frame_indices)} frames from video: {video_path} (total frames: {total_frames})")
    for frame_index in tqdm(frame_indices, desc="Extracting specific frames"):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if ret:
            frames.append((frame_index, frame))
        else:
            print(f"Warning: Unable to read frame {frame_index} from {video_path}")
    cap.release()
    return frames
    
def kmeans_select_frames(video_path, num_frames, n_clusters):
    """Perform KMeans clustering on frames from the main camera."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Performing KMeans clustering on video: {video_path} (total frames: {total_frames})")

    frame_features = []
    frame_indices = []
    for i in tqdm(range(total_frames), desc="Extracting frames for KMeans"):
        ret, frame = cap.read()
        if not ret:
            break
        frame_indices.append(i)
        resized_frame = cv2.resize(frame, (64, 64)).flatten()
        frame_features.append(resized_frame)
    cap.release()

    print("Fitting KMeans model...")
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(frame_features)

    frames_per_cluster = num_frames // n_clusters
    sampled_indices = []
    for i in range(n_clusters):
        cluster_indices = np.where(kmeans.labels_ == i)[0]
        selected_indices = np.linspace(0, len(cluster_indices) - 1, num=frames_per_cluster, dtype=int)
        sampled_indices.extend([frame_indices[cluster_indices[idx]] for idx in selected_indices])

    del frame_features
    gc.collect()
    return sorted(sampled_indices)

def create_csv_file(csv_path, yaml_data, frames):
    print(f"Creating CSV file at: {csv_path}")

    # Extract keypoints and entities from YAML in the exact order
    keypoints = yaml_data["Keypoints"]
    entities = yaml_data.get("Entities", ["entity"])

    num_keypoints = len(keypoints)
    num_entities = len(entities)

    # Total number of (x, y, state) triplets
    total_triplets = num_keypoints * num_entities

    # Prepare the header rows based on the keypoints and entities
    # Row 1: scorer information (kept generic here)
    row1 = ["Scorer"] * (1 + total_triplets * 3)

    # Row 2: entities (one column per coord of each keypoint/entity)
    row2 = ["entities"]

    # Row 3: bodyparts (keypoints)
    row3 = ["bodyparts"]

    # Row 4: coordinate labels
    row4 = ["coords"]

    for entity in entities:
        for keypoint in keypoints:
            # For each keypoint of each entity we add three columns: x, y, state
            row2 += [entity, entity, entity]
            row3 += [keypoint, keypoint, keypoint]
            row4 += ["x", "y", "state"]

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Write header rows
        writer.writerow(row1)
        writer.writerow(row2)
        writer.writerow(row3)
        writer.writerow(row4)

        # Write frame rows with placeholders for each keypoint *and* entity
        for frame_index, _ in frames:
            row = [f"Frame_{frame_index}.jpg"]
            for _ in range(total_triplets):
                row += ["", "", "0"]  # Placeholder for x, y, and state
            writer.writerow(row)

    print(f"CSV file saved at: {csv_path}")

def sync_kmeans_frame_selection(base_path, num_frames, n_clusters):
    videos_folder = locate_videos_folder(base_path)
    video_files = sorted([f for f in os.listdir(videos_folder) if f.endswith(('.mp4', '.avi'))])
    camera_names = [os.path.splitext(f)[0] for f in video_files]
    annotation_folder, camera_dirs = create_annotation_folders(base_path, camera_names)
    # Look for any existing .yaml file in the base path
    yaml_files = glob.glob(os.path.join(base_path, "*.yaml"))
    if yaml_files:
        yaml_path = yaml_files[0]
        print(f"Found existing YAML file: {yaml_path}")
    else:
        yaml_path = os.path.join(base_path, f"{os.path.basename(base_path.rstrip('/'))}.yaml")
        print(f"No YAML file found. Will create a new one at: {yaml_path}")

    yaml_data = load_or_create_yaml(yaml_path, os.path.basename(base_path.rstrip("/")), camera_names)

    print(f"Detected cameras: {camera_names}")
    main_camera_index = int(input(f"Select the main camera index (0-{len(camera_names) - 1}): "))
    main_camera = video_files[main_camera_index]

    print(f"Main camera selected: {main_camera}")
    main_camera_path = os.path.join(videos_folder, main_camera)
    selected_frame_indices = kmeans_select_frames(main_camera_path, num_frames, n_clusters)

    for video_file, camera_dir in zip(video_files, camera_dirs):
        video_path = os.path.join(videos_folder, video_file)
        print(f"Processing video: {video_file}")
        synced_frames = extract_specific_frames(video_path, selected_frame_indices)

        print(f"Saving annotations and sampled frames for camera: {camera_dir}")
        csv_path = os.path.join(camera_dir, "annotations.csv")
        create_csv_file(csv_path, yaml_data, synced_frames)

        for frame_index, frame in tqdm(synced_frames, desc=f"Saving frames to {camera_dir}"):
            cv2.imwrite(f"{camera_dir}/Frame_{frame_index}.jpg", frame)
        gc.collect()


base_path = input("Enter the base path to the main folder (e.g., Child_1): ")
videos_folder = locate_videos_folder(base_path)
video_files = sorted([f for f in os.listdir(videos_folder) if f.endswith(('.mp4', '.avi'))])
total_frames_list = [get_total_frames(os.path.join(videos_folder, video_file)) for video_file in video_files]
print("Total frames in each video:")
for video_file, total_frames in zip(video_files, total_frames_list):
    print(f"{video_file}: {total_frames} frames")
num_frames = int(input("Enter the total number of frames to sample per camera (num_frames): "))
n_clusters = int(input("Enter the number of clusters (n_clusters): "))
if num_frames % n_clusters != 0:
    print("Warning: num_frames should be a multiple of n_clusters.")
    num_frames = int(input("Please enter a new value for num_frames that is a multiple of n_clusters: "))
sync_kmeans_frame_selection(base_path, num_frames, n_clusters)
print("Process completed successfully.")

