import pymysql
import redis
import json
import copy


class MySQLUtils:
    def __init__(
        self, host, port, user, pwd, default_db, table_name=None, charset=None
    ):
        self.host, self.port = host, port
        self.user, self.pwd = user, pwd
        self.default_db = default_db
        self.table_name = table_name
        self.charset = charset
        self.db_instance = None
        self.cursor_to_db = None
        self.connected = False

    @property
    def loc(self):
        return (
            f"`{self.default_db}`" + (f".`{self.table_name}`")
            if self.table_name is not None
            else ""
        )

    def connect(self):
        try:
            if self.connected:
                self.db_instance.ping(True)
                return True
            if self.cursor_to_db is not None:
                self.cursor_to_db.close()
                self.cursor_to_db = None
            if self.db_instance is not None:
                self.db_instance.close()
                self.db_instance = None

            self.db_instance = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.pwd,
                database=self.default_db,
                charset=self.charset,
            )
            self.cursor_to_db = self.db_instance.cursor()
        except Exception as e:
            self.connected = False
            self.db_instance = None
            self.cursor_to_db = None
            raise Exception(f"connection failed. err={e}")
        else:
            self.connected = True
            return True

    def disconnect(self):
        if not self.connected:
            return True
        try:
            self.connected = False
            self.cursor_to_db.close()
            self.db_instance.close()
            self.cursor_to_db = None
            self.db_instance = None
            return True
        except Exception as e:
            raise Exception(f"failed to disconnect. err={e}")

    def execute_cmd(self, cmd):
        try:
            self.connect()
            affected = self.cursor_to_db.execute(cmd)
            fetch_results = list(self.cursor_to_db.fetchall())
            self.db_instance.commit()
            return affected, fetch_results
        except Exception as e:
            try:
                self.db_instance.rollback()
            except:
                pass
            raise Exception(f"execution failed. err={e}")

    def get(self, match_q):  # [{and, and}, <or> {and, and}]
        cmd = f"SELECT * FROM {self.loc} "
        cmd += " WHERE " if len(match_q) > 0 else ""
        for i, q_or_relation in enumerate(match_q):
            if i != 0:
                cmd += " or "
            cmd += (
                "("
                + " and ".join(
                    [
                        f"`{q_and_relation[0]}` = '{q_and_relation[1]}'"
                        for q_and_relation in q_or_relation.items()
                    ]
                )
                + ")"
            )
        return self.execute_cmd(cmd)

    def add(self, data):  # [{columns},{columns}]
        res = []
        for item in data:
            keys, vals = [f"`{key}`" for key in item.keys()], [
                f"'{val}'" for val in item.values()
            ]
            keys = ",".join(keys)
            vals = ",".join(vals)
            cmd = f"INSERT INTO {self.loc} ({keys}) VALUES ({vals})"
            res.append(self.execute_cmd(cmd))

    def remove(self, match_q):  # [{and, and}, <or> {and, and}]
        cmd = f"DELETE FROM {self.loc} "
        cmd += " WHERE " if len(match_q) > 0 else ""
        for i, q_or_relation in enumerate(match_q):
            if i != 0:
                cmd += " or "
            cmd += (
                "("
                + " and ".join(
                    [
                        f"`{q_and_relation[0]}` = '{q_and_relation[1]}'"
                        for q_and_relation in q_or_relation.items()
                    ]
                )
                + ")"
            )
        return self.execute_cmd(cmd)

    def modify(self, match_q, new_content):
        cmd = f"UPDATE {self.loc} SET "

        cmd += ", ".join(
            [
                f"`{q_kv_pairs[0]}` = '{q_kv_pairs[1]}'"
                for q_kv_pairs in new_content.items()
            ]
        )

        cmd += " WHERE "
        for i, q_or_relation in enumerate(match_q):
            if i != 0:
                cmd += " or "
            cmd += (
                "("
                + " and ".join(
                    [
                        f"`{q_and_relation[0]}` = '{q_and_relation[1]}'"
                        for q_and_relation in q_or_relation.items()
                    ]
                )
                + ")"
            )
        return self.execute_cmd(cmd)


