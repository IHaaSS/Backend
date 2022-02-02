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
    has_attachment = attachment_name == ""
    requests = [ipfs.write_json(incident)]
    if has_attachment:
        requests.append(ipfs.write_file(attachment))
    ipfsRefs = await asyncio.gather(*requests)

    attachments = []
    if has_attachment:
        attachments.append(attachment_name, eth.ipfs2bytes(ipfsRefs[1]))

    icd.add_incident(ipfsRefs[0], attachments)

    return '', 200


@bp.route('/incidents/comments', methods=['POST'])
async def add_incident_comment():
    body = request.get_json()
    parent = body['parent']
    incident = body['incident']
    comment = body['comment']

    requests = [ipfs.write_json(comment)]
    attachments = []
    if 'attachment' in request.files:
        attachment = request.files['attachment']
        attachment_name = request.form.get('attachmentName')
        requests.append(ipfs.write_file(attachment))

    ipfsRefs = await asyncio.gather(*requests)

    if len(ipfsRefs) > 1:
        attachments.append((attachment_name, eth.ipfs2bytes(ipfsRefs[1])))

    icd.add_comment(
        parent,
        incident,
        eth.ipfs2bytes(ipfsRefs[0]),
        attachments
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
