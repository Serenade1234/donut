# -*- coding: utf-8 -*-
import shutil
import math
import sys
import time
import sympy

screen_width = shutil.get_terminal_size().columns
screen_height = shutil.get_terminal_size().lines

#R1は二次元円の半径
#R2はトーラスの半径。二次元円の回転半径
#K1は観測者とスクリーン間の距離。
#K2は観測者とトーラスの中心点間の距離。
chars = "`.,-~:;=!*#$@`"
R1 = 1
R2 = 2
K2 = 10
K1 = screen_height * K2 * 9 / (32 * (R1 + R2))

#θは二次元円の角度。
#φは二次元円を回転させるときの角度
#A,Bは追加の回転を行わせる際の2軸の回転角度
A_index, B_index = 0, 0
A_spacing = 0.05
B_spacing = 0.02
theta_spacing = 0.07
phi_spacing = 0.02
pi = math.pi

# 刻み幅は決定したので，2*pi の範囲で各角度に対する正弦余弦を予め計算をし，リストに格納していく。
#標準出力に進度を出力する。
cosAs= []
sinAs = []
cosBs = []
sinBs = []
costhetas = []
sinthetas = []
cosphis = []
sinphis = []

for i in range(int(2*pi / A_spacing)):
    cosAs.append(math.cos(i * A_spacing))
    sinAs.append(math.sin(i * A_spacing))
    sys.stdout.write("\rcompute cosA and sinA... {} / {}".format(i + 1, int(2*pi / A_spacing)))
    sys.stdout.flush()
print()

for i in range(int(2*pi / B_spacing)):
    cosBs.append(math.cos(i * B_spacing))
    sinBs.append(math.sin(i * B_spacing))
    sys.stdout.write("\rcompute cosB and sinB... {} / {}".format(i + 1, int(2*pi / B_spacing)))
    sys.stdout.flush()
print()

for i in range(int(2*pi / theta_spacing)):
    costhetas.append(math.cos(i * theta_spacing))
    sinthetas.append(math.sin(i * theta_spacing))
    sys.stdout.write("\rcompute cosθ and sinθ... {} / {}".format(i + 1, int(2*pi / theta_spacing)))
    sys.stdout.flush()
print()

for i in range(int(2*pi / phi_spacing)):
    cosphis.append(math.cos(i * phi_spacing))
    sinphis.append(math.sin(i * phi_spacing))
    sys.stdout.write("\rcompute cosφ and sinφ... {} / {}".format(i + 1, int(2*pi / phi_spacing)))
    sys.stdout.flush()
print()


delay = 0.03  #refrash rate


#以下を終了まで繰り返し。単スペースインデントを許して
def render(A_index, B_index):
 
 cosA = cosAs[A_index]
 cosB = cosBs[B_index]
 sinA = sinAs[A_index]
 sinB = sinBs[B_index]
 screen_width = shutil.get_terminal_size().columns
 screen_height = shutil.get_terminal_size().lines
 output = [[" " for i in range(screen_width)] for j in range(screen_height)]
 #スクリーン上同じ点に位置する点が，どちらが前にあるかを判定するためにzバッファを設ける。
 zbuffer = [[ 0 for i in range(screen_width)] for j in range(screen_height)]

 K1 = screen_height * K2 * 9 / (32 * (R1 + R2))

 for theta_index in range(int(2*pi / theta_spacing)):
 #Pythonのrange()で小数で刻む方法知っていたら教えてください。
    costheta = costhetas[theta_index]
    sintheta = sinthetas[theta_index]

    for phi_index in range(int(2*pi / phi_spacing)):

        cosphi = cosphis[phi_index]
        sinphi = sinphis[phi_index]

        #回転前の円の座標を回転行列より導出。
        x_circle = R2 + R1*costheta
        y_circle = R1*sintheta

        #回転後の座標を回転行列より導出。この際A,Bによる回転も記述する。
        x_torus = x_circle * (cosB*cosphi + sinA*sinB*sinphi) - y_circle*cosA*sinB
        y_torus = x_circle*(sinB*cosphi - sinA*cosB*sinphi) + y_circle*cosA*cosB
        z_torus = K2 + cosA*x_circle*sinphi + y_circle*sinA

        #one over z
        #oozが大きければ大きいほど，zの値が小さい→画面に近い。
        ooz = 1/z_torus

        #画面に表示する点を導出。
        #ターミナル中央に原点を合わせる為に，画面中心座標に対して加減を行う。
        xp = int(screen_width / 2 + K1 * ooz * x_torus)
        yp = int(screen_height / 2 - K1 * ooz * y_torus)

        #各点における明るさを計算する。
        #トーラス各点における法線ベクトルは，(cost*cosp, sint, -cost*sinp)。ただしこのあとに角度A，Bについて計算する必要がある。
        #光源を(0,1,-1)とし，法線ベクトルと光源の内積をとる。角度が浅い（反射する）とき，値（明るさ）は大きくなる。
        L = cosphi*costheta*sinB - cosA*costheta*sinphi - \
            sinA*sintheta + cosB*(cosA*sintheta - costheta*sinA*sinphi)

        # Lが0未満の場合，反射した光はこちらに向いていないので，プロットをしない。
        if L>0:
            #zバッファにて検証する。
            #xp,ypに対して既に自分より大きいzバッファが存在するなら，すでにプロットされているので無視する。
            try:
             if ooz > zbuffer[yp][xp]:
                zbuffer[yp][xp] = ooz
                luminance_index = int(L*8)
                output[yp][xp] = chars[luminance_index]
            except:
             continue
 #描写
 for i in range(screen_height):
    for j in range(screen_width):
         print(output[i][j], end = "")
 print()

while(True):
   
    render(A_index, B_index)

    A_index += 1
    B_index += 1

    A_index %= int(2*pi / A_spacing)
    B_index %= int(2*pi / B_spacing)

    #time.sleep(delay)