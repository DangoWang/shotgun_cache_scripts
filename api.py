# coding:utf-8
import psycopg2
import json
os.environ['SG_PG_CONFIG'] = dict(database="", user="", password="", host="", port="5432")

class FindSqlCache:
    def __init__(self):
        pass

    def find(self, entity, filters, fields, order=None):
        self.conn = psycopg2.connect(**eval(os.environ['SG_PG_CONFIG']))
        self.cursor = self.conn.cursor()
        order_script = ''
        default_script = 'ORDER BY '
        if order:
            order_script = []
            for o in order:
                direction = 'DESC' if o.get('direction') == 'desc' else 'ASC'
                order_script.append(o.get('field_name') + ' ' + direction)
            order_script = ','.join(order_script)
            order_script = default_script + order_script
        order_script += ';'
        self.cursor.execute('SELECT ID FROM %s %s' % (entity, order_script))
        results_ids_temp = list(self.cursor.fetchall())
        results_ids = []
        for ri in results_ids_temp:
            results_ids.append(ri[0])
        result = self.__deal_with_filter(results_ids, entity, filters)  # 把拉取到的id进行过滤
        final_results = self.__deal_with_fields(result, entity, fields)
        self.conn.close()
        return final_results

    def __deal_with_filter(self, *args):
        results_ids, entity, filters = args
        if not filters:
            return results_ids
        final_results = []
        for id in results_ids:
            is_match = False
            deal_withed_result = False
            for fil in filters:
                if not fil:
                    is_match = True
                    continue
                deal_withed_result = self.__deal_with_jump_filter(entity, id, fil)
                if not deal_withed_result:
                    is_match = False
                    break
                is_match = True
            if is_match and deal_withed_result:
                final_results.append(id)
        return final_results

    def __deal_with_jump_filter(self, entity, id, fil):
        #  entity: Version
        #  fil: ['sg_task.Task.code', 'is', 'aaa']
        #  id:
        _filter, operate, limit = fil
        _filter_list = _filter.split('.')
        table = entity
        _id = id
        field = _filter_list[-1]
        i = 0
        while 1:
            if i+3 > len(_filter_list):
                r = False
                if operate == 'is':
                    s = "SELECT * FROM %s WHERE ID=%s AND %s='%s';" % (table, _id, field, limit)
                    self.cursor.execute(s)
                elif operate == 'in':
                    limit = ','.join(["'"+l+"'" for l in limit])
                    self.cursor.execute("SELECT * FROM %s WHERE ID=%s AND %s IN (%s);" % (table, _id, field, limit))
                elif operate == 'is_not':
                    self.cursor.execute("SELECT * FROM %s WHERE ID=%s AND NOT %s='%s';" % (table, _id, field, limit))
                elif operate == 'not_in':
                    limit = ','.join(["'" + l + "'" for l in limit])
                    self.cursor.execute("SELECT * FROM %s WHERE ID=%s AND %s NOT IN (%s);" % (table, _id, field, limit))
                elif operate == 'contains':
                    self.cursor.execute("SELECT * FROM %s WHERE ID=%s AND CONTAINS (%s, '%s');" % (table, _id, field,limit))
                else:
                    return False
                r = list(self.cursor.fetchall())
                if list(r):
                    return True
                return False
            else:
                script = "SELECT %s FROM %s WHERE ID=%s;" % (_filter_list[i], table, _id)
                self.cursor.execute(script)
                next_table_info = list(self.cursor.fetchall())
                ttt = list(next_table_info)[0][0]
                if not ttt:
                    return False
                _id = eval(ttt).get('id')
                table = _filter_list[i+1]
                field = _filter_list[i+2]
            i += 2

    def __deal_with_fields(self, result_ids, entity, fields):
        final_results = []
        for _id in result_ids:
            this_result = {'id': _id, 'type': entity}
            for f in fields:
                i = 0
                fields_list = f.split('.')
                field = fields_list[-1]
                table = entity
                __id = _id
                while 1:
                    if i+3 > len(fields_list):
                        self.cursor.execute(
                            "SELECT %s FROM %s WHERE ID=%s;" % (field, table, __id))
                        r = list(self.cursor.fetchall())
                        if not r:
                            this_result[f] = '-'
                        else:
                            fr = list(r)[0][0]
                            try:
                                this_result[f] = eval(fr)
                            except:
                                this_result[f] = fr
                        break
                    else:
                        self.cursor.execute(
                            "SELECT %s FROM %s WHERE ID=%s;" % (fields_list[i], table, __id))
                        next_table_info = list(self.cursor.fetchall())
                        if not next_table_info[0][0]:
                            this_result[f] = '-'
                            break
                        __id = eval(next_table_info[0][0]).get('id')
                        table = fields_list[i+1]
                        field = fields_list[i+2]
                    i += 2
            final_results.append(this_result)
        return json.loads(json.dumps(final_results))

    def find_one(self, entity, filters, fields):
        result = self.find(entity, filters, fields) or [{}]
        return result[0]