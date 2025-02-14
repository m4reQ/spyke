import base64
import hashlib
import itertools
import os
import pathlib
import subprocess
import tomllib
import zipfile

from packaging import tags

CMAKE_CONFIG = 'RelWithDebInfo'
DIST_DIR = './dist'
BUILD_DIR = './build'
WHL_DIR = '.'

with open('./pyproject.toml', 'rb') as f:
    config = tomllib.load(f)

project_name = config['project']['name']
project_version = config['project']['version']
dependencies = [
    'PyOgg',
    'PyOpenAL',
    'numpy',
    'colorama',
    'Pillow',
    'pydub',
    'freetype-py',
    'psutil']
    # 'pygl @ git+https://github.com/m4reQ/pygl@private_0.0.1']

retcode = subprocess.call(('cmake', '-S', '.', '-B', BUILD_DIR))
if retcode != 0:
    raise RuntimeError('Failed to run cmake configure.')

retcode = subprocess.call(('cmake', '--build', BUILD_DIR, '--config', CMAKE_CONFIG))
if retcode != 0:
    raise RuntimeError('Failed to run cmake build.')

retcode = subprocess.call(('cmake', '--install', BUILD_DIR, '--config', CMAKE_CONFIG))
if retcode != 0:
    raise RuntimeError('Failed to run cmake install.')

dist_info_dir = os.path.join(DIST_DIR, f'{project_name}-{project_version}.dist-info')
if not os.path.exists(dist_info_dir):
    os.mkdir(dist_info_dir)

# top_level.txt
with open(os.path.join(dist_info_dir, 'top_level.txt'), 'w+') as f:
    f.write(f'{project_name}\n')

# METADATA
with open(config['project']['readme']['file'], 'r') as f:
    description_lines = f.readlines()

with open(os.path.join(dist_info_dir, 'METADATA'), 'w+') as f:
    f.write('Metadata-Version: 2.2\n')
    f.write(f'Name: {project_name}\n')
    f.write(f'Version: {project_version}\n')
    f.write(f'Summary: {config['project']['description']}\n')
    f.write(f'Home-page: {config['project']['urls']['home']}\n')
    f.write(f'Requires-Python: {config['project']['requires-python']}\n')

    for author in config['project']['authors']:
        f.write(f'Author: {author['name']}\n')

    for classifier in config['project']['classifiers']:
        f.write(f'Classifier: {classifier}\n')

    for dependency in dependencies:
        f.write(f'Requires-Dist: {dependency}\n')

    f.write(f'Description-Content-Type: {config['project']['readme']['content-type']}\n')
    f.write(f'Description: {description_lines[0]}')
    for descr_line in description_lines[1:]:
        f.write(f'       |{descr_line}')

# WHEEL
whl_tag = str(next(tags.cpython_tags()))
with open(os.path.join(dist_info_dir, 'WHEEL'), 'w+') as f:
    f.write('Wheel-Version: 1.0\n')
    f.write('Generator: yomama (6.9.420)\n')
    f.write('Root-Is-Purelib: false\n')
    f.write(f'Tag: {whl_tag}\n')

# RECORD
record_filepath = os.path.join(dist_info_dir, 'RECORD')
with open(record_filepath, 'w+') as f:
    directories = itertools.chain(
        pathlib.Path(DIST_DIR, project_name).rglob('*'),
        pathlib.Path(DIST_DIR, 'data').rglob('*'),
        pathlib.Path(dist_info_dir).rglob('*'))
    for file in directories:
        if file.is_dir():
            continue

        if file.name == 'RECORD':
            f.write(f'{file.relative_to(DIST_DIR).as_posix()},,\n')
            continue

        content = file.read_bytes()
        length = len(content)
        sha = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode().removesuffix('=')
        f.write(f'{file.relative_to(DIST_DIR).as_posix()},sha256={sha},{length}\n')

whl_filename = os.path.join(WHL_DIR, f'{project_name}-{project_version}-{whl_tag}.whl')
with zipfile.ZipFile(whl_filename, 'w', compresslevel=9) as whl:
    for file in pathlib.Path(DIST_DIR).rglob('*'):
        whl.write(file, arcname=file.relative_to(DIST_DIR))
