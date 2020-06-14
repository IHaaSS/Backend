import pymongo
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from calculations.calculate import calculate_cosine
from normalization.norm import normalize_incident, generate_id_list, reverse_norm_incident
from generation.questionGeneration import generate_question, get_attribute_name, generate_counter_question, \
    generate_mc_question
import json
from flask_pymongo import PyMongo
from bson.json_util import dumps, loads

app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = 'test'
app.config["MONGO_URI"] = 'mongodb+srv://admin:waschbecken@ba-tool-c4fgc.mongodb.net/test?retryWrites=true&w=majority'
mongo = PyMongo(app)
db = mongo.db
coll_i = db.predef_incidents
coll_ui = db.user_incidents
coll_ni = db.norm_incidents
coll_nui = db.norm_userIncidents
coll_sour = db.sources
coll_eve = db.events
coll_ent = db.entities
coll_im = db.impacts
coll_que = db.questions
coll_counter_que = db.counter_questions
coll_rel = db.relations


# reference incidents


@app.route('/incidents', methods=['GET'])
def get_incidents():
    incidents = dumps(coll_i.find())
    return incidents


@app.route('/incidents', methods=['POST'])
def post_incident():
    body = request.get_json()
    incident = body
    idList = list(coll_i.find())
    if len(idList) == 0:
        incident['myId'] = 0
    elif len(idList) > 0:
        incident['myId'] = coll_i.find_one(sort=[('myId', pymongo.DESCENDING)])['myId'] + 1;
    incident['transmittedBy'] = 'admin'
    coll_i.insert_one(incident)
    post_norm_ref_incident(incident)
    return dumps(incident)


@app.route('/incidents/<incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    coll_i.delete_one({'_id': incident_id})
    return '', 200


@app.route('/transferIncidents', methods=['POST'])
def post_StagedIncident():
    body = request.get_json()
    incident = {'title': body['title'], 'sources': body['sources'], 'events': body['events'],
                'entities': body['entities'], 'impacts': body['impacts'], 'transmittedBy': 'user'}
    id = coll_i.find_one(sort=[('myId', pymongo.DESCENDING)])['myId']
    if (id is None):
        incident['myId'] = 0
    else:
        incident['myId'] = id + 1;
    coll_i.insert_one(incident)
    post_norm_ref_incident(incident)
    delete_user_incident(body['myId'])
    return dumps(incident)


# normalized reference incidents


@app.route('/norm_incidents', methods=['GET'])
def get_norm_ref_incidents():
    incidents = coll_ni.find()
    return dumps(incidents)


@app.route('/norm_incidents', methods=['POST'])
def post_norm_ref_incident(incident):
    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    norm_incident = normalize_incident(incident, sources, events, entities, impacts)
    coll_ni.insert_one(norm_incident)
    return dumps(norm_incident)


@app.route('/norm_incidents/<incident_id>', methods=['DELETE'])
def delete_norm_incident(incident_id):
    coll_ni.delete_one({'id': incident_id})
    return '', 200


# user incidents


@app.route('/user_incidents', methods=['GET'])
def get_user_incidents():
    incidents = dumps(coll_ui.find())
    return incidents


def get_user_incident(incident_id):
    return coll_ui.find_one({'myId': incident_id})


@app.route('/user_incidents', methods=['POST'])
def post_user_incident():
    body = request.get_json()
    user_incident = body
    idList = list(coll_ui.find())
    if len(idList) == 0:
        user_incident['myId'] = 0
    else:
        user_incident['myId'] = coll_ui.find_one(sort=[('myId', pymongo.DESCENDING)])['myId'] + 1
    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    norm_user_incident = post_norm_user_incident(user_incident, sources, events, entities, impacts)
    norm_ref_incidents = get_norm_ref_incidents()
    question_response = execute_completion(user_incident, sources, events, entities, impacts, norm_user_incident, norm_ref_incidents)
    coll_ui.insert_one(user_incident)
    return question_response


@app.route('/user_incidents/<incident_id>', methods=['DELETE'])
def delete_user_incident(incident_id):
    if incident_id is None:
        incident_id = request.get()
    coll_ui.delete_one({'myId': incident_id})
    coll_nui.delete_one({'refId': incident_id})
    return ''

# normalized user incident


@app.route('/norm_UserIncidents', methods=['POST'])
def post_norm_user_incident(incident, sources, events, entities, impacts):
    norm_incident = normalize_incident(incident, sources, events, entities, impacts)
    coll_nui.insert_one(norm_incident)
    return norm_incident


def delete_norm_user_incident(incident_id):
    coll_nui.delete_one({'refId': incident_id})
    return '', 200


def get_norm_user_incident(id):
    incidents = dumps(coll_nui.find({'refId': id}))
    return json.loads(incidents)[0]


# get topics / attributes


@app.route('/sources', methods=['GET'])
def get_sources():
    sources = dumps(coll_sour.find())
    return sources


@app.route('/impacts', methods=['GET'])
def get_impacts():
    impacts = dumps(coll_im.find())
    return impacts


@app.route('/events', methods=['GET'])
def get_events():
    events = dumps(coll_eve.find())
    return events


@app.route('/entities', methods=['GET'])
def get_entities():
    entities = dumps(coll_ent.find())
    return entities


# questions


@app.route('/questions', methods=['POST'])
def post_question():
    body = request.get_json()
    q = {}
    idList = list(coll_que.find())
    if len(idList) == 0:
        q['questionId'] = 0
    else:
        q['questionId'] = coll_que.find_one(sort=[('questionId', pymongo.DESCENDING)])['questionId'] + 1
    q['text'] = body['text']
    post_relation(q['questionId'], body)
    if 'counterText' in body:
        if len(body['counterText']) > 0:
            q_counter = q
            q_counter['text'] = body['counterText']
            coll_counter_que.insert_one(q_counter)
    coll_que.insert_one(q)
    return dumps(q)


# toDo: shorten it
@app.route('/relations', methods=['POST'])
def post_relation(question_id, temp):
    re = {}
    for source in temp['sources']:
        t = source['source']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 1, 'attributeId': t[-1]}
            coll_rel.insert_one(r)
    for event in temp['events']:
        t = event['event']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 2, 'attributeId': t[-1]}
            coll_rel.insert_one(r)
    for entity in temp['entities']:
        t = entity['entity']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 3, 'attributeId': t[-1]}
            coll_rel.insert_one(r)
    for impact in temp['impacts']:
        t = impact['impact']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 4, 'attributeId': t[-1]}
            coll_rel.insert_one(r)
    return dumps(re)


