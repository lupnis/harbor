import utils.redis_ops as rops


def gen_ticket_str(ip):
    return f"ts:ti:{ip}"


def gen_req_cnt_str(ip):
    return f"ts:rc:{ip}"


def gen_peasant_str(ip):
    return f"ts:pe:{ip}"


def record_ip_visit(redis_entity, ip, expire=None):
    rops.plus1(
        redis_entity,
        gen_req_cnt_str(ip),
        get_upd_ttl(redis_entity, gen_req_cnt_str(ip), expire),
    )


def judge_ip_peasant(redis_entity, ip, limit):
    cnt = redis_entity.get(gen_req_cnt_str(ip))
    if cnt is None:
        cnt = 0
    return int(cnt) > limit


def add_ip_peasant(redis_entity, ip, expire=None):
    return redis_entity.set(gen_peasant_str(ip), 1, expire)


def ip_peasant(redis_entity, ip):
    return redis_entity.get(gen_peasant_str(ip)) is not None


def in_whitelist(config_handler, ip):
    whitelist = config_handler.get("whitelist", [])
    return ip in whitelist


def add_ticket(redis_entity, ip, ticket, expire=None):
    return redis_entity.set(gen_ticket_str(ip), ticket, expire)


def check_ticket(redis_entity, ip, ticket):
    ret = redis_entity.get(gen_ticket_str(ip))
    if ret is None:
        return False
    ret = ret.decode() if isinstance(ret, bytes) else str(ret)
    return ret == ticket


def withdraw_ticket(redis_entity, ip):
    ret = redis_entity.delete(gen_ticket_str(ip))
    return ret


def get_upd_ttl(redis_entity, key, expire=None):
    ttl = redis_entity.db_instance.ttl(key)
    return ttl if ttl > 0 else expire


def visit_control(config_handler, redis_entity, ip):
    # stage 1. judge if source IP is alread blocked
    if ip_peasant(redis_entity, ip) and not in_whitelist(config_handler, ip):
        return False
    # stage 2. update visit status and judge if to block source IP
    record_ip_visit(redis_entity, ip, config_handler.get("vc_pe_expire_secs", 60))
    if judge_ip_peasant(
        redis_entity, ip, config_handler.get("limit_req_count", 120)
    ) and not in_whitelist(config_handler, ip):
        add_ip_peasant(redis_entity, ip, config_handler.get("vc_pe_expire_secs", 60))
        return False
    return True
