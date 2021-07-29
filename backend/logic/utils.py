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