# get all questions that answer attribute
def get_questions(ids, phase):
    result = []
    copy_ids = set()
    for element in ids['sources']:
        if element not in copy_ids:
            result.append(get({}, element, ids['sources'], 1, copy_ids, phase))
    copy_ids = set()
    for element in ids['events']:
        if element not in copy_ids:
            result.append(get({}, element, ids['events'], 2, copy_ids, phase))
    copy_ids = set()
    for element in ids['entities']:
        if element not in copy_ids:
            result.append(get({}, element, ids['entities'], 3, copy_ids, phase))
    copy_ids = set()
    for element in ids['impacts']:
        if element not in copy_ids:
            result.append(get({}, element, ids['impacts'], 4, copy_ids, phase))
    return result


def get(result, attr_id, ids, topic_id, copy_ids, phase):
    relations = coll_rel.find({'attributeId': attr_id, 'topicId': topic_id})
    result['questions'] = []
    result['children'] = []
    # generic question get created (refinement + completion)
    question = generate_generic_question(attr_id, topic_id, phase)
    result['questions'].append(question)
    copy_ids.add(attr_id)
    # completion
    if phase == 1:
        for r in relations:
            # load manually created questions from db
            temp = coll_que.find({'questionId': r['questionId']})
            for t in temp:
                q = generate_specific_question(t, r['attributeId'], topic_id)
                result['questions'].append(q)
        # load questions following attribute hierarchy
        for element in ids:
            if element[:-2] == attr_id:
                copy_ids.add(element)
                result['children'].append(get({}, element, ids, topic_id, copy_ids, phase))
    # refinement
    else:
        for r in relations:
            # find existing counter questions for relation
            temp = coll_counter_que.find({'questionId': r['questionId']})
            # if counter questions exist
            if len(list(temp)) > 0:
                for t in temp:
                    q = generate_specific_question(t, r['attributeId'], topic_id)
                    result['questions'].append(q)
            # if counter question does not exist
            #else:
                # find non-counter question
                #q_positive = coll_que.find({'questionId': r['questionId']})
                # generate counter question for non-counter questions
                #for q in q_positive:
                    #q = generate_manual_counter_question(q, r['attributeId'], topic_id)
                    #result['questions'].append(q)
    if len(result['children']) == 0:
        del result['children']
    return result


def generate_generic_question(attr_id, topic_id, phase):
    if topic_id == 1:
        sources = get_sources()
        attribute = get_attribute_name(attr_id, sources)
    if topic_id == 2:
        events = get_events()
        attribute = get_attribute_name(attr_id, events)
    if topic_id == 3:
        entities = get_entities()
        attribute = get_attribute_name(attr_id, entities)
    if topic_id == 4:
        impacts = get_impacts()
        attribute = get_attribute_name(attr_id, impacts)
    if phase == 1:
        question = {'text': generate_question(attribute), 'answer': 0, 'questionId': 0, 'attrId': attr_id,
                    'topicId': topic_id}
    else:
        question = {'text': generate_counter_question(attribute), 'answer': 0, 'questionId': 0, 'attrId': attr_id,
                    'topicId': topic_id}
    if attr_id[:-2]:
        question['parentId'] = attr_id[:-2]
    return question


