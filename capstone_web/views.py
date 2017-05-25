# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import json
import time
from PIL import Image
import settings
import os, sys

from common import utils
from caae.FaceAging import FaceAging

import tensorflow as tf
import pprint

flags = tf.app.flags
flags.DEFINE_integer(flag_name='epoch', default_value=50, docstring='number of epochs')
flags.DEFINE_boolean(flag_name='is_train', default_value=False, docstring='training mode')
flags.DEFINE_string(flag_name='dataset', default_value='UTKFace', docstring='dataset name')
flags.DEFINE_string(flag_name='savedir', default_value='/static/outputs', docstring='dir for saving training results')
flags.DEFINE_string(flag_name='testdir', default_value='200200', docstring='dir for testing images')
FLAGS = flags.FLAGS


def home(request, page="", arg1="", arg2=""):
    try:
        info={}
        return render(request, 'capstone.html', info)

            
    except:
        error_message = utils.string_trace_debug()
        utils.log_error(error_message)
    return render(request, "default/page_error.html", {"error":error_message, "time":time.strftime("%Y/%m/%d %H:%M:%S")})


@csrf_exempt
def upload_img(request):
    # try:
        gender = int(request.POST.get("gender", "0"))
        age = int(request.POST.get("age", "0"))
        UPLOAD_DIR = os.path.join(settings.PROJECT_PATH, "static/inputs")
        if not os.path.exists(UPLOAD_DIR):
            os.mkdir(UPLOAD_DIR)

        ret = {"ret": True}
        if 'upfile' in request.FILES:
            file = request.FILES['upfile']
            file_name = time.strftime("%Y%m%d%H%M%S")
            file_path = os.path.join(UPLOAD_DIR, file_name)

            fp = open(file_path, 'w')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()


            if ".png" in file.name:
                im = Image.open(file_path)
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, im)
                bg = bg.resize((200, 200), Image.ANTIALIAS)
                bg.save(file_path+".jpg", quality=70)
                os.remove(file_path)
            else :
                os.rename(file_path, file_path+".jpg")

                im = Image.open(file_path+".jpg")
                im = im.resize((200, 200), Image.ANTIALIAS)
                im.save(file_path+".jpg", quality=70)


            file_path = file_path+".jpg"


            outfile = make_image(file_path, age, gender)
            # face.make_output(file_path,age,gender)

            ret = {"ret": True, "outfile": outfile}
        else:
            ret = {"ret": False, "msg": "파일을 업로드 해주세요."}

        return HttpResponse(json.dumps(ret))
    # except:
    #     error_message = utils.string_trace_debug()
    #     utils.log_error(error_message)
    #     return {"ret": False, 'msg': error_message}



def make_image(file_path, age, gender) :

    pprint.pprint(FLAGS.__flags)

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    with tf.Session(config=config) as session:
        model = FaceAging(
            session,  # TensorFlow session
            is_training=FLAGS.is_train,  # flag for training or testing mode
            save_dir=FLAGS.savedir,  # path to save checkpoints, samples, and summary
            dataset_name=FLAGS.dataset  # name of the dataset in the folder ./data
        )
        print('\n\tTesting Mode')
        checkpoint_dir = os.path.join(settings.PROJECT_PATH, "caae/save/checkpoint")
        output_path = os.path.join(settings.PROJECT_PATH, "static/outputs")

        file_name_10_10 = time.strftime("%Y%m%d%H%M%S") + ".png"
        model.make_output(file_path,age,gender,checkpoint_dir, output_path, file_name_10_10)



        file_name = time.strftime("%Y%m%d%H%M%S")+".png"
        img = Image.open(os.path.join(output_path,file_name_10_10))
        # 1*10
        # img2 = img.crop((0, 0, 128, 1280))
        #1*1
        img2 = img.crop((0, age * 128, 128, age * 128+128))
        img2.save(os.path.join(output_path,file_name))
        return "/static/outputs/"+file_name

def page_alive(request):
    return HttpResponse("alive")
