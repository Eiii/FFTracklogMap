import subprocess
import json
import math
import logging
from pathlib import Path
from argparse import ArgumentParser


HISTORY_URL = 'https://plan.foreflight.com/tracklogs/api/tracklogs/?page={0}&pageSize=150'
KML_URL = 'https://plan.foreflight.com/tracklogs/export/{0}/kml'
CURL_TEMPLATE = Path('curl_command.sh')
TMP_SCRIPT = Path('tmp.sh')

LOG = logging.getLogger('ff-track.download')


def run_template_cmd(url, param):
    with CURL_TEMPLATE.open('r') as fd:
        lines = fd.readlines()
    lines[0] = f"curl '{url.format(param)}' \\\n"
    with TMP_SCRIPT.open('w') as fd:
        fd.writelines(lines)
    # Probably doesn't work on windows
    result = subprocess.run(f'sh {TMP_SCRIPT}', stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    return result.stdout


def download_history_uuids():
    max_pages = None
    current_page = 0
    all_uuids = []
    while max_pages is None or current_page < max_pages:
        LOG.info(f'Downloading tracklog history page {current_page+1}/{max_pages or "?"}')
        result = json.loads(run_template_cmd(HISTORY_URL, current_page))
        all_uuids += [track['trackUuid'] for track in result['tracklogs']]
        max_pages = math.ceil(result['totalTracklogs'] / result['pageSize'])
        current_page += 1
    return all_uuids


def download_tracklog_kml(uuid, output_path):
    result = run_template_cmd(KML_URL, uuid)
    with output_path.open('wb') as fd:
        fd.write(result)


def make_parser():
    parser = ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=Path('tracklogs'))
    return parser


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    args = make_parser().parse_args()
    tracklog_uuids = download_history_uuids()
    if not args.output_dir.exists():
        args.output_dir.mkdir()
    LOG.info(f'Found {len(tracklog_uuids)} tracklogs')
    for i, uuid in enumerate(tracklog_uuids):
        output_path = args.output_dir / f'{uuid}.kml'
        if not output_path.exists():
            LOG.info(f'Downloading {uuid} ({i}/{len(tracklog_uuids)})')
            download_tracklog_kml(uuid, output_path)
        else:
            LOG.info(f'Skipping {uuid}, exists')

