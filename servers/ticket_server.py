if __name__ == "__main__":
    print("this module shall be run under the main.py container")
    exit(0)


from tornado.web import RequestHandler, Application
import tornado.httpserver
import datetime

from data.db import RedisUtils
import core.visit_ctrl as vctrl
import core.msg_format as mft
from data.codegen import CodeGenerator


config_handler_ts = None
redis_entity = None
ticket_generator = None


class TicketProvidingController(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def post(self):
        visit_from = self.request.remote_ip
        if vctrl.visit_control(config_handler_ts, redis_entity, visit_from) == False:
            self.set_status(429)
            self.write(mft.gen_message(0, "Too many requests."))
            self.finish()
            return

        pk = self.get_argument("pk", str(datetime.datetime.now().timestamp()))
        ticket = ticket_generator.generate(f"{visit_from}+{pk}")
        vctrl.add_ticket(
            redis_entity,
            visit_from,
            ticket,
            config_handler_ts.get("ticket_expire_secs", 3600),
        )
        self.set_status(200)
        self.write(mft.gen_message(200, "OK", ticket))
        self.finish()

    def get(self):
        visit_from = self.request.remote_ip
        if vctrl.visit_control(config_handler_ts, redis_entity, visit_from) == False:
            self.set_status(429)
            self.write(mft.gen_message(0, "Too many requests."))
            self.finish()
            return

        ticket = self.get_argument("ticket")
        ret = vctrl.check_ticket(redis_entity, visit_from, ticket)
        self.set_status(200)
        self.write(mft.gen_message(200, "OK.", ret))
        self.finish()


class TicketDestoryController(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def post(self):
        visit_from = self.request.remote_ip
        if vctrl.visit_control(config_handler_ts, redis_entity, visit_from) == False:
            self.set_status(429)
            self.write(mft.gen_message(0, "Too many requests."))
            self.finish()
            return

        ticket = self.get_argument("ticket")

        ret = vctrl.check_ticket(redis_entity, visit_from, ticket)
        if ret == False:
            if vctrl.in_whitelist(config_handler_ts, visit_from):
                vctrl.withdraw_ticket(redis_entity, visit_from)
                self.set_status(200)
                self.write(
                    mft.gen_message(200, "Successfully destoried target ticket.")
                )
            else:
                self.set_status(403)
                self.write(mft.gen_message(403, "Destory failed."))
        else:
            vctrl.withdraw_ticket(redis_entity, visit_from)
            self.set_status(200)
            self.write(mft.gen_message(200, "Successfully destoried target ticket."))
        self.finish()


class TicketManageController(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def get(self):
        visit_from = self.request.remote_ip

        cursor_ti = self.get_argument("cur_ti", 0)
        cursor_rc = self.get_argument("cur_rc", 0)
        cursor_pe = self.get_argument("cur_pe", 0)

        cnt = config_handler_ts.get("list_show_count", 32)
        if not vctrl.in_whitelist(config_handler_ts, visit_from):
            self.set_status(403)
            self.write(mft.gen_message(403, "Fetch failed."))
            self.finish()
            return

        next_cur_ti, ret_ti = redis_entity.execute_cmd(
            f"scan {cursor_ti} match ts:ti:* count {cnt}"
        )
        ret_ti = [
            [
                item.decode()[6:],
                redis_entity.get(item.decode()).decode(),
                redis_entity.db_instance.ttl(item.decode()),
            ]
            for item in ret_ti
        ]

        next_cur_rc, ret_rc = redis_entity.execute_cmd(
            f"scan {cursor_rc} match ts:rc:* count {cnt}"
        )
        ret_rc = [
            [
                item.decode()[6:],
                redis_entity.get(item.decode()).decode(),
                redis_entity.db_instance.ttl(item.decode()),
            ]
            for item in ret_rc
        ]

        next_cur_pe, ret_pe = redis_entity.execute_cmd(
            f"scan {cursor_pe} match ts:pe:* count {cnt}"
        )
        ret_pe = [
            [
                item.decode()[6:],
                redis_entity.get(item.decode()).decode(),
                redis_entity.db_instance.ttl(item.decode()),
            ]
            for item in ret_pe
        ]

        data = {
            "tickets": ret_ti,
            "tickets_next_cur": int(next_cur_ti),
            "request_counts": ret_rc,
            "request_next_cur": int(next_cur_rc),
            "peasants": ret_pe,
            "peasants_next_cur": int(next_cur_pe),
        }
        self.write(mft.gen_message(200, "OK.", data))
        self.finish()

    def post(self):
        visit_from = self.request.remote_ip
        if not vctrl.in_whitelist(config_handler_ts, visit_from):
            self.set_status(403)
            self.write(mft.gen_message(403, "Operation failed."))
            self.finish()
            return

        op_type = self.get_argument("op_type", -1)
        try:
            op_type = int(op_type)
        except:
            op_type = -1

        op_target = self.get_argument("op_target", None)
        op_val = self.get_argument(
            "op_val", config_handler_ts.get("ticket_expire_secs", 3600)
        )
        try:
            op_val = int(op_val)
        except:
            op_val = 3600

        if op_type == -1 or op_target is None:
            self.write(mft.gen_message(200, "Test OK."))
            self.finish()
            return

        if op_type == 0:  # add/modify ticket
            if op_val is not None:
                pk = str(datetime.datetime.now().timestamp())
                ticket = ticket_generator.generate(f"{visit_from}+{pk}")
                vctrl.add_ticket(redis_entity, op_target, ticket, op_val)
        elif op_type == 1:  # delete ticket
            vctrl.withdraw_ticket(redis_entity, op_target)
        elif op_type == 2:  # add/modify peasant
            vctrl.add_ip_peasant(redis_entity, op_target, op_val)
        elif op_type == 3:  # delete peasant
            redis_entity.delete(vctrl.gen_peasant_str(op_target))
        elif op_type == 4:  # reset request count
            redis_entity.delete(vctrl.gen_req_cnt_str(op_target))
        elif op_type == 5:  # add/modify request count
            redis_entity.set(
                vctrl.gen_req_cnt_str(op_target),
                int(op_val),
                config_handler_ts.get("vc_pe_expire_secs", 60),
            )
        self.write(mft.gen_message(200, "OK."))
        self.finish()


def TicketServer(config_handler, general_config_handler):
    global config_handler_ts, redis_entity, ticket_generator
    config_handler_ts = config_handler
    redis_entity = RedisUtils(
        general_config_handler.get("redis_host", "localhost"),
        general_config_handler.get("redis_port", 6379),
        general_config_handler.get("redis_usr", None),
        general_config_handler.get("redis_pwd", None),
        config_handler_ts.get("db", 0),
    )
    ticket_generator = CodeGenerator()
    redis_entity.connect()

    app = Application(
        handlers=[
            (
                config_handler_ts.get("api_ticket_provide", "/api/ticket/get"),
                TicketProvidingController,
            ),
            (
                config_handler_ts.get("api_ticket_destory", "/api/ticket/destory"),
                TicketDestoryController,
            ),
            (
                config_handler_ts.get("api_ticket_manage", "/api/ticket/manage"),
                TicketManageController,
            ),
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    return http_server
