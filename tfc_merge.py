import json
import sys

# Load JSON from file paths
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# Save JSON to a file
def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Check if enough arguments are provided
if len(sys.argv) != 4:
    print("Usage: python merge.py <input_json_1> <input_json_2> <output_json>")
    sys.exit(1)

# Get file paths from command-line arguments
file_path_1 = sys.argv[1]
file_path_2 = sys.argv[2]
output_file = sys.argv[3]

# Load the JSON data from the files
json1 = load_json(file_path_1)
json2 = load_json(file_path_2)

# Merge the two JSON arrays
merged_json = json1 + json2

# Sort by 'page_id' in descending order
sorted_json = sorted(merged_json, key=lambda x: x['page_id'], reverse=True)

# Save the sorted merged JSON to the output file
save_json(sorted_json, output_file)

print(f"Sorted merged JSON saved to {output_file}")
