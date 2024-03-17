import psychopy.visual as visual
import psychopy.core as core
import psychopy.event as event
import psychopy.gui as gui
import random
import sys
import time
import datetime
from psychopy.hardware.brainproducts import RemoteControlServer
import wave
import contextlib
import numpy as np
import os
import pygame as pg
import socket


#######################################
#########GUI部分记录被试编号############
#######################################

gui = gui.Dlg(title='information')
gui.addField('Number:')
gui.show()

if not gui.OK:
    sys.exit('user cancelled')

number=gui.data[0]

####################################################
#########避免被试编号重复导致数据被覆盖部分############
####################################################

all_subject=[]
if os.path.exists('attentionSubject.npy'):
    temp_sub=np.load('attentionSubject.npy')
    for t in range(len(temp_sub)):
        all_subject.append(temp_sub[t])
        if temp_sub[t]==number:
            sys.exit("already exist the subject")
else:
    all_subject.append(number)


################################
#########初始参数配置############
################################

myClock=core.Clock()
win = visual.Window(
    size=[1600,1000],
    fullscr=False,
    units='pix',
)

textInstr=visual.TextStim(
    win=win,
    color=[1.0,1.0,1.0],
    height=50,
    units='pix'
)
textInstr.text='根据提示，请做出相应的运动想象'

rectWidth=250
rectCenter=visual.Rect(
    win=win,
    height=rectWidth,
    width=rectWidth,
)
rectRight=visual.Rect(
    win=win,
    height=rectWidth,
    width=rectWidth,
)
rectLeft=visual.Rect(
    win=win,
    height=rectWidth,
    width=rectWidth,
)
rectTop=visual.Rect(
    win=win,
    height=rectWidth,
    width=rectWidth,
)
rectBottom=visual.Rect(
    win=win,
    height=rectWidth,
    width=rectWidth,
)

rectCenter.pos = [0, 0]
rectLeft.pos = [-rectWidth,0]
rectRight.pos = [rectWidth,0]
rectTop.pos = [0,rectWidth]
rectBottom.pos = [0,-rectWidth]

fist=visual.ImageStim(
    win=win,
    image='./fist.png',
    size=rectWidth,
)
fistOption={0:[-rectWidth,0],1:[rectWidth,0],2:[0,rectWidth],3:[0,-rectWidth]}


arrow=visual.ShapeStim(
    win=win,
    fillColor='darkred',
    size=.5,
    lineColor='red'
)

prepareTime=2
recordTime=4#10
restTime=4#6
cue={0:'左',1:'右',2:'上',3:'下'}

arrowOption={0:[(-rectWidth*2,0),(-rectWidth*1.2,rectWidth*0.4),(-rectWidth*1.2,rectWidth*0.2),(0,rectWidth*0.2),(0,-rectWidth*0.2),(-rectWidth*1.2,-rectWidth*0.2),(-rectWidth*1.2,-rectWidth*0.4)],
             1:[(rectWidth * 2, 0), (rectWidth * 1.2, rectWidth * 0.4),
                          (rectWidth * 1.2, rectWidth * 0.2), (0, rectWidth * 0.2), (0, -rectWidth * 0.2),
                          (rectWidth * 1.2, -rectWidth * 0.2), (rectWidth * 1.2, -rectWidth * 0.4)],
             2:[(0,rectWidth * 2), (rectWidth * 0.4,rectWidth * 1.2),
                          (rectWidth * 0.2,rectWidth * 1.2), ( rectWidth * 0.2,0), ( -rectWidth * 0.2,0),
                          ( -rectWidth * 0.2,rectWidth * 1.2), ( -rectWidth * 0.4,rectWidth * 1.2)],
             3:[(0,-rectWidth * 2), (rectWidth * 0.4,-rectWidth * 1.2),
                          (rectWidth * 0.2,-rectWidth * 1.2), ( rectWidth * 0.2,0), ( -rectWidth * 0.2,0),
                          ( -rectWidth * 0.2,-rectWidth * 1.2), ( -rectWidth * 0.4,-rectWidth * 1.2)]}

trail=4
session_num=2
trail_per_session=int(trail/session_num)

textInstr.draw()

win.flip()

k1=event.waitKeys()

labelIndex=[i for i in range(4)]

pg.mixer.init(buffer=1024)
dingAudio='ding.wav'
dingNote=pg.mixer.Sound(dingAudio)
pg.mixer.set_num_channels(1)

# rcs = RemoteControlServer()  # RemoteControlServer(host='127.0.0.1', port=6700, timeout=1.0, testMode=False)


################################
#########数据收集部分############
################################

for per_session in range(session_num):
    label = []
    # name = 'MI'
    # participant = 'Subject' + str(number) + '_' + 'Session' + str(per_session+1)
    # rcs.open(name, workspace='D:\MI-BCI\sub1\MI_BCI_BP.rwksp', participant=participant)
    # rcs.openRecorder()
    # rcs.mode = 'monitor'  # or 'impedence', or 'default'
    #
    # print('session '+str(per_session+1)+' start to record at ' + str(myClock.getTime()))
    # rcs.startRecording()
    textInstr.text='session '+str(per_session+1)+' 开始\n工作人员确定数据开始记录无误后\n按任意键开始'
    textInstr.draw()
    win.flip()
    keys=event.waitKeys()

    for i in range(trail_per_session):
        if (i%4==0):
            random.shuffle(labelIndex)
        random_index=labelIndex[i%4]
        label.append(random_index)
        arrow.vertices=arrowOption[random_index]
        fist.pos=fistOption[random_index]
        textInstr.text=str(prepareTime)+'s后听到”叮“声开始进行运动想象'
        textInstr.draw()
        win.flip()
        time.sleep(prepareTime)
        dingNote.play()
        time.sleep(0.5)
        rectCenter.draw()
        rectLeft.draw()
        rectRight.draw()
        rectTop.draw()
        rectBottom.draw()
        arrow.draw()
        fist.draw()


        win.flip()
        print('marker recording start at ' + str(myClock.getTime()))
        # rcs.sendAnnotation('trail'+ 'S', 'STIM')

        time.sleep(recordTime)

        print('marker recording end at ' + str(myClock.getTime()))
        # rcs.sendAnnotation('trail'+ 'E', 'STIM')

        if i == trail_per_session - 1:
            print('session '+str(per_session+1)+' stop to record at ' + str(myClock.getTime()))
            # rcs.stopRecording()
            label_array = np.array(label)
            np.save('sub'+str(number)+'_session_'+str(per_session+1)+'_label.npy', label_array)
        else:
            textInstr.text = '休息'+str(restTime)+'s后继续'
            textInstr.draw()
            win.flip()
            time.sleep(restTime)
    if per_session<session_num-1:
        textInstr.text = 'session'+str(per_session+1)+'结束\n休息片刻\n休息完毕后联系工作人员继续开始'
        textInstr.draw()
        win.flip()
        keys = event.waitKeys()


all_subject=np.array(all_subject)
np.save('attentionSubject.npy',all_subject)
textInstr.text = '测试完成，谢谢参与'
textInstr.draw()
win.flip()
key = event.waitKeys()

win.close()
