wsgi_app = "hackackathon.wsgi"

daemon = True
pidfile = "gunicorn.pid"

workers = 2
threads = 2

bind = "127.0.0.1:8000"

accesslog = "log/gunicorn-access.log"


def when_ready(server):
    print("Gunicorn listo")


def on_exit(server):
    print("Gunicorn apagado")
