# usage: python driving_models.py 1 0 - train the dave-orig model
from __future__ import print_function

import csv
import shutil
import sys
import os

sys.path.append("..")
from data_utils import *
import pandas as pd
# add tensorflow.
from tensorflow.keras.layers import Convolution2D, Input, Dense, Flatten, Lambda, MaxPooling2D, Dropout, Activation, \
    SpatialDropout2D
    # remove merge
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras import models, optimizers, backend

import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import time


def Dave_orig(input_tensor=None, load_weights=False):  # original dave
    if input_tensor is None:
        input_tensor = Input(shape=(100, 100, 3))
    x = Convolution2D(24, (5, 5), padding='valid', activation='relu', strides=(2, 2), name='block1_conv1')(input_tensor)
    x = Convolution2D(36, (5, 5), padding='valid', activation='relu', strides=(2, 2), name='block1_conv2')(x)
    x = Convolution2D(48, (5, 5), padding='valid', activation='relu', strides=(2, 2), name='block1_conv3')(x)
    x = Convolution2D(64, (3, 3), padding='valid', activation='relu', strides=(1, 1), name='block1_conv4')(x)
    x = Convolution2D(64, (3, 3), padding='valid', activation='relu', strides=(1, 1), name='block1_conv5')(x)
    x = Flatten(name='flatten')(x)
    x = Dense(1164, activation='relu', name='fc1')(x)
    x = Dense(100, activation='relu', name='fc2')(x)
    x = Dense(50, activation='relu', name='fc3')(x)
    x = Dense(10, activation='relu', name='fc4')(x)
    x = Dense(1, name='before_prediction')(x)
    x = Lambda(atan_layer, output_shape=atan_layer_shape, name='prediction')(x)

    m = Model(input_tensor, x)
    if load_weights:
        m.load_weights('../trained_models/Model1.h5')

    # compiling
    m.compile(loss='mse', optimizer='Adam')
    # m.compile(loss=[rmse], optimizer='adadelta')

    return m


def Dave_norminit(input_tensor=None, load_weights=False):  # original dave with normal initialization
    if input_tensor is None:
        input_tensor = Input(shape=(100, 100, 3))
    x = Convolution2D(24, (5, 5), padding='valid', activation='relu', strides=(2, 2),
                      name='block1_conv1')(input_tensor)
    x = Convolution2D(36, (5, 5), padding='valid', activation='relu', strides=(2, 2),
                      name='block1_conv2')(x)
    x = Convolution2D(48, (5, 5), padding='valid', activation='relu', strides=(2, 2),
                      name='block1_conv3')(x)
    x = Convolution2D(64, (3, 3), padding='valid', activation='relu', strides=(1, 1),
                      name='block1_conv4')(x)
    x = Convolution2D(64, (3, 3), padding='valid', activation='relu', strides=(1, 1),
                      name='block1_conv5')(x)
    x = Flatten(name='flatten')(x)
    x = Dense(1164, kernel_initializer=normal_init, activation='relu', name='fc1')(x)
    x = Dense(100, kernel_initializer=normal_init, activation='relu', name='fc2')(x)
    x = Dense(50, kernel_initializer=normal_init, activation='relu', name='fc3')(x)
    x = Dense(10, kernel_initializer=normal_init, activation='relu', name='fc4')(x)
    x = Dense(1, name='before_prediction')(x)
    x = Lambda(atan_layer, output_shape=atan_layer_shape, name='prediction')(x)

    m = Model(input_tensor, x)
    if load_weights:
        m.load_weights('../trained_models/Model2.h5')

    # compiling
    m.compile(loss='mse', optimizer='Adam')
    # m.compile(loss=[rmse], optimizer='adadelta')
    return m


