# coding:utf-8
import psycopg2

postgre_config = dict(database="", user="", password="", host="", port="5432")

def registerCallbacks(reg):
    event_filter = {}
    reg.registerCallback(
        'your script name',
        'password',
        cache_data,
        event_filter,
        None,
    )
    reg.logger.info("Registered callback.=================================\n\n\n\n")

def cache_data(sg, logger, event, args):
    schema_info = sg.schema_read({'type': 'Project', 'id': 1}) # this method may be a little slow, otherwise you can save this info to a json file if you got this problem.
    if not event:
        return
    if not event.get('entity'):
        return
    entity_type = event.get('entity').get('type')
    entity_id = event.get('entity').get('id')
    all_entities = schema_info.keys()
    entity_fields = schema_info.get(entity_type, {}).keys()
    if entity_type in  ['Group']:
        return
    if not entity_type in all_entities or not entity_fields:
        return
    if not event.get('event_type').split('_')[-1] in ['Change', 'Retirement']:
        return
    if not event.get('event_type').split('_')[1] in all_entities:
        return
    all_fields = [fl for fl in entity_fields if 'group' not in fl.lower()]
    while 1:
        try:
            all_fields_values = sg.find_one(entity_type, [['id', 'is', entity_id]], all_fields)
            break
        except:
            continue
    if not all_fields_values:
        return
    updating_fields = []
    updating_values = []
    for field_name, field_value in all_fields_values.iteritems():
        if field_name in ['type', 'None', 'user']:
            continue
        if isinstance(field_value, dict):
            updating_fields.append(field_name)
            v = field_value
            updating_values.append(v)
        elif isinstance(field_value, list) and len(field_value) > 0:
            first_dict = field_value[0]
            if not isinstance(first_dict, dict):
                continue
            updating_fields.append(field_name)
            v = first_dict
            updating_values.append(v)
        else:
            updating_fields.append(field_name)
            field_value = str(field_value) if field_value else 'null'
            updating_values.append(field_value)
    conn = psycopg2.connect(**postgre_config)
    c = conn.cursor()
    c.execute("SELECT id from %s" % entity_type) or []
    all_ids_search = c.fetchall()
    all_ids = []
    if all_ids_search:
        all_ids = [ai[0] for ai in list(all_ids_search)]
    temp = {}
    for i, field in enumerate(updating_fields):
        temp[field] = updating_values[i]
    execute_script = []
    if not entity_id in all_ids:
        create_script = "INSERT INTO %s (%s) VALUES (%s)" % (entity_type, 'id', entity_id)
        c.execute(create_script)
    update_list = []
    for k, v in temp.iteritems():
        if isinstance(v, dict):
            v = "'"+str(v).replace("'", '"') + "'"
        elif isinstance(v, int) or isinstance(v, float):
            v = str(v)
        elif isinstance(v, unicode) or isinstance(v, str):
            v = "'"+v.replace("'", '"')+"'" if v != 'null' else 'null'
        else:
            v = "'" + str(v) + "'"
        if k in ['None', 'none'] or v in ['None', 'none']:
            continue
        update_list.append(k + '=' + v)
    update_script = 'UPDATE %s SET %s WHERE ID=%s' % (entity_type, ','.join(update_list), entity_id)
    c.execute(update_script)
    conn.commit()
    conn.close()



















