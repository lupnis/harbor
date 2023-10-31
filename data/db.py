import redis
import json
import copy


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