def Dave_dropout(input_tensor=None, load_weights=False):  # simplified dave
    if input_tensor is None:
        input_tensor = Input(shape=(100, 100, 3))
    x = Convolution2D(16, (3, 3), padding='valid', activation='relu', name='block1_conv1')(input_tensor)
    x = MaxPooling2D(pool_size=(2, 2), name='block1_pool1')(x)
    x = Convolution2D(32, (3, 3), padding='valid', activation='relu', name='block1_conv2')(x)
    x = MaxPooling2D(pool_size=(2, 2), name='block1_pool2')(x)
    x = Convolution2D(64, (3, 3), padding='valid', activation='relu', name='block1_conv3')(x)
    x = MaxPooling2D(pool_size=(2, 2), name='block1_pool3')(x)
    x = Flatten(name='flatten')(x)
    x = Dense(500, activation='relu', name='fc1')(x)
    x = Dropout(.5)(x)
    x = Dense(100, activation='relu', name='fc2')(x)
    x = Dropout(.25)(x)
    x = Dense(20, activation='relu', name='fc3')(x)
    x = Dense(1, name='before_prediction')(x)
    x = Lambda(atan_layer, output_shape=atan_layer_shape, name="prediction")(x)

    m = Model(input_tensor, x)
    if load_weights:
        m.load_weights('../trained_models/Model3.h5')

    # compiling
    m.compile(loss='mse', optimizer=optimizers.Adam(lr=1e-04))
    # m.compile(loss=[rmse], optimizer='adadelta')
    return m


def Epoch_model(input_tensor=None, load_weights=False):
    if input_tensor is None:
        input_tensor = Input(shape=(128, 128, 3))

    x = Convolution2D(32, (3, 3), activation='relu', padding='same')(input_tensor)
    x = MaxPooling2D((2, 2), strides=(2, 2))(x)
    x = Dropout(0.25)(x)

    x = Convolution2D(64, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2))(x)
    x = Dropout(0.25)(x)

    x = Convolution2D(128, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), strides=(2, 2))(x)
    x = Dropout(0.5)(x)

    y = Flatten()(x)
    y = Dense(1024, activation='relu')(y)
    y = Dropout(.5)(y)
    y = Dense(1)(y)

    m = Model(input_tensor, y)
    if load_weights:
        m.load_weights('../trained_models/Model4.h5')

    # compliling
    m.compile(loss='mse', optimizer=optimizers.Adam(lr=1e-04))
    # m.compile(loss=[rmse], optimizer='adadelta')

    return m


def rmse(y_true, y_pred):  # used for loss metric, output tensor
    '''Calculates RMSE
    '''
    return K.sqrt(K.mean(K.square(y_pred - y_true)))


def calc_rmse(yhat, label):  # used for loss cal, output float
    mse = 0.
    count = 0
    if len(yhat) != len(label):
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "yhat and label have different lengths")
        return -1
    for i in range(len(yhat)):
        count += 1
        predicted_steering = yhat[i]
        steering = label[i]
        # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", predicted_steering)
        # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", steering)
        mse += (float(steering) - float(predicted_steering)) ** 2.
    return (mse / count) ** 0.5


def calc_mse(yhat, label):  # used for loss cal, output float
    mse = 0.
    count = 0
    if len(yhat) != len(label):
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "yhat and label have different lengths")
        return -1
    for i in range(len(yhat)):
        count += 1
        predicted_steering = yhat[i]
        steering = label[i]
        # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", predicted_steering)
        # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", steering)
        mse += (float(steering) - float(predicted_steering)) ** 2.
    return (mse / count)


