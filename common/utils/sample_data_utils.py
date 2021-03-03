import json
from pathlib import Path
import enum


def to_dict(o):
    return o.__dict__()


class ExportSamplesStatus(enum.Enum):
    DISABLED = 1,
    ENABLED = 2


def resolve_file_name_from_object_class(obj):
        if isinstance(obj, list):
            file_name = obj[0].__class__.__name__ + 's'
        else:
            file_name = obj.__class__.__name__
        return file_name



def export_samples(obj, run_id, enable_export=ExportSamplesStatus.DISABLED.name,file_name=None):
    if enable_export == ExportSamplesStatus.ENABLED.name:
        if not file_name:
            file_name = resolve_file_name_from_object_class(obj)
        dir = 'exported_jsons/' + run_id
        Path(dir).mkdir(parents=True, exist_ok=True)
        with open(dir + '/' + file_name + ".json", "w") as write_file:
            json.dump(obj, write_file, default=to_dict)
