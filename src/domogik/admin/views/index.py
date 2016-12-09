from domogik.admin.application import app, render_template
from domogikmq.configloader import Loader as mqLoader
from domogik.common.configloader import Loader as dmgLoader
from domogik.common.utils import get_ip_for_interfaces, ucode
from flask import request
from flask_login import login_required

@app.route('/')
@login_required
def index():
    mqConfig = mqLoader('mq').load()[0]
    butlerConfig = dict(dmgLoader('butler').load()[1])

    qrCode = dict()
    qrCode["admin_url"] = str(request.url)
    qrCode["rest_port"] = int(app.port)
    qrCode["rest_path"] = "/rest"
    qrCode["rest_auth"] = bool(app.rest_auth)
    qrCode["mq_ip"] = str(mqConfig['ip'])
    qrCode["mq_port_pubsub"] = int( mqConfig['sub_port'])
    qrCode["mq_port_req_rep"] = int(mqConfig['req_rep_port'])
    qrCode["butler_name"] = ucode(butlerConfig['name'])
    qrCode["butler_sex"] = str(butlerConfig['sex'])
    qrCode["butler_lang"] = str(butlerConfig['lang'])
    return render_template('index.html',
            qrdata=qrCode)
