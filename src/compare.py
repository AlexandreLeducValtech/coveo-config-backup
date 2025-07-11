import zipfile

def are_snapshots_identical(zip1_path, zip2_path):
    """
    Compare two ZIP files by their content and structure.

    Args:
        zip1_path (str): The file path of the first ZIP file.
        zip2_path (str): The file path of the second ZIP file.

    Returns:
        bool: True if the ZIP files are identical, False otherwise.
    """
    def zip_content_dict(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            return {info.filename: z.read(info.filename) for info in sorted(z.infolist(), key=lambda x: x.filename)}
    try:
        return zip_content_dict(zip1_path) == zip_content_dict(zip2_path)
    except Exception:
        return False