## Script for judge response
## Takahiro Kamijo
## 2024.05.03

import pandas as pd
import os
import numpy as np
import tkinter.filedialog
import matplotlib.pyplot as plt

os.makedirs("./response_results", exist_ok=True)
os.chdir("./response_results")


def speed_calculation(xcoor, ycoor):  ##xcoor, ycoorは座標データのパス
    xlist = xcoor['Center_X']
    ylist = ycoor['Center_Y']
    xnum = xcoor.shape[0]
    xcomean = []
    ycomean = []

    for i in range(0, xnum - 4):  # 一秒間の平均位置を出すことでスムージング 0.5~119.5 s
        xmean = (xlist[i + 4] + xlist[i + 3] + xlist[i + 2] + xlist[i + 1] + xlist[i]) / 5
        ymean = (ylist[i + 4] + ylist[i + 3] + ylist[i + 2] + ylist[i + 1] + ylist[i]) / 5
        xcomean.append(xmean)
        ycomean.append(ymean)

    length = len(xcomean)
    dist_before = [] #0~120 sの距離を格納
    dist_after = [] #120~240 sの距離を格納

    for i in range(0, 478):  ##最初の位置からどれだけ動いたかを計算
        xdiff = xcomean[i] - xcomean[0]
        ydiff = ycomean[i] - ycomean[0]
        dist_before.append(np.sqrt(xdiff ** 2 + ydiff ** 2))

    for i in range(478, length):  ##最初の位置からどれだけ動いたかを計算
        xdiff = xcomean[i] - xcomean[478]
        ydiff = ycomean[i] - ycomean[478]
        dist_after.append(np.sqrt(xdiff ** 2 + ydiff ** 2))


    print(len(dist_after))
    print(len(dist_before))
    length_after= len(dist_after)

    before = max(dist_before[:])
    after = max(dist_after[:])
    print(before)
    print(after)
    time = list(np.arange(0.5, len(xcomean)*0.25 + 0.5, 0.25))  ##timeは1秒から始まる(最初のスピードの値が0.5-1.5秒のスピードだから )
    df_speed = pd.DataFrame({'time': time,
                             'x': xcomean,
                             'y': ycomean })



    #120 sの時点の位置から体の半分以上離れたら反応したとみなす
    delay = 0
    response = False

    for i in range(0, length_after):
        if dist_after[i]<17:
            delay += 0.25
        else:
            response = True
            break

    if before<17:
        if response:
            df_speed["response_delay"] = delay
        else:
            df_speed["response_delay"] = 120
    else:
        df_speed["response_delay"] = "Not applicable"


    df_speed.to_csv('./response.csv')

    ###speedをプロット
    fig = plt.figure()
    ###xをプロット
    axx = fig.add_subplot(211)
    tix = np.arange(0.5, len(xcomean) * 0.25 + 0.5, 0.25)
    axx.plot(tix, xcomean)
    axx.axvspan(120, 120, color="green")

    ###yをプロット
    axy = fig.add_subplot(212)
    tiy = np.arange(0.5, len(xcomean) * 0.25 + 0.5, 0.25)
    axy.plot(tiy, ycomean)
    axy.axvspan(120, 120, color="green")

    plt.savefig("./result.png")


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
