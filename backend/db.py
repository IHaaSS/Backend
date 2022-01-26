from flask import Blueprint, request
import asyncio
from bson import json_util
from backend.storage import mongo as db

from backend.logic.normalization import normalize_incident, generate_id_list, reverse_norm_incident
from backend.logic.questions import execute_refinement, execute_completion
from backend.logic.utils import update_norm_user_incident

bp = Blueprint("db", __name__)


#####################
# reference incidents
#####################


@bp.route('/incidents', methods=['GET'])
def get_incidents():
    incidents = db.get_incidents()
    return json_util.dumps(incidents)


@bp.route('/incidents', methods=['POST'])
async def post_incident():
    body = request.get_json()
    incident = await save_incident(body, 'admin')
    return json_util.dumps(incident)


@bp.route('/incidents/<incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    db.delete_incident(incident_id)
    return '', 200


#################
# user incidents
#################

@bp.route('/user_incidents', methods=['GET'])
def get_user_incidents():
    incidents = db.get_user_incidents()
    return json_util.dumps(incidents)


@bp.route('/user_incidents', methods=['POST'])
async def post_user_incident():
    body = request.get_json()
    user_incident = body
    user_incident['myId'] = db.get_new_user_incident_id()
    categories = await db.get_categories()
    norm_user_incident = normalize_incident(user_incident, *categories)
    norm_ref_incidents = await db.get_norm_incidents()
    question_response = execute_completion(user_incident, categories, norm_user_incident, norm_ref_incidents)
    await asyncio.gather(*[
        db.insert_norm_user_incident(norm_user_incident),
        db.insert_user_incident(user_incident)
    ])
    return question_response


@bp.route('/user_incidents/approve', methods=['POST'])
async def approve_user_incident():
    body = request.get_json()
    uid = body.pop('myId')
    user_incident = db.get_user_incident(uid)
    incident = await save_incident(user_incident, 'user')
    remove_user_incident(uid)
    return json_util.dumps(incident)


@bp.route('/user_incidents/<incident_id>', methods=['DELETE'])
async def delete_user_incident(incident_id):
    remove_user_incident(incident_id)
    return ''


################
# questions
################

@bp.route('/questions', methods=['POST'])
def post_question():
    body = request.get_json()
    q = {
        'questionId': db.get_new_question_id(),
        'text': body['text']
    }

    post_relation(q['questionId'], body)
    if 'counterText' in body:
        if len(body['counterText']) > 0:
            q_counter = q
            q_counter['text'] = body['counterText']
            db.insert_question_counter(q_counter)
    db.insert_question(q)
    return json_util.dumps(q)


@bp.route('/relations', methods=['POST'])
def post_relation(question_id, temp):
    topics = ['source', 'event', 'entity', 'impact']
    topics_plural = ['sources', 'events', 'entities', 'impacts']
    for i, topic in enumerate(topics_plural):
        for source in temp[topic]:
            t = source[topics[i]]
            if len(t) != 0:
                db.insert_relation(question_id, i+1, t[-1])


# handle response from frontend after user answered questions
@bp.route('/answer', methods=['POST'])
async def post_answer():
    body = request.get_json()
    nui, copy_nui, categories, ref_norm_incidents = await asyncio.gather(*[
        db.get_norm_user_incident(body['id']),
        db.get_norm_user_incident(body['id']),
        db.get_categories(),
        db.get_norm_incidents()
    ])
    categories_ids = list(map(lambda c: generate_id_list(c, []), categories))
    s, ev, en, im = categories_ids

    u = {'title': nui["title"], 'refId': nui["refId"],
         'normSources': update_norm_user_incident(nui['normSources'], s, body['answers'],
                                                  body['phase'], 1),
         'normEvents': update_norm_user_incident(nui['normEvents'], ev, body['answers'],
                                                 body['phase'], 2),
         'normEntities': update_norm_user_incident(nui['normEntities'], en, body['answers'],
                                                   body['phase'], 3),
         'normImpacts': update_norm_user_incident(nui['normImpacts'], im, body['answers'],
                                                  body['phase'], 4)}
    if body['phase'] == 2:
        user_incident = db.get_user_incident(u['refId'])
        rev_incident = reverse_norm_incident(u, *categories, user_incident)
        db.update_user_incident(rev_incident)
        return {'id': u['refId'], 'questions': [], 'phase': 2}

    if body['phase'] == 1:
        db.update_norm_incident(u)
        return execute_refinement(u, copy_nui, ref_norm_incidents, categories, *categories_ids, body)


async def save_incident(incident, transmitted_by):
    incident['transmittedBy'] = transmitted_by
    db.insert_incident(incident)
    categories = await db.get_categories()
    norm_incident = normalize_incident(incident, *categories)
    await db.insert_norm_incident(norm_incident)
    return incident


def remove_user_incident(uid):
    db.delete_user_incident({'myId': uid})
    db.delete_norm_user_incident({'refId': uid})
