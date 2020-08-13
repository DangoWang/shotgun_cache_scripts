# coding:utf-8
import shotgun_api3
import psycopg2
import json
sg = shotgun_api3.Shotgun("https://yoursite.shotgunstudio.com",
                          script_name="your script",
                          api_key="your key")
conn = psycopg2.connect(database="", user="", password="", host="", port="5432")

entities_to_cache = ['Project', 'HumanUser', 'TaskTemplate', 
                      'Step',
                      'Note', 'Attachment', 'Task', 'Asset', 'Shot', 'Version']
projects_ids_to_cache = []

c = conn.cursor()
schema_info = sg.schema_read({'type': 'Project', 'id': 1})# this method may be a little slow, otherwise you can save this info to a json file if you got this problem.
lll = len(schema_info.keys())
j = 0
for entity, entity_value in schema_info.iteritems():
    print j, lll, entity
    j += 1
    if entity not in entities_to_cache:
        continue
    if entity in ['Group']:
        continue
    all_fields = entity_value.keys()
    all_fields_values_list = sg.find(entity, [['project.Project.id', 'in', projects_to_cache]], all_fields)
    for all_fields_values in all_fields_values_list:
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
        entity_type = entity
        entity_id = all_fields_values.get('id')
        c.execute("SELECT ID from %s" % entity_type)
        all_ids_search = c.fetchall()
        all_ids_search = all_ids_search or []
        all_ids = [a[0] for a in all_ids_search]
        temp = {}
        for i, field in enumerate(updating_fields):
            temp[field] = updating_values[i]
        temp = json.loads(json.dumps(temp, ensure_ascii=False), encoding='utf-8')
        execute_script = []
        if not entity_id in all_ids:
            execute_script.append("insert into %s (%s) values (%s)" % (entity_type, 'id', entity_id))
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
            execute_script.append('update %s set %s=%s where id=%s' % (entity_type, k,  v, entity_id))
        for es in execute_script:
            try:
                c.execute(es)
            except Exception as e:
                print es
                raise
conn.commit()
conn.close()









