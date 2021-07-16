import ipfshttpclient
import os
ipfs = ipfshttpclient.connect(
    "/ip4/" + os.getenv('IPFS_IP') +
    "/tcp/" + os.getenv('IPFS_PORT') + "/http"
)


def write_json(data):
    """
    Write a single object to a JSON file in a local IPFS path (MFS)
    :return: IPFS hash
    """
    return ipfs.add_json(data)


def read_json(hash):
    """
    Read a single JSON item from IPFS
    :param hash:
    :return: List or Dict based on JSON
    """
    return ipfs.get_json(hash)

