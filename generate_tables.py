# coding:utf-8
import shotgun_api3
import psycopg2
sg = shotgun_api3.Shotgun("https://yoursite.shotgunstudio.com",
                          script_name="your script",
                          api_key="your key")

conn = psycopg2.connect(database="", user="", password="", host="", port="5432")
c = conn.cursor()
schema_info = sg.schema_read({'type': 'Project', 'id': 1})# this method may be a little slow, otherwise you can save this info to a json file if you got this problem.
lll = len(schema_info.keys())
i = 0
for entity, entity_value in schema_info.iteritems():
    print i, lll
    if entity in ['Group']:
        continue
    script = '(ID INT PRIMARY KEY NOT NULL,'
    for field, filed_value in entity_value.iteritems():
        if field in ['id', 'group', 'user']:
            continue
        field_type = filed_value.get('data_type').get('value')
        sqlite_field_type = 'INT' if 'number' in field_type else 'TEXT'
        script += field + ' ' + sqlite_field_type + ','
        pass
    script = script.rstrip(',')
    script += ');'
    i += 1
    full_script = '''CREATE TABLE %s %s'''%(entity, script)
    print full_script
    c.execute(full_script)
conn.commit()
conn.close()