class RedisUtils:
    def __init__(self, host, port, user=None, pwd=None, db_num=None, charset="utf-8"):
        self.host, self.port = host, port
        self.user, self.pwd = user, pwd
        self.db_num = db_num
        self.charset = charset
        self.db_instance = None
        self.connected = False

    @property
    def loc(self):
        return self.db_num

    def connect(self):
        try:
            if self.connected:
                if not self.db_instance.ping():
                    self.connected = False
                    self.db_instance.close()
                    self.db_instance = None
                    return False
                return True
            if self.db_instance is not None:
                self.db_instance.close()
                self.db_instance = None

            self.db_instance = redis.Redis(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.pwd,
                db=self.db_num,
                encoding=self.charset,
            )
        except Exception as e:
            self.connected = False
            self.db_instance = None
            raise Exception(f"connection failed. err={e}")
        else:
            self.connected = True
            return True

    def disconnect(self):
        if not self.connected:
            return True
        try:
            self.connected = False
            self.db_instance.close()
            self.db_instance = None
            return True
        except Exception as e:
            raise Exception(f"failed to disconnect. err={e}")

    def execute_cmd(self, cmd):
        try:
            return self.db_instance.execute_command(cmd)
        except Exception as e:
            raise Exception(f"execution failed. err={e}")

    def get(self, name):
        try:
            self.connect()
            return self.db_instance.get(name)
        except Exception as e:
            raise Exception(f"failed to get. err={e}")

    def set(self, name, value, expire=None):
        try:
            self.connect()
            return self.db_instance.set(name, value, expire)
        except Exception as e:
            raise Exception(f"failed to set. err={e}")

    def lappend_list(self, name, val):
        try:
            self.connect()
            return self.db_instance.lpush(name, val)
        except Exception as e:
            raise Exception(f"failed to lappend list. err={e}")

    def rappend_list(self, name, val):
        try:
            self.connect()
            return self.db_instance.rpush(name, val)
        except Exception as e:
            raise Exception(f"failed to rappend list. err={e}")

    def set_dict(self, name, vals):
        try:
            self.connect()
            return self.db_instance.hset(name, mapping=vals)
        except Exception as e:
            raise Exception(f"failed to set dict. err={e}")

    def flush(self, asynchronous=False):
        try:
            self.connect()
            return self.db_instance.flushdb(asynchronous)
        except Exception as e:
            raise Exception(f"failed to flush. err={e}")

    def flush_all(self, asynchronous=False):
        try:
            self.connect()
            return self.db_instance.flushall(asynchronous)
        except Exception as e:
            raise Exception(f"failed to flush all. err={e}")

    def delete(self, names):
        try:
            self.connect()
            return self.db_instance.delete(names)
        except Exception as e:
            raise Exception(f"failed to delete. err={e}")

    def insert_json(self, name, value, expire=None):
        try:
            val = self.get_json(name)
            ret_val = copy.deepcopy(val)
            if val is None:
                val = value
            elif isinstance(val, list):
                if isinstance(value, list):
                    for item in value:
                        val.append(str(item))
                else:
                    val.append(str(value))
            elif isinstance(val, dict):
                if isinstance(value, dict):
                    for k, v in value.items():
                        val[k] = v
                else:
                    raise Exception(f"type {type(value)} can not be added to dict")
            else:
                val = val + value
            self.set(name, json.dumps(val), expire=expire)
            return ret_val  # old value
        except Exception as e:
            raise Exception(f"failed to insert. err={e}")

    def get_json(self, name, repl=None):
        res = self.get(name)
        return json.loads(res) if res is not None else repl

    def set_json(self, name, value, expire=None):
        return self.set(name, json.dumps(value), expire)

    def select_db(self, db_index):
        try:
            self.connect()
            return self.db_instance.select(db_index)
        except Exception as e:
            raise Exception(f"failed to select db. err={e}")
