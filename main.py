import tornado

from data.config import ConfigHandler
import core.msg_format as mft
import servers.ticket_server as ticket_server
import servers.file_server as file_server

if __name__ == "__main__":
    general_config_handler = ConfigHandler(
        "./server_config.json", "general", mft.default_config
    )
    ts_config_handler = ConfigHandler(
        "./server_config.json", "ticket_server", mft.default_config
    )
    fs_config_handler = ConfigHandler(
        "./server_config.json", "file_server", mft.default_config
    )
    http_server_t = ticket_server.TicketServer(
        ts_config_handler, general_config_handler
    )
    http_server_f = file_server.FileServer(
        ts_config_handler, fs_config_handler, general_config_handler
    )

    tornado.options.parse_command_line()

    http_server_t.listen(ts_config_handler.get('listen_port', 9001))
    http_server_f.listen(fs_config_handler.get('listen_port', 9002))
    instance = tornado.ioloop.IOLoop.instance()
    instance.start()
