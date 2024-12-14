import yaml
import os

def load_config(file_path="config/config.yaml"):
    """
    Loads configuration from the specified YAML file.
    :param file_path: Path to the YAML configuration file.
    :return: Parsed configuration dictionary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
