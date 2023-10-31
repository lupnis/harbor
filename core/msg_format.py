from pathlib import Path


def gen_message(status, message=None, data=None, ext=None):
    return {"res": status, "msg": message, "data": data, "ext": ext}


def default_config():
    return {
        "general": {
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_pwd": None,
            "redis_usr": None,
        },
        "file_server": {
            "api_file_download": "/file/download",
            "api_file_manage": "/file/manage",
            "api_file_upload": "/file/upload",
            "db": 15,
            "file_download_count_limit": 32,
            "file_keep_time_limit": 604800,
            "file_sorage_path": str(Path("./upload").absolute()),
            "listen_port": 9002,
            "upload_size_limit": 33554432,
        },
        "ticket_server": {
            "api_ticket_destory": "/api/ticket/destory",
            "api_ticket_manage": "/api/ticket/manage",
            "api_ticket_provide": "/api/ticket/get",
            "db": 15,
            "limit_req_count": 60,
            "listen_port": 9001,
            "list_show_count": 32,
            "ticket_expire_secs": 3600,
            "whitelist": ["127.0.0.1", "::1"],
            "vc_pe_expire_secs": 60,
        },
    }