def error_test():
    # Train variables define & Input variables parse
    # TODO

    batch_size = 64
    nb_epoch = 30
    image_shape = (100, 100)
    model_name = sys.argv[1]
    model_existed = sys.argv[2]
    seed_name = sys.argv[3]
    seed_str = seed_name.split("_")[3]
    seed_number = int(seed_str[0])
    data_collection_para = sys.argv[4].strip().split(
        ',')  # data_collection_para : [is_new_seed(for entropy), is_err_collection(collect err or not), err_type(collect normal(1)/sampling(2)/random data(3))]
    is_err_collection = data_collection_para[1]
    err_type = data_collection_para[2]

    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", seed_number, seed_number, seed_number)
    dataset_path = '../train_carla/'
    test_dataset_path = '../scenario_runner-0.9.13/_out/'
    with open(test_dataset_path + 'label_test.csv', 'r') as f:
        rows = len(f.readlines()) - 1
        if rows == 0:
            return 0

    # --------------------------------------Build Model---------------------------------------- #
    # Dave_v1
    if model_name == '1':
        if model_existed == '0':
            model = Dave_orig()
        else:
            model = Dave_orig(None, True)
        save_model_name = '../trained_models/Model1.h5'

    # Dave_v2
    elif model_name == '2':
        # K.set_learning_phase(1)
        if model_existed == '0':
            model = Dave_norminit()
        else:
            model = Dave_norminit(None, True)
        save_model_name = '../trained_models/Model2.h5'
        # batch_size = 64 # 1 2 3 4 5 6x
        nb_epoch = 30

    # Dave_v3
    elif model_name == '3':
        # K.set_learning_phase(1)
        if model_existed == '0':
            model = Dave_dropout()
        else:
            model = Dave_dropout(None, True)
        save_model_name = '../trained_models/Model3.h5'
        # nb_epoch = 30

    # Udacity Epoch Model
    elif model_name == '4':
        if model_existed == '0':
            model = Epoch_model()
        else:
            model = Epoch_model(None, True)
        save_model_name = '../trained_models/Model4.h5'
        image_shape = (128, 128)
        nb_epoch = 30
        batch_size = 32
    else:
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", bcolors.FAIL + 'invalid model name, must in [1, 2, 3, 4]' + bcolors.ENDC)

    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", bcolors.OKGREEN + 'model %s built' % model_name + bcolors.ENDC)


    # --------------------------------------Evaluation---------------------------------------- #
    # Different evaluation methods for different model
    if model_name != '4':
        K.set_learning_phase(0)
        test_generator, samples_per_epoch = load_carla_test_data(path=test_dataset_path, batch_size=batch_size,
                                                                 shape=image_shape)
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", 'test samples: ', samples_per_epoch)
        loss = model.evaluate(test_generator, steps=math.ceil(samples_per_epoch * 1. / batch_size), verbose=1)
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "model %s evaluate_generator loss: %.8f" % (model_name, loss))
        # --------------------------------------Predict Dave---------------------------------------- #
        filelist = []
        true_angle_list = []

        with open(test_dataset_path + 'label_test.csv', 'r') as f:
            rows = len(f.readlines()) - 1
            f.seek(0)
            for i, line in enumerate(f):
                if i == 0:
                    continue
                file_name = line.split(',')[0]
                # TODO BEGIN
                # if i > int(rows * 0.75):
                filelist.append(test_dataset_path + 'center/' + file_name)
                true_angle_list.append(float(line.split(',')[2]))
                # TODO END

        # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", 'filelist length: ', len(filelist))
        # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", 'true_angle_list', true_angle_list)

        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------IMG READ-------")
        predict_angle_list = []
        imgs = []
        raw_imgs = []
        count = 0
        ori_image_size = (720, 1280)
        for f in filelist:
            count += 1
            if (count % 100 == 0):
                print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", str(count) + ' images read')
            orig_name = f
            gen_img = preprocess_image(orig_name, image_shape)
            raw_img = preprocess_image(orig_name, ori_image_size)
            imgs.append(gen_img)
            raw_imgs.append(raw_img)
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------IMG READ COMPLETE-------")

        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------DAVE PREDICT-------")
        count = 0
        imgs = np.array(imgs)
        for i in range(len(imgs)):
            predict_angle_list.append(model.predict(imgs[i])[0])
            # TODO: Add arrows to raw images and save
            # gen_img_deprocessed = draw_arrow3(deprocess_image(raw_imgs[i], (720, 1280, 3)), -true_angle_list[i], -predict_angle_list[-1])
            # imsave('./test_output_carla/' + str(i) + 'th_img.png', gen_img_deprocessed)
            # count += 1
            # if (count % 20 == 0):
            #     print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", str(count) + ' images saved')
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------DAVE PREDICT COMPLETE-------")
        yhat = predict_angle_list
        test_y = true_angle_list


    else:
        # label data read
        test_steering_log = path.join(test_dataset_path, 'label_test.csv')
        test_data = carla_load_steering_data(test_steering_log)
        test_frame_id = carla_load_frame_id(test_data)
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", 'testset frame_id len: ', len(test_frame_id))

        # dataset divide
        time_list_test = []
        for j in range(0, len(test_frame_id)):
            time_list_test.append(test_frame_id[j])

        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", 'time_list_test len: ', len(time_list_test))
        test_generator = carla_data_generator(frame_id=test_frame_id,
                                              steering_log=test_steering_log,
                                              image_folder=test_dataset_path,
                                              unique_list=time_list_test,
                                              gen_type='test',
                                              batch_size=len(time_list_test),
                                              image_size=image_shape,
                                              shuffle=False,
                                              preprocess_input=normalize_input,
                                              preprocess_output=exact_output)

        # --------------------------------------Predict Epoch---------------------------------------- #
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------EPOCH PREDICT-------")
        test_x, test_y = next(test_generator)
        yhat = model.predict(test_x)
        print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------EPOCH PREDICT COMPLETE-------")
    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", yhat)
    loss = calc_mse(yhat, test_y)
    # --------------------------------------FIND ERROR---------------------------------------- #
    filelist_list = []
    list_row = []
    with open(test_dataset_path + 'label_test.csv', 'r') as f:
        rows = len(f.readlines()) - 1
        f.seek(0)
        for i, line in enumerate(f):
            if i == 0:
                continue
            file_name = line.split(',')[0]
            filelist_list.append(file_name)

    df = pd.read_csv(test_dataset_path + 'label_test.csv')
    df.head(2)
    df = df.drop(df.index[0:250])
    df.to_csv(test_dataset_path + 'label_test.csv', index=False, sep=',', encoding="utf-8")

    # path = '../scenario_runner-0.9.13/_out/'
    # shutil.rmtree(path + 'center')  # 清空out
    # os.mkdir(path + 'center')  

    a = np.loadtxt("diversity.txt")
    iterate = int(seed_name.split("_")[1])
    lamb = 1
    countcc = 0
    divadd = 0
    error_list = []
    lenm = len(filelist_list)

    # for i in range(6):
    #      for j in range(125):
    #         if a[i,j]==1:
    #             divadd=divadd+1

    with open(test_dataset_path + 'model' + model_name + '_oriMSE.csv', 'r') as f:
        rows = len(f.readlines()) - 1
        f.seek(0)
        m = 0
        num_of_samples = 0
        for i, line in enumerate(f):
            if i == 0:
                continue
            if (int(seed_number) - 1) * 125 < i <= (int(seed_number) * 125):
                num_of_samples += 1
                predict_steering_angle = line.split(',')[1]
                oriMSE = line.split(',')[2]
                true_angle_gt = line.split(',')[3]
                if ((float(yhat[m]) - float(predict_steering_angle)) ** 2) > (lamb * float(oriMSE)):
                    countcc = countcc + 1
                    list_row.append(
                        [filelist_list[m], predict_steering_angle, float(yhat[m]), true_angle_gt, model_name,
                         seed_number, m])
                    # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", predict_steering_angle, float(yhat[m]), oriMSE)
                    if a[seed_number - 1, m] == 0 and iterate != 0:
                        a[seed_number - 1, m] = 1
                        divadd = divadd + 1
                    error_list.append(m)

                else:
                    os.remove(test_dataset_path + 'center/' + filelist_list[m])
                if (m + 1) < lenm:
                    m = m + 1
                else:
                    break

        with open('/home/vangogh/software/FuzzScene/code/GA/sample_num.csv', 'a+', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            timestr = time.strftime("%Y%m%d-%H%M%S")
            csv_writer.writerow([timestr, model_name, seed_number, num_of_samples])

    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", countcc)
    np.savetxt("diversity.txt", a)

    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", is_err_collection)
    if is_err_collection == '1':  # Collect Data for RQ2 RQ3
        if err_type == '1' or err_type == '2':  # normal data
            file_path_img = '../Violated images/err_images/model_' + str(model_name) + '/'
            if err_type == '2':  # sampling data
                file_path_sam = '../Violated images/sampling/model_' + str(model_name) + '/error.csv'
                with open(file_path_sam, 'a+', encoding='utf-8') as f:
                    cw = csv.writer(f)
                    for line in range(len(list_row)):
                        cw.writerow(list_row[line])
        elif err_type == '3':  # random data
            file_path_img = '../Violated images/random/'
        file_path_error = file_path_img + 'error.csv'

        for img in list_row:
            shutil.move(test_dataset_path + 'center/' + img[0], file_path_img)

        with open(file_path_error, 'a+', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            for line in range(len(list_row)):
                csv_writer.writerow(list_row[line])

    # --------------------------------------Get_OriMSE---------------------------------------- #
    # filelist = []
    # with open(test_dataset_path + 'label_test.csv', 'r') as f:
    #     rows = len(f.readlines()) - 1
    #     f.seek(0)
    #     for i, line in enumerate(f):
    #         if i == 0:
    #             continue
    #         file_name = line.split(',')[0]
    #         filelist.append(file_name) 

    # file_path = '/home/software/FuzzScene/code/scenario_runner-0.9.13/_out/model4_oriMSE.csv'
    # with open(file_path, 'a+', encoding='utf-8') as f:
    #     for m in range(len(yhat)):  
    #         list_1 = [filelist[m],float(yhat[m]),loss]     
    #         csv_writer = csv.writer(f)
    #         csv_writer.writerow(list_1)
    # --------------------------------------Visualize results---------------------------------------- #
    # loss = calc_mse(yhat, test_y)
    # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", 'model %s MSE loss on test_set: %.8f' % (model_name, loss))

    # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------PLOT RESULT-------")
    # plt.figure(figsize=(32, 8))
    # plt.plot(test_y, 'r.-', label='target')
    # plt.plot(yhat, 'b.-', label='predict')
    # plt.legend(loc='best')
    # plt.title("loss(%s) %.8f Evaluated on %d images" % (model.loss, loss, len(test_y)))
    # model_fullname = "%s_%d.png" % (model_name, int(time.time()))
    # plt.savefig('./trained_models/{}_{}_loss {}_{} epochs_{} batch_size.png'.format(model_name, int(time.time()), model.loss, nb_epoch, batch_size))
    # plt.show()
    # print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", "--------PLOT RESULT COMPLETE-------")

    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", bcolors.OKGREEN + 'Model evaluated' + bcolors.ENDC)

    file = open('list.txt', 'w', encoding='utf-8')
    for i in range(len(error_list)):
        file.write(str(error_list[i]) + '\n')

    file.close()

    np.savetxt("list.txt", error_list)

    return countcc, divadd, error_list


if __name__ == '__main__':
    a = error_test()
    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", type(a))
    print("[" + os.path.basename(__file__) + ", Line " + str(sys._getframe().f_lineno) + ", " + sys._getframe().f_code.co_name + "] ", a)
    pricount, div, error_list = a
    error_count = './error_count.csv'
    with open(error_count, 'a+', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([sys.argv[3], pricount, div, error_list])
