import zipfile
import json

def compare_jsons_in_zips(zip1_path, zip2_path):
    """Extract the single JSON file from each ZIP, load as dict, and compare content."""
    def extract_single_json(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            json_files = [info for info in z.infolist() if not info.is_dir() and info.filename.lower().endswith('.json')]
            if len(json_files) != 1:
                raise ValueError(f"Expected exactly one JSON file in {zip_path}, found {len(json_files)}")
            data = z.read(json_files[0].filename).decode('utf-8')
            return json.loads(data)
    try:
        dict1 = extract_single_json(zip1_path)
        dict2 = extract_single_json(zip2_path)
        return json.dumps(dict1, sort_keys=True) == json.dumps(dict2, sort_keys=True)
    except Exception as e:
        # Optionally log or print the error
        return False