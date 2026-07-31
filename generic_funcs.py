from pathlib import Path
import re
from typing import Sequence, Any


def create_dir_if_not_exists(path_name: str) -> None:
    path = Path(path_name)
    path.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str, replacement: str = "-") -> str:
    if not name:
        return "unnamed"

    name = re.sub(r'[\\/*?:"<>|]', replacement, name) # remove invalid characters
    name = name.strip(" .") # remove whitespace and dots
    name = re.sub(f"{re.escape(replacement)}+", replacement, name) # collapse multiple replacements

    if not name:
        return "unnamed"

    return name

def extract_filename_without_extension_from_filepath(filepath : str) -> str:
    filepath = Path(filepath)
    return filepath.stem

def generate_lubm_input_folder_string(
    negations: bool | None = None,
    level: int | None = None
) -> str:
    negstring = ''

    if negations is not None:
        negstring = '_neg' if negations else '_noneg'

    level_string = '' if level is None else str(level)

    return f'lubm-0_{level_string}*{negstring}'

def zip_seq(seq1 : Sequence[Any], seq2 : Sequence[Any]) -> list[Any] :
    if len(seq1) != len(seq2):
        raise ValueError(
            f"Sequences must have equal length: {len(seq1)} != {len(seq2)}"
        )

    result = []
    for e1, e2 in zip(seq1, seq2):
        result.append(e1)
        result.append(e2)
    return result