def generate_specific_question(q, attribute_id, topic_id):
    question = {'text': q['text'], 'answer': 0, 'questionId': q['questionId'], 'attrId': attribute_id,
                'topicId': topic_id}
    if attribute_id[:-2]:
        question['parentId'] = attribute_id[:-2]
    return question


def generate_manual_counter_question(q, attribute_id, topic_id):
    question = {'text': generate_mc_question(q['text']), 'answer': 0, 'questionId': q['questionId'],
                'attrId': attribute_id,
                'topicId': topic_id}
    if attribute_id[:-2]:
        question['parentId'] = attribute_id[:-2]
    return question


# handle response from frontend after user answered questions


@app.route('/answer', methods=['POST'])
def post_answer():
    body = request.get_json()
    nui = get_norm_user_incident(body['id'])
    ui = get_user_incident(body['id'])
    copy_nui = get_norm_user_incident(body['id'])
    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    ref_norm_incidents = get_norm_ref_incidents()
    s = generate_id_list(json.loads(sources)[0], [])
    ev = generate_id_list(json.loads(events)[0], [])
    en = generate_id_list(json.loads(entities)[0], [])
    im = generate_id_list(json.loads(impacts)[0], [])

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
        user_incident = get_user_incident(u['refId'])
        rev_incident = reverse_norm_incident(u, sources, events, entities, impacts, user_incident)
        coll_ui.delete_one({'myId': u['refId']})
        coll_ui.insert_one(rev_incident)
        return {'id': u['refId'], 'questions': [], 'phase': 2}
    if body['phase'] == 1:
        coll_nui.delete_one({'refId': u['refId']})
        coll_nui.insert_one(u)
        return execute_refinement(u, copy_nui, ref_norm_incidents, sources, events, entities, impacts, s, ev, en, im, body)

# completion


def execute_completion(user_incident, sources, events, entities, impacts, norm_user_incident, norm_ref_incidents):
    question_ids = calculate_cosine(norm_user_incident, norm_ref_incidents, sources, events, entities, impacts, 1, None)
    questions = get_questions(question_ids, 1)
    if len(question_ids) == 0:
        question_ids = calculate_cosine(norm_user_incident, norm_ref_incidents, sources, events, entities, impacts, 2,
                                        norm_user_incident)
        if len(question_ids) == 0:
            return {'id': norm_user_incident['refId'], 'questions': [], 'phase': 2}
        else:
            questions = get_questions(question_ids, 2)
            question_response = {'id': norm_user_incident['refId'], 'questions': questions, 'phase': 2}
            return question_response
    else:
        question_response = {'id': user_incident['myId'], 'questions': questions, 'phase': 1}
    return question_response

# refinement


def execute_refinement(u, copy_nui, ref_norm_incidents, sources, events, entities, impacts, s, ev, en, im, body):
    temp = {'title': copy_nui["title"], 'refId': copy_nui["refId"],
            'normSources': create_temp_incident(copy_nui['normSources'], s, body['answers'], 1),
            'normEvents': create_temp_incident(copy_nui['normEvents'], ev, body['answers'], 2),
            'normEntities': create_temp_incident(copy_nui['normEntities'], en, body['answers'], 3),
            'normImpacts': create_temp_incident(copy_nui['normImpacts'], im, body['answers'], 4)}
    question_ids = calculate_cosine(u, ref_norm_incidents, sources, events, entities, impacts, 2, temp)
    if len(question_ids) == 0:
        return {'id': u['refId'], 'questions': [], 'phase': 2}
    else:
        questions = get_questions(question_ids, 2)
        question_response = {'id': u['refId'], 'questions': questions, 'phase': 2}
        return question_response


def update_norm_user_incident(vector, attr_list, answers, phase, topic_id):
    for answer in answers:
        if answer['topicId'] == topic_id:
            if phase == 1:
                vector[attr_list.index(answer['attributeId'])] = answer['value']
                if answer['value'] > 0:
                    check_for_lower_granularity(attr_list, vector, answer['attributeId'])
            else:
                vector[attr_list.index(answer['attributeId'])] = abs(answer['value'] - 1)
    return vector


def create_temp_incident(vector, attr_list, answers, topic_id):
    for answer in answers:
        if answer['topicId'] == topic_id:
            vector[attr_list.index(answer['attributeId'])] = 0
            check_for_lower_granularity(attr_list, vector, answer['attributeId'])
    return vector


def check_for_lower_granularity(list_source, nui_attrs, attr_Id):
    if attr_Id[:-2]:
        nui_attrs[list_source.index(attr_Id[:-2])] = 0
        check_for_lower_granularity(list_source, nui_attrs, attr_Id[:-2])
    else:
        return nui_attrs


app.run(debug=True)
