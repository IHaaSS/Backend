import os
import pymongo
from pymongo import MongoClient

db = 'test'
uri = 'mongodb://' + os.getenv('MONGO_USER') + ':' + os.getenv('MONGO_PASS') + '@' + os.getenv('MONGO_IP') +\
      ':27017/test?retryWrites=true&w=majority'

client = MongoClient(uri)
db = client[db]
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


def get_incidents():
    return coll_i.find()


def insert_incident(incident):
    id = coll_i.find_one(sort=[('myId', pymongo.DESCENDING)])#
    if id is None:
        incident['myId'] = 0
    else:
        incident['myId'] = id['myId'] + 1
    coll_i.insert_one(incident)


def delete_incident(incident_id):
    coll_i.delete_one({'_id': incident_id})


def get_norm_incidents():
    return coll_ni.find()


def insert_norm_incident(norm_incident):
    coll_ni.insert_one(norm_incident)


def delete_norm_incident(incident_id):
    coll_ni.delete_one({'id': incident_id})


def get_norm_user_incident(id):
    return coll_nui.find_one({'refId': id})


def insert_norm_user_incident(incident):
    coll_nui.insert_one(incident)


def delete_norm_user_incident(incident_id):
    coll_nui.delete_one({'refId': incident_id})
    return '', 200


def get_user_incidents():
    return coll_ui.find()


def get_user_incident(id):
    return coll_ui.find({'refId': id})


def get_new_user_incident_id():
    id = coll_ui.find_one(sort=[('myId', pymongo.DESCENDING)])
    return 0 if id is None else id['myId']+1


def insert_user_incident(incident):
    coll_ui.insert_one(incident)


def delete_user_incident(incident_id):
    coll_ui.delete_one({'refId': incident_id})
    return '', 200


def get_sources():
    return coll_sour.find_one()


def get_impacts():
    return coll_im.find_one()


def get_events():
    return coll_eve.find_one()


def get_entities():
    return coll_ent.find_one()


def get_questions():
    return coll_que.find()


def get_new_question_id():
    id = coll_que.find_one(sort=[('questionId', pymongo.DESCENDING)])
    return 0 if id is None else id['questionId']+1


def insert_question(question):
    coll_que.insert_one(question)


def get_question(question_id):
    return coll_que.find({'questionId': question_id})


def get_question_counter(question_id):
    return coll_counter_que.find({'questionId': question_id})


def insert_question_counter(question_counter):
    coll_counter_que.insert_one(question_counter)


def insert_relation(question_id, topic_id, attribute_id):
    coll_rel.insert_one({
        'questionId': question_id,
        'topicId': topic_id,
        'attributeId': attribute_id
    })


def get_relations(attribute_id, topic_id):
    return coll_rel.find({
        'attributeId': attribute_id,
        'topicId': topic_id
    })
