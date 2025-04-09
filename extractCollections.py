import os
import json

def extract_collection_names(directory):
    """Extract collection names from MongoDB metadata files."""
    collection_names = []
    
    # Find all metadata files
    metadata_files = [f for f in os.listdir(directory) if f.endswith('.metadata.json')]
    
    for metadata_file in metadata_files:
        file_path = os.path.join(directory, metadata_file)
        try:
            with open(file_path, 'r') as f:
                metadata = json.load(f)
                
            # The namespace typically contains the database and collection names
            if "ns" in metadata:
                # Format is typically "database.collection"
                namespace = metadata["ns"]
                collection_name = namespace.split(".")[-1]
                collection_names.append(collection_name)
            else:
                print(f"No namespace found in {metadata_file}")
                
        except Exception as e:
            print(f"Error reading {metadata_file}: {e}")
    
    return collection_names

# Path to your MongoDB files
admin_dir = "admin"

# Extract collection names
collections = extract_collection_names(admin_dir)

# Print results
print("\n=== MongoDB Collections ===")
for i, collection in enumerate(collections, 1):
    print(f"{i}. {collection}")
print(f"\nTotal collections found: {len(collections)}")