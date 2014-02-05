#!/usr/bin/env python

import os, sys, datetime, subprocess
try:
    from flask import Blueprint, request
except:
    sys.stderr.write('Flask module is not avaliable\n')
    sys.exit(1)

def get_conf(name):
    config = {'feed_type':'SMS', 'feed_con':'Gammu', 'time_delay':1800}
    config['send_script_path'] = '/opt/gammu/bin/send_sms'
    config['send_config_path'] = '/opt/gammu/etc/gammu/send_sms.conf'
    if name in config:
        return config[name]
    return None

def within_session(last_received, current_received):
    if not last_received:
        return False
    if not current_received:
        return False

    try:
        if type(last_received) is not datetime.datetime:
            dt_format = '%Y-%m-%dT%H:%M:%S'
            if '.' in last_received:
                dt_format = '%Y-%m-%dT%H:%M:%S.%f'
            last_received = datetime.datetime.strptime(last_received, dt_format)
    except:
        return False

    try:
        if type(current_received) is not datetime.datetime:
            dt_format = '%Y-%m-%dT%H:%M:%S'
            if '.' in current_received:
                dt_format = '%Y-%m-%dT%H:%M:%S.%f'
            current_received = datetime.datetime.strptime(current_received, dt_format)
    except:
        return False

    time_diff = current_received - last_received
    if time_diff.seconds <= get_conf('time_delay'):
        return True

    return False

def ask_sender(phone_number):
    message = 'Dear citizen, could you tell us you geolocation, please?'
    send_script = get_conf('send_script_path')
    send_config = get_conf('send_config_path')
    try:
        subprocess.call([send_script, send_config, phone_number, message])
    except:
        pass

sms_take = Blueprint('sms_take', __name__)

@sms_take.route('/sms_feeds/', methods=['GET', 'POST'])
def take_sms():
    '''
    sys.stderr.write(str(request.form) + '\n\n')
    save_list = []
    for part in ['feed', 'phone', 'time', 'text']:
        if part in request.form:
            save_list += [part + ': ' + str(request.form[part].encode('utf8'))]
    save_str = ', '.join(save_list) + '\n'
    sf = open('/tmp/cd.debug.001', 'a')
    sf.write(save_str)
    sf.close()
    '''
    db = None
    params = {}

    if not params['text']:
        return 'no SMS message text provided'

    feed_name = params['feed']
    phone_number = params['phone']

    feed_type = get_conf('feed_type')
    #feed_conn = get_conf('feed_conn')
    received = params[time]
    if not received:
        received = datetime.datetime.now()

    channels = [{'type':'SMS', 'value':feed_name}]
    publishers = []
    authors = [{'type':'phone', 'value':phone_number}]
    endorsers = []

    original = params[text]
    texts = [params[text]]
    tags = []
    if params[text]:
        for word in params[text].split(' '):
            if word.startswith('#'):
                use_tag = word[1:]
                if use_tag:
                    tags.append(use_tag)

    session = '' + params['phone'] + ':' + received
    new_session = True

    last_report = db.find_last_report({'channels':channels[0], 'authors':authors[0]})
    if last_report:
        if within_session(last_report['received'], received):
            session = last_report['session']
            new_session = False

    report = {}
    report['feed_type'] = feed_type
    report['received'] = received
    report['session'] = session
    report['session_quit'] = False
    report['channels'] = channels
    report['authors'] = authors
    report['original'] = original
    report['texts'] = texts
    report['tags'] = tags

    db.save_report(report)

    if new_session:
        ask_sender()

    return 'SMS received\n\n'

