from pathlib import Path
import re
from typing import Sequence, Any


def create_dir_if_not_exists(path_name : str):
    path = Path(path_name)
    path.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name, replacement="-"):
    return re.sub(r'[\\/*?:"<>|]', replacement, name)

def extract_filename_from_filepath(filepath : str) -> str:
    filepath = Path(filepath)
    return filepath.stem


def generate_lubm_input_folder_string(negations : bool=None, level : int='') -> str :
    negstring = ''
    if negations is not None:
        negstring = 'neg'
        if not negations:
            negstring = 'no' + negstring
        negstring = '_' + negstring
    return f'lubm-0_{level}*{negstring}'

def zip_seq(seq1 : Sequence[Any], seq2 : Sequence[Any]) -> list[Any] :
    result = []
    for i,e1 in enumerate(seq1):
        result.append(e1)
        result.append(seq2[i])
    return result
