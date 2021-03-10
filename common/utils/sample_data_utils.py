import json
from pathlib import Path
import enum


def to_dict(o):
    return o.__dict__()


class ExportSamplesStatus(enum.Enum):
    DISABLED = 1,
    ENABLED = 2


def export_samples(object, run_id, enable_export=ExportSamplesStatus.DISABLED.name):

    if enable_export == ExportSamplesStatus.ENABLED.name :
        if object:
            if isinstance(object, list):
                file_name = object[0].__class__.__name__ + 's'
            else:
                file_name = object.__class__.__name__
            dir = 'exported_jsons/' + run_id
            Path(dir).mkdir(parents=True, exist_ok=True)
            with open(dir + '/' + file_name + ".json", "w") as write_file:
                json.dump(object, write_file, default=to_dict)
