import ipfshttpclient
import os
ipfs = ipfshttpclient.connect(
    "/ip4/" + os.getenv('IPFS_IP') +
    "/tcp/" + os.getenv('IPFS_PORT') + "/http"
)


async def write_file(data):
    """
    Write a file to IPFS
    :param data: file
    :return: IPFS hash
    """
    response = ipfs.add(data)
    return response['Hash']


async def write_str(data):
    return ipfs.add_str(data)


async def write_json(data):
    """
    Write a single object to a JSON
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


def read(hash):
    return ipfs.cat(hash)
