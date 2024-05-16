"""
Script for judge response
## Takahiro Kamijo
## 2024.03.05

"""



import pandas as pd
import os
import numpy as np
import tkinter.filedialog
import matplotlib.pyplot as plt

os.makedirs("./response_results", exist_ok=True)
os.chdir("./response_results")


def speed_calculation(xcoor, ycoor):  ##xcoor, ycoorは座標データのパス
    xlist = xcoor['blob_coord_x']
    ylist = ycoor['blob_coord_y']
    xnum = xcoor.shape[0]
    xcomean = []
    ycomean = []

    for i in range(0, xnum - 4):  # 一秒間の平均位置を出すことでスムージング 0.5~119.5 s
        xmean = (xlist[i + 4] + xlist[i + 3] + xlist[i + 2] + xlist[i + 1] + xlist[i]) / 5
        ymean = (ylist[i + 4] + ylist[i + 3] + ylist[i + 2] + ylist[i + 1] + ylist[i]) / 5
        xcomean.append(xmean)
        ycomean.append(ymean)

    xconum = len(xcomean)//4
    speed = []
    for i in range(0, xconum - 1):  ##1秒間隔でspeedを出す 1~119
        xdiff = xcomean[4*(i + 1)] - xcomean[4*i]
        ydiff = ycomean[4*(i + 1)] - ycomean[4*i]
        speed.append(np.sqrt(xdiff ** 2 + ydiff ** 2))


    time = list(np.arange(1, len(speed) + 1, 1))  ##timeは1秒から始まる(最初のスピードの値が0.5-1.5秒のスピードだから )
    df_speed = pd.DataFrame({'time': time,
                             'speed_mean': speed})


    speed_before_stimulus = np.mean(speed[54:59])  ##55~59秒のspeedの平均
    print(speed_before_stimulus)
    end = len(speed)
    speed_after_stimulus = speed[59:end]  ##60~119のspeed
    print(len(speed))

    ##判定

    a = 0
    response_delay = -4
    response = False
    for i in range(0, end-59):
        if speed_after_stimulus[i] > speed_before_stimulus:
            a += 1
        else:
            a = 0
        response_delay = response_delay + 1

        if a == 4:        ##最初にspeedが刺激前の最大値を超えてから4秒経過したらresponseとする

            response = True
            break

    if response:
        df_speed["response_delay"] = response_delay
    else:
        if end == 118: ##刺激開始から60秒以内に反応がなければ 59s
            df_speed["response_delay"] = 59
        else:    ##覚醒したという判定にならないまま画面から出たらNot applicable
            df_speed["response_delay"] = "Not applicable"

    df_speed.to_csv('./response.csv')

    ########################################################################################
    ###speedをプロット
    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 1)
    ti = time
    ax.plot(ti, speed)
    baseline = [speed_before_stimulus] * len(time)
    ax.plot(ti, baseline)
    ax.axvspan(response_delay + 60, response_delay + 63, color="coral")

    ###xをプロット
    axx = fig.add_subplot(223)
    tix = np.arange(0.5, len(xcomean) * 0.25 + 0.5, 0.25)
    axx.plot(tix, xcomean)
    axx.axvspan(response_delay + 60, response_delay + 63, color="coral")
    axx.axvspan(60, 60, color="green")

    ###yをプロット
    axy = fig.add_subplot(224)
    tiy = np.arange(0.5, len(xcomean) * 0.25 + 0.5, 0.25)
    axy.plot(tiy, ycomean)
    axy.axvspan(response_delay + 60, response_delay + 63, color="coral")
    axy.axvspan(60, 60, color="green")

    plt.savefig("./result.png")
    plt.show()


#################################################################################################

def main():
    # select file
    root = tkinter.Tk()
    root.withdraw()
    filepath_x = tkinter.filedialog.askopenfilename()

    root = tkinter.Tk()
    root.withdraw()
    filepath_y = tkinter.filedialog.askopenfilename()
    os.chdir(os.path.dirname(filepath_y))

    # Load data
    xcoor = pd.read_csv(filepath_x)
    ycoor = pd.read_csv(filepath_y)

    # Lethargus analysis
    speed_calculation(xcoor, ycoor)


if __name__ == '__main__':
    main()
