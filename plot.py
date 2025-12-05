import logging
import matplotlib.pyplot as plt
from sys import argv
from itertools import islice, chain
from pathlib import Path
from argparse import ArgumentParser
from mpl_toolkits.basemap import Basemap
import warnings; warnings.filterwarnings('ignore')
from fastkml import KML, Placemark
from fastkml.utils import find_all


LOG = logging.getLogger('ff-track.plot')


def parse_filter_kml(path, only_year=None):
    LOG.info(f'Loading {path}')
    kml = KML.parse(path)
    tracklog = next(find_all(kml, of_type=Placemark))
    year = tracklog.kml_geometry.track_items[0].when.dt.year
    if only_year and year != only_year:
        return []
    else:
        return [tracklog.geometry.geoms]


def calc_bounds(tracks, margin):
    all_pts_gen = (((p.x, p.y) for p in track) for track in tracks)
    all_pts = chain.from_iterable(all_pts_gen)
    min_x = None
    min_y = None
    max_x = None
    max_y = None
    for x, y in all_pts:
        min_x = min(min_x or x, x)
        max_x = max(max_x or x, x)
        min_y = min(min_y or y, y)
        max_y = max(max_y or y, y)
    return (min_x-margin, min_y-margin, max_x+margin, max_y+margin)


def plot_tracks_map(tracks, margin, linewidth, alpha, out_width, output):
    fig, ax = plt.subplots()
    min_lon, min_lat, max_lon, max_lat = calc_bounds(tracks, margin)
    map = Basemap(projection='lcc',
                  lon_0=(min_lon+max_lon)/2,
                  lat_0=min_lat, 
                  lat_1=max_lat,
                  llcrnrlon=min_lon,
                  llcrnrlat=min_lat,
                  urcrnrlon=max_lon,
                  urcrnrlat=max_lat)
    map.drawlsmask(ocean_color=(0, 0, 0.2), land_color='black', resolution='h', grid=1.25)
    for track in tracks:
        lon, lat = zip(*[(p.x, p.y) for p in track])
        xs, ys = map(lon, lat)
        map.plot(xs, ys, color='white', linewidth=linewidth, alpha=alpha)
    ax.set_position([0, 0, 1, 1])
    (min_x, max_x), (min_y, max_y) = map([min_lon, max_lon], [min_lat, max_lat])
    dpi = fig.get_dpi()
    fig.set_size_inches(out_width / dpi, out_width / dpi * (max_y - min_y) / (max_x - min_x))
    fig.savefig(output)


def make_parser():
    parser = ArgumentParser()
    parser.add_argument('--directory', type=Path, default=Path('tracklogs'))
    parser.add_argument('--margin', type=float, default=0.1)
    parser.add_argument('--linewidth', type=float, default=1)
    parser.add_argument('--alpha', type=float, default=0.3)
    parser.add_argument('--year-filter', type=int, default=None)
    parser.add_argument('--truncate-tracklogs', type=int, default=None)
    parser.add_argument('--width', type=float, default=1000)
    parser.add_argument('--output', type=Path, default=Path('map.png'))
    return parser


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    args = make_parser().parse_args()
    kmls = args.directory.glob('*.kml')
    tracks_gen = (parse_filter_kml(kml, args.year_filter) for kml in islice(kmls, args.truncate_tracklogs))
    tracks = list(chain.from_iterable(tracks_gen))
    LOG.info(f'Plotting {len(tracks)} tracklogs')
    plot_tracks_map(tracks, args.margin, args.linewidth, args.alpha, args.width, args.output)
    LOG.info(f'Wrote {args.output}')
