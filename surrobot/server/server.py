from tornado import (ioloop, web)
import simplejson as json

from surrobot.core.autoreply import query_by_body

def TemplateRenderHandler(template):
    class UploadHandler(web.RequestHandler):
        def get(self):
            self.render(template)
    return UploadHandler


class AutoreplyHandler(web.RequestHandler):
    def post(self):
        in_mail = json.loads(self.get_argument('mail_body'))
        print '[incoming mail]', in_mail
        try:
            top_k = int(self.get_argument('top_k'))
        except:
            top_k = 5
        replies = query_by_body(in_mail, top_k=5)
        self.write(json.dumps(replies))


handlers = [
    (r"/(.*\.jpg)", web.StaticFileHandler, {"path": "images/"}),
    (r"/(.*\.png)", web.StaticFileHandler, {"path": "images/"}),
    (r"/(.*\.css)", web.StaticFileHandler, {"path": "css/"}),
    (r"/(.*\.js)", web.StaticFileHandler, {"path": "js/"}),
    (r"/", TemplateRenderHandler('demo.html')),
    (r"/autoreply", AutoreplyHandler),
]

settings = {
    "autoreload": True,
    "debug": True,
    "template_path": "surrobot/server/template"
}

if __name__ == "__main__":
    application = web.Application(handlers, **settings)
    application.listen(8889, address="0.0.0.0")
    ioloop.IOLoop.current().start()


