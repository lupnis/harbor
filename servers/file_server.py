if __name__ == "__main__":
    print("this module shall be run under the main.py container")
    exit(0)


from tornado.web import RequestHandler, Application
import tornado.httpserver
from tornado.escape import url_escape
import datetime
import aiofiles
import os
import time
from pathlib import Path

from data.db import RedisUtils
import core.visit_ctrl as vctrl
import core.file_ctrl as fctrl
import core.msg_format as mft
from data.codegen import CodeGenerator

config_handler_ts = None
config_handler_fs = None
redis_entity = None
hash_generator = None


class FileUploadController(RequestHandler):
    async def post(self):
        # record visit
        visit_from = self.request.remote_ip
        if vctrl.visit_control(config_handler_ts, redis_entity, visit_from) == False:
            self.set_status(429)
            self.write(mft.gen_message(0, "Too many requests."))
            self.finish()
            return

        # check ticket
        ticket = self.get_argument("ticket", None)
        if vctrl.check_ticket(
            redis_entity, visit_from, ticket
        ) == False and not vctrl.in_whitelist(config_handler_ts, visit_from):
            self.set_status(403)
            self.write(mft.gen_message(0, "Ticket expired."))
            self.finish()
            return

        # check file count and file size
        file_doc = self.request.files.get("file", [])
        if len(file_doc) != 1:
            self.set_status(403)
            self.write(mft.gen_message(0, "File forbidden."))
            self.finish()
            return

        file_doc = file_doc[0]

        if fctrl.check_file_size(config_handler_fs, file_doc["body"]) == False:
            self.set_status(403)
            self.write(mft.gen_message(0, "File size exceeded."))
            self.finish()
            return

        # check file keep time limit
        file_time_limit = self.get_argument(
            "keep", config_handler_fs.get("file_keep_time_limit", 604800)
        )
        try:
            file_time_limit = int(file_time_limit)
        except:
            file_time_limit = config_handler_fs.get("file_keep_time_limit", 604800)

        if fctrl.check_keep_time(config_handler_fs, file_time_limit) == False:
            self.set_status(403)
            self.write(mft.gen_message(0, "File keep time exceeded."))
            self.finish()
            return

        # check max downloads
        file_down_limit = self.get_argument(
            "download", config_handler_fs.get("file_download_count_limit", 32)
        )
        try:
            file_down_limit = int(file_down_limit)
        except:
            file_down_limit = config_handler_fs.get("file_download_count_limit", 32)
        if fctrl.check_max_download(config_handler_fs, file_down_limit) == False:
            self.set_status(403)
            self.write(mft.gen_message(0, "File download count exceeded."))
            self.finish()
            return

        # save logic
        storage_path_root = config_handler_fs.get(
            "file_sorage_path", Path("./upload").absolute()
        )
        file_ori_name = str(file_doc["filename"])
        file_hash_name = hash_generator.generate(
            file_ori_name + str(datetime.datetime.now().timestamp())
        )
        file_code = (
            datetime.datetime.now().strftime("%d")
            + hash_generator.generate(file_hash_name)[:6]
        )
        fctrl.register_file(
            redis_entity,
            file_ori_name,
            file_hash_name,
            file_code,
            file_down_limit,
            file_time_limit,
        )
        file_path = os.path.join(storage_path_root, file_hash_name + ".hashed")
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_doc["body"])
        self.set_status(200)
        self.write(
            mft.gen_message(
                200,
                "OK.",
                {
                    "file_code": file_code,
                    "expire": file_time_limit,
                    "count": file_down_limit,
                },
            )
        )
        self.finish()


class FileDownloadController(RequestHandler):
    async def post(self):
        visit_from = self.request.remote_ip
        if vctrl.visit_control(config_handler_ts, redis_entity, visit_from) == False:
            self.set_status(429)
            self.write(mft.gen_message(0, "Too many requests."))
            self.finish()
            return

        # check ticket
        ticket = self.get_argument("ticket", None)
        if vctrl.check_ticket(
            redis_entity, visit_from, ticket
        ) == False and not vctrl.in_whitelist(config_handler_ts, visit_from):
            self.set_status(403)
            self.write(mft.gen_message(0, "Ticket expired."))
            self.finish()
            return

        # get file code
        file_code = self.get_argument("code")
        if not fctrl.check_file_availability(redis_entity, file_code):
            self.set_status(404)
            self.write(mft.gen_message(0, "File not found."))
            self.finish()
            return

        storage_path_root = config_handler_fs.get(
            "file_sorage_path", Path("./upload").absolute()
        )
        filehash, filename = fctrl.get_file_info(redis_entity, file_code)
        file_path = os.path.join(storage_path_root, filehash + ".hashed")
        fsize = fmodified = None
        try:
            fsize = os.path.getsize(file_path)
            fmodified = time.ctime(os.path.getmtime(file_path))
        except:
            ...

        self.set_status(200)
        self.write(
            mft.gen_message(
                200,
                "OK.",
                {"file_name": url_escape(filename), "upload": fmodified, "size": fsize},
            )
        )
        self.finish()

    async def get(self):
        # record visit
        visit_from = self.request.remote_ip
        if vctrl.visit_control(config_handler_ts, redis_entity, visit_from) == False:
            self.set_status(429)
            self.write(mft.gen_message(0, "Too many requests."))
            self.finish()
            return

        # check ticket
        ticket = self.get_argument("ticket", None)
        if vctrl.check_ticket(
            redis_entity, visit_from, ticket
        ) == False and not vctrl.in_whitelist(config_handler_ts, visit_from):
            self.set_status(403)
            self.write(mft.gen_message(0, "Ticket expired."))
            self.finish()
            return

        # get file code
        file_code = self.get_argument("code")
        if not fctrl.check_file_availability(redis_entity, file_code):
            self.set_status(404)
            self.write(mft.gen_message(0, "File not found."))
            self.finish()
            return

        # get file detailed info
        storage_path_root = config_handler_fs.get(
            "file_sorage_path", Path("./upload").absolute()
        )
        filehash, filename = fctrl.get_file_info(redis_entity, file_code)
        file_path = os.path.join(storage_path_root, filehash + ".hashed")
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header(
            "Content-Disposition",
            f'attachment; filename="{url_escape(filename)}"'.encode(),
        )
        try:
            async with aiofiles.open(file_path, "rb") as f:
                while True:
                    c = await f.read()
                    if not c:
                        break
                    self.write(c)
            self.set_status(200)
            self.finish()
        except:
            self.set_status(500)
            self.finish(mft.gen_message(0, "File corrupted."))
        finally:
            fctrl.record_download(redis_entity, file_code, file_path)


def FileServer(config_ts, config_fs, general_config_handler):
    global config_handler_ts, config_handler_fs, redis_entity, hash_generator
    config_handler_ts = config_ts
    config_handler_fs = config_fs

    redis_entity = RedisUtils(
        general_config_handler.get("redis_host", "localhost"),
        general_config_handler.get("redis_port", 6379),
        general_config_handler.get("redis_usr", None),
        general_config_handler.get("redis_pwd", None),
        config_handler_fs.get("db", 0),
    )
    hash_generator = CodeGenerator()
    redis_entity.connect()

    app = Application(
        handlers=[
            (
                config_handler_ts.get("api_file_upload", "/file/upload"),
                FileUploadController,
            ),
            (
                config_handler_ts.get("api_file_download", "/file/download"),
                FileDownloadController,
            ),
            # (
            #     config_handler_ts.get("api_file_manage", "/file/manage"),
            #     FileManageController,
            # ),
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    return http_server
