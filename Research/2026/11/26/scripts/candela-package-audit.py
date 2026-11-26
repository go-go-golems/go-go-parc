"""Print stored archive and canonical payload sizes for a Jig Stage job ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def audit(path):
    studies = {}
    meshes = {}
    summary = dict(archive_bytes=path.stat().st_size, scene_files_bytes=0,
                   studies_bytes=0, meshes_bytes=0, scene_count=0, body_count=0)
    with ZipFile(path) as archive:
        for entry in archive.infolist():
            if not entry.filename.startswith('scene-'):
                continue
            summary['scene_files_bytes'] += entry.compress_size
            if not entry.filename.endswith('/jig-program.js'):
                continue
            source = archive.read(entry).decode().strip()
            program = json.loads(source.removeprefix('export const program = ').removesuffix(';'))
            summary['scene_count'] += 1
            def account(obj, seen):
                data = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()
                seen[hashlib.sha256(data).digest()] = len(data)
                return len(data)
            summary['studies_bytes'] += account(program['studies'], studies)
            for body in program['bodies']:
                fields = {k: body[k] for k in ('positions', 'normals', 'indices', 'triFace', 'faces') if k in body}
                summary['meshes_bytes'] += account(fields, meshes)
                summary['body_count'] += 1
    for label, groups in [('study', studies), ('mesh', meshes)]:
        summary[label + '_distinct_count'] = len(groups)
        summary[label + '_distinct_bytes'] = sum(groups.values())
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', type=Path)
    print(json.dumps(audit(parser.parse_args().job), indent=2))
