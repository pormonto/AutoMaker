import bson
import os
import json
import time
import signal
from functools import partial

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("File reading timed out")

def read_bson_file_with_timeout(file_path, timeout=30):
    """Read a BSON file with a timeout to avoid hanging on large files."""
    # Set up the timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        with open(file_path, 'rb') as f:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            print(f"Reading file: {file_path} ({file_size:.2f} MB)")
            data = bson.decode_all(f.read())
        signal.alarm(0)  # Cancel the alarm
        return data
    except TimeoutError:
        print(f"Timeout reached while reading {file_path}.")
        print(f"File is likely too large. Consider using mongorestore and a MongoDB server for this file.")
        return []

def get_document_preview(doc, max_fields=3, max_array_items=2, max_string_len=50):
    """Create a preview of a document showing only top-level structure."""
    preview = {}
    
    # Get a slice of the top-level fields
    fields = list(doc.keys())[:max_fields]
    
    for field in fields:
        value = doc[field]
        
        # Handle different types of values
        if isinstance(value, dict):
            preview[field] = f"{{...}} ({len(value)} keys)"
        elif isinstance(value, list):
            if len(value) > 0:
                preview[field] = f"[...] ({len(value)} items)"
            else:
                preview[field] = "[]"
        elif isinstance(value, str):
            if len(value) > max_string_len:
                preview[field] = value[:max_string_len] + "..."
            else:
                preview[field] = value
        else:
            preview[field] = value
    
    # Indicate if there are more fields
    if len(doc) > max_fields:
        preview["..."] = f"({len(doc) - max_fields} more fields)"
        
    return preview

# Add this function to your existing script
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
            
        except Exception as e:
            print(f"Error reading {metadata_file}: {e}")
    
    return collection_names

# Path to your BSON files
admin_dir = "admin"

# Add this before processing BSON files
print("=== MongoDB Collections ===")
collections = extract_collection_names(admin_dir)
for i, collection in enumerate(collections, 1):
    print(f"{i}. {collection}")
print(f"Total collections: {len(collections)}\n")

# List all BSON files (not metadata)
bson_files = [f for f in os.listdir(admin_dir) if f.endswith('.bson')]

# Sort by file size (smallest to largest)
bson_files.sort(key=lambda f: os.path.getsize(os.path.join(admin_dir, f)))

for bson_file in bson_files:
    file_path = os.path.join(admin_dir, bson_file)
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
    
    print(f"\n=== Contents of {bson_file} ({file_size:.2f} MB) ===")
    
    try:
        # Use a timeout appropriate for the file size
        timeout = max(30, int(file_size * 2))  # 2 seconds per MB, minimum 30 seconds
        documents = read_bson_file_with_timeout(file_path, timeout=timeout)
        
        if not documents:
            print("No documents loaded (timed out or empty file)")
            continue
        
        print(f"Total documents: {len(documents)}")
        
        for i, doc in enumerate(documents[:5]):  # Print first 5 docs only
            print(f"\nDocument {i+1} preview:")
            preview = get_document_preview(doc)
            print(json.dumps(preview, default=str, indent=2))
        
        if len(documents) > 5:
            print(f"...and {len(documents) - 5} more documents")
    except Exception as e:
        print(f"Error reading file: {e}")
        
    # Ask if user wants to continue after each large file
    if file_size > 50:  # If file is larger than 50MB
        resp = input("Continue to next file? (y/n): ")
        if resp.lower() != 'y':
            break