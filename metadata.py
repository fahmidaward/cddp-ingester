from multiprocessing import Pool
import os

from gdb_utils import get_metadata, get_abstract, get_title, update_resource
from utils import logger_setup, parse_cddp, get_layers


# Configure logging.
LOGGER = logger_setup()


def update_metadata(dataset, layers):
    gdb_path, layer = dataset
    # For a given dataset, find out if it is published. If so, parse the metadata from the fGDB.
    if layer.lower() in layers:
        metadata = get_metadata(gdb_path, layer)
        if metadata:
            # Get the layer's REST endpoint.
            layer_href = layers[layer.lower()].replace('http', 'https')
            # Update the published layer's metadata.
            abstract = get_abstract(metadata)
            if abstract:
                try:
                    update_resource(layer_href, {'abstract': abstract})
                    LOGGER.info('Updated abstract: {}'.format(layer))
                except:
                    LOGGER.exception('Error during update of abstract for {}'.format(layer))
            else:
                LOGGER.warning('No abstract available for {}'.format(layer))
            # Update the layer title from metadata.
            title = get_title(metadata)
            if title:
                try:
                    update_resource(layer_href, {'title': title})
                    LOGGER.info('Updated title: {}'.format(layer))
                except:
                    LOGGER.exception('Error during update of title for {}'.format(layer))
            else:
                LOGGER.warning('No title available for {}'.format(layer))
        else:
            LOGGER.warning('No metadata available for {}'.format(layer))


def mp_handler(cddp_path=None):
    """Multiprocessing handler to import metadata from file GDBs in the mounted CDDP volume.
    """
    if not cddp_path:
        # Assume that this path set via an environment variable if not explicitly passed in.
        cddp_path = os.getenv('CDDP_PATH')

    datasets = parse_cddp(cddp_path, LOGGER)
    workspace = os.getenv('GEOSERVER_WORKSPACE')
    layers = get_layers(workspace)

    # Use a multiprocessing Pool to update layer metadata in parallel.
    p = Pool(processes=4)
    iterable = [(dataset, layers) for dataset in datasets]
    p.starmap(update_metadata, iterable)


if __name__ == "__main__":
    mp_handler()
