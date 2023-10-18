def plus1(redis_entity, key, expire=None):
    try:
        val = redis_entity.get(key)
        if val is None:
            val = 0
        return redis_entity.set(key, int(val) + 1, expire)
    except:
        return redis_entity.set(key, 1, expire)


def minus1(redis_entity, key, expire=None):
    try:
        val = redis_entity.get(key)
        if val is None:
            val = 0
        return redis_entity.set(key, int(val) - 1, expire)
    except:
        return redis_entity.set(key, 0, expire)
