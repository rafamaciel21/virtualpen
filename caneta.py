import cv2
import numpy as np

#Um método de callback obrigatório que é inserido na função da barra deslizante.
def nothing(x):
    pass
 
# IInicializando a webcam.
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
 
# Crie uma janela chamada "trackbars".
cv2.namedWindow("Trackbars")
 
#Agora crie 6 barras deslizantes que controlarão o intervalo inferior e superior dos canais H, S e V. 
# Os argumentos são os seguintes: Nome da barra deslizante, nome da janela, intervalo e função de callback. 
# Para o canal Hue (H), o intervalo é de 0 a 179, e para os canais Saturação (S) e Valor (V), o intervalo é de 0 a 255.
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)
  
  
while True:
     
    # Comece a capturar o feed da webcam quadro a quadro.
    ret, frame = cap.read()
    if not ret:
        break
    # Inverta o quadro horizontalmente (opcional).
    frame = cv2.flip( frame, 1 ) 
     
    # Converta a imagem BGR para uma imagem HSV.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
    # Obtenha os novos valores das barras deslizantes em tempo real conforme o usuário os ajusta.
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")
  
    # Defina os intervalos inferior e superior de HSV de acordo com os valores selecionados pelas barras deslizantes.
    lower_range = np.array([l_h, l_s, l_v])
    upper_range = np.array([u_h, u_s, u_v])
     
    # Filtre a imagem e obtenha a máscara binária, onde o branco representa a cor alvo.
    mask = cv2.inRange(hsv, lower_range, upper_range)
  
    # Você também pode visualizar a parte real da cor alvo (opcional).
    res = cv2.bitwise_and(frame, frame, mask=mask)
     
    # Converta a máscara binária para uma imagem de 3 canais, isso é feito apenas para que possamos empilhá-la com as outras.
    mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
     
    # Empilhe a máscara, o quadro original e o resultado filtrado.
    stacked = np.hstack((mask_3,frame,res))
     
    # Exiba o quadro empilhado com 40% do tamanho original.
    cv2.imshow('Trackbars',cv2.resize(stacked,None,fx=0.4,fy=0.4))
     
    # Se o usuário pressionar ESC, saia do programa.
    key = cv2.waitKey(1)
    if key == 27:
        break
     
    # Se o usuário pressionar s, imprima este array.
    if key == ord('s'):
         
        thearray = [[l_h,l_s,l_v],[u_h, u_s, u_v]]
        print(thearray)
         
        # Também salve este array como `penval.npy`.
        np.save('penval',thearray)
        break
     
#Libere a câmera e destrua as janelas. 
cap.release()
cv2.destroyAllWindows()