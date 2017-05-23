# -*- coding:utf-8 -*-
from django.conf import settings
from django.http import HttpResponse
from datetime import date
import datetime

import json
import zlib
import base64
import time
import sys
import traceback
import re
import urllib
import urllib2
import smtplib
import hashlib
import zipfile
import os.path

def string_trace_debug():
    exc_type, exc_value, exc_tb = sys.exc_info()
    return str(traceback.format_exception(exc_type, exc_value, exc_tb))  


def response_trace_debug():
    exc_type, exc_value, exc_tb = sys.exc_info()
    return HttpResponse(traceback.format_exception(exc_type, exc_value, exc_tb))


def log_trace_debug():
    message = string_trace_debug()
    log_error(message)
    return HttpResponse(message)


def log_error(message):
    print message

def now(format='%Y%m%d%H%M%S'):
    return time.strftime(format)

def encode_utf8(val):
    if val == None:
        return ""
    try:
        ret = val.encode('utf-8').strip()
    except:
        try:
            ret = str(val).strip()
        except:
            ret = val.strip()
    return ret

def md5uidx(useridx):
    return hashlib.md5(str(useridx)).digest()

def md5(value):
    return hashlib.md5(str(value)).hexdigest()

def shaPwd(pwd):
    return hashlib.sha512(hashlib.sha1(pwd).hexdigest()).hexdigest()
    
def req_rest_api_with_url(url, values=None):
    #values : {} map
    if values != None and len(values) > 0:
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
    else:
        req = urllib2.Request(url)
    rsp = urllib2.urlopen(req)
    value = rsp.read()
    return json.loads(value)


def unzip_only_file(path):
    zfile = zipfile.ZipFile(path)
    (root, zipname) = os.path.split(path)
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        if filename != '':
            filepath = '%s/%s' % (root, filename.decode('utf-8'))
            fd = open(filepath, 'w')
            fd.write(zfile.read(name))
            fd.close()
    zfile.close()  
    

def unzip(path):
    zfile = zipfile.ZipFile(path)
    (root, zipname) = os.path.split(path)
    print root, zipname
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        if filename == '':
            # directory
            dir = os.path.join(root, dirname)
            if not os.path.exists(dir):
                os.mkdir(dir)
        else:
            # file
            filename = '%s/%s' % (root, name.decode('utf-8'))
            fd = open(filename, 'w')
            fd.write(zfile.read(name))
            fd.close()
    zfile.close()        

 
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def has_authority(allowed_auths, users_auths):
    if allowed_auths == None or len(allowed_auths) == 0:
        return True
    for t in allowed_auths:
        if t in users_auths:
            return True
    return False

def timestring_with_timegap(timestring, gap_sec, key_time_format):
    ts = time.mktime(datetime.datetime.strptime(timestring, key_time_format).timetuple()) + gap_sec
    return datetime.datetime.fromtimestamp(float(ts)).strftime(key_time_format)


#패킷전송은 최소한의 암호화를 위해 아래 방법으로 encoding해서 보낸다 
def get_value(request):
    post = None
    try:
        if request.method == "POST":
            data = base64.b64decode(request.POST['n'][::-1])
            post = json.loads(zlib.decompress(data))
        else:
            post = request.GET
    except:
        return None
    return post

def encoderesult(res):
    jsonstring = json.dumps(res)
    com = zlib.compress(jsonstring)
    return com[::-1]

def return_result(request, res):
    if request.method == "GET":
        return HttpResponse(json.dumps(res))
    return HttpResponse(encoderesult(res))

#타로 cms페이지의 권한을 비트로 돌려준다. 
def author2bit(membertype):
#         membertype = [u'dv', u'op', u'cp', ]
    ret = 0
    if 'dv' in membertype:
        ret |= 1
    if 'op' in membertype:
        ret |= 2
    if 'cp' in membertype:
        ret |= 4
    return str(ret)

def bit2author(bit):
    ret = []
    bit = int(bit)
    if (bit & 4) != 0:
        ret.append('cp')
    if (bit & 2) != 0:
        ret.append('op')
    if (bit & 1) != 0:
        ret.append('dv')
    return ret

