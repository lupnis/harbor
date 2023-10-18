import utils.redis_ops as rops
import os

def gen_file_code_valid_countdown_str(file_code):
    return f"fs:cd:{file_code}"  # xxxxxxxx:5


def gen_file_code_reference_str(file_code):
    return f"fs:rr:{file_code}"  # xxxxxxxx:fwegubwuigheoihqoi


def gen_file_code_oriname_str(file_code):
    return f"fs:oo:{file_code}"  # xxxxxxxx:origin.txt


def check_file_availability(redis_entity, file_code):
    ret = redis_entity.get(gen_file_code_valid_countdown_str(file_code))
    if ret is None or int(ret) <= 0:
        return False
    return True


def check_file_size(config_handler, file):
    return len(file) <= config_handler.get("upload_size_limit", 33554432)  # 32MiB


def check_keep_time(config_handler, keep_time):
    return keep_time <= config_handler.get("file_keep_time_limit", 604800)  # 7 Days


def check_max_download(config_handler, download):
    return download <= config_handler.get("file_download_count_limit", 32)  # 32


def register_file(
    redis_entity,
    file_ori_name,
    file_hash_name,
    file_code,
    file_down_limit,
    file_time_limit,
):
    redis_entity.set(
        gen_file_code_valid_countdown_str(file_code), file_down_limit, file_time_limit
    )
    redis_entity.set(
        gen_file_code_reference_str(file_code), file_hash_name, file_time_limit
    )
    redis_entity.set(
        gen_file_code_oriname_str(file_code), file_ori_name, file_time_limit
    )


def get_file_info(redis_entity, file_code):
    filehash = redis_entity.get(gen_file_code_reference_str(file_code)).decode()
    filename = redis_entity.get(gen_file_code_oriname_str(file_code)).decode()
    return filehash, filename


def record_download(redis_entity, file_code, path):
    ttl = redis_entity.db_instance.ttl(gen_file_code_valid_countdown_str(file_code))
    if ttl ==-2:
        remove_file(redis_entity, file_code, path)
        return
    elif ttl <= 0:
        return
    
    rops.minus1(
        redis_entity,
        gen_file_code_valid_countdown_str(file_code),
        ttl
    )
    if int(redis_entity.get(gen_file_code_valid_countdown_str(file_code))) <= 0:
        remove_file(redis_entity, file_code, path)


def remove_file(redis_entity, file_code, path):
    try:
        redis_entity.delete(gen_file_code_valid_countdown_str(file_code))
        redis_entity.delete(gen_file_code_reference_str(file_code))
        redis_entity.delete(gen_file_code_oriname_str(file_code))
        os.remove(path)
    except:
        pass
