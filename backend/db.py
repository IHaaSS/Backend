from flask import Blueprint, request

from bson import json_util
from backend.storage import mongo as db
from backend.storage.mongo import get_norm_user_incident

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
def post_incident():
    body = request.get_json()
    incident = body
    incident['transmittedBy'] = 'admin'
    db.insert_incident(incident)
    post_norm_ref_incident(incident)
    return json_util.dumps(incident)


@bp.route('/incidents/<incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    db.delete_incident(incident_id)
    return '', 200


@bp.route('/transferIncidents', methods=['POST'])
def post_StagedIncident():
    body = request.get_json()
    incident = {'title': body['title'], 'sources': body['sources'], 'events': body['events'],
                'entities': body['entities'], 'impacts': body['impacts'], 'transmittedBy': 'user'}
    db.insert_incident(incident)
    post_norm_ref_incident(incident)
    delete_user_incident(body['myId'])
    return json_util.dumps(incident)

################################
# normalized reference incidents
################################


@bp.route('/norm_incidents', methods=['GET'])
def get_norm_ref_incidents():
    incidents = db.get_norm_incidents()
    return json_util.dumps(incidents)


@bp.route('/norm_incidents', methods=['POST'])
def post_norm_ref_incident(incident):
    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    norm_incident = normalize_incident(incident, sources, events, entities, impacts)
    db.insert_norm_incident(norm_incident)
    return json_util.dumps(norm_incident)


@bp.route('/norm_incidents/<incident_id>', methods=['DELETE'])
def delete_norm_incident(incident_id):
    db.delete_norm_incident(incident_id)
    return '', 200


#################
# user incidents
#################

@bp.route('/user_incidents', methods=['GET'])
def get_user_incidents():
    incidents = db.get_user_incidents()
    return json_util.dumps(incidents)


@bp.route('/user_incidents', methods=['POST'])
def post_user_incident():
    body = request.get_json()
    user_incident = body
    user_incident['myId'] = db.get_new_user_incident_id()
    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    norm_user_incident = post_norm_user_incident(user_incident, sources, events, entities, impacts)
    norm_ref_incidents = get_norm_ref_incidents()
    question_response = execute_completion(user_incident, sources, events, entities, impacts, norm_user_incident, norm_ref_incidents)
    db.insert_user_incident(user_incident)
    db.insert_user_incident(user_incident)
    return question_response


@bp.route('/user_incidents/<incident_id>', methods=['DELETE'])
def delete_user_incident(incident_id):
    if incident_id is None:
        incident_id = request.get()
    db.delete_user_incident({'myId': incident_id})
    db.delete_norm_user_incident({'refId': incident_id})
    return ''

################################
# normalized user incident
################################


@bp.route('/norm_UserIncidents', methods=['POST'])
def post_norm_user_incident(incident, sources, events, entities, impacts):
    norm_incident = normalize_incident(incident, sources, events, entities, impacts)
    db.insert_norm_user_incident(norm_incident)
    return norm_incident


################################
# get topics / attributes
################################

@bp.route('/sources', methods=['GET'])
def get_sources():
    sources = db.get_sources()
    return json_util.dumps(sources)


@bp.route('/impacts', methods=['GET'])
def get_impacts():
    impacts = db.get_impacts()
    return json_util.dumps(impacts)


@bp.route('/events', methods=['GET'])
def get_events():
    events = db.get_events()
    return json_util.dumps(events)


@bp.route('/entities', methods=['GET'])
def get_entities():
    entities = db.get_entities()
    return json_util.dumps(entities)


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
def post_answer():
    body = request.get_json()
    nui = get_norm_user_incident(body['id'])
    ui = db.get_user_incident(body['id'])
    copy_nui = get_norm_user_incident(body['id'])
    sources = db.get_sources()
    events = db.get_events()
    entities = db.get_entities()
    impacts = db.get_impacts()
    ref_norm_incidents = get_norm_ref_incidents()
    s = generate_id_list(sources, [])
    ev = generate_id_list(events, [])
    en = generate_id_list(entities, [])
    im = generate_id_list(impacts, [])

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
        rev_incident = reverse_norm_incident(u, sources, events, entities, impacts, user_incident)
        db.delete_user_incident({'myId': u['refId']})
        db.insert_user_incident(rev_incident)
        return {'id': u['refId'], 'questions': [], 'phase': 2}
    if body['phase'] == 1:
        db.delete_norm_user_incident(u['refId'])
        db.insert_norm_user_incident(u)
        return execute_refinement(u, copy_nui, ref_norm_incidents, sources, events, entities, impacts, s, ev, en, im, body)

