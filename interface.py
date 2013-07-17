from flask import Flask, render_template, request, Markup
from memcache import Client
from pyga.requests import Tracker, Page, Session, Visitor
tracker = Tracker('MO-42545376-1', '213.239.193.15:2222')

import cleverbot

client = Client(['localhost:11211'], debug=True)
app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    # Users identity
    user_id = request.headers.get('X-Mxit-USERID-R', 'dev').encode('utf-8')
    user_nick = request.form.get('X-Mxit-ID-R', 'avoid3d')

    visitor = Visitor()
    visitor.ip_address = request.headers.get('X-Forwarded-For', '127.0.0.1')
    ga_session = Session()

    # User's msg to cleverbot
    text = request.args.get('input', None)

    msgs = ['Welcome to chatterbot! Say Hello?']
    page = Page('/')

    if text:
        page = Page('/chat/')
        # Attempt to fetch a session for the user.
        session = client.get(user_id)
        if not session:
            session = cleverbot.Session()
            session.msgs = []

        session.msgs.append('%s: %s' % (user_nick, text))
        reply = session.Ask(text)
        session.msgs.append('bot: %s' % reply)

        client.set(user_id, session)
        msgs = session.msgs[-10:]

    tracker.track_pageview(page, ga_session, visitor)
    return render_template('index.html', msgs=msgs, Markup=Markup)

app.run(host='0.0.0.0', port=2222)
