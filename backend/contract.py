from flask import Blueprint, request

import json
from backend.storage import ethereum as eth
from backend.storage import ipfs
import asyncio

bp = Blueprint("contract", __name__, url_prefix='/contract')
icd = eth.IncidentsContract()


#####################
# contract routes
#####################
@bp.route('/incidents', methods=['GET'])
async def get_incidents():
    incidents = icd.get_incidents()
    incidents_full = await asyncio.gather(*[icd.get_incident(i) for i in incidents])
    return json.dumps(incidents_full)


@bp.route('/incidents', methods=['POST'])
async def add_incident():
    attachment = request.files['attachment']
    attachment_name = request.form.get('attachmentName')
    incident = json.loads(request.form.get('incident'))
    ipfsRefs = await asyncio.gather(*[
        ipfs.write_json(incident),
        ipfs.write_file(attachment)
    ])
    icd.add_incident(ipfsRefs[0], [(attachment_name, eth.ipfs2bytes(ipfsRefs[1]))])
    return '', 200


@bp.route('/incidents/comments', methods=['POST'])
async def add_incident_comment():
    parent = request.form.get('parent')
    incident = request.form.get('incident')
    comment = request.form.get('comment')
    attachment = request.files['attachment']
    attachment_name = request.form.get('attachmentName')
    ipfsRefs = await asyncio.gather(*[
        ipfs.write_json(comment),
        ipfs.write_file(attachment)
    ])
    icd.add_comment(
        parent,
        eth.ipfs2bytes(ipfsRefs[0]),
        incident,
        [(attachment_name, eth.ipfs2bytes(ipfsRefs[1]))]
    )
    return '', 200


@bp.route('/incidents/vote', methods=['POST'])
def vote_incident():
    body = request.get_json()
    icd.vote_incident(body['ref'], body['vote'])
    return '', 200


@bp.route('/incidents/comments/vote', methods=['POST'])
def vote_incident_comment():
    body = request.get_json()
    icd.vote_comment(body['ref'], body['vote'])
    return '', 200
