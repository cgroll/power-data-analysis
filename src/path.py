from pathlib import Path

class ProjPaths:

    current_file_path = Path(__file__)
    pkg_src_path = current_file_path.parent
    project_path = current_file_path.parent.parent
    data_path = project_path / "data"
    raw_data_path = project_path / "data" / "raw_data"