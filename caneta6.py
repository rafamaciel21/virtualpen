import cv2
import numpy as np
import time


load_from_disk = True
if load_from_disk:
    penval = np.load('penval.npy')
 
cap = cv2.VideoCapture(0)
 
# Carregue estas 2 imagens e redimensione-as para o mesmo tamanho.
pen_img = cv2.resize(cv2.imread('caneta.png',1), (50, 50))
eraser_img = cv2.resize(cv2.imread('borracha.png',1), (50, 50))
 
kernel = np.ones((5,5),np.uint8)
 
# Tornando o tamanho da janela ajustável.
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
 
# Este é o quadro no qual iremos desenhar.
canvas = None
 
#Crie um objeto de subtrator de fundo.
backgroundobject = cv2.createBackgroundSubtractorMOG2(detectShadows = False)
 
# Este limiar determina a quantidade de distúrbio no fundo.
background_threshold = 600
 
# Uma variável que indica se você está usando uma caneta ou uma borracha.
switch = 'Pen'
 
# Com esta variável, monitoraremos o tempo entre a troca anterior.
last_switch = time.time()
 
# Inicialize os pontos x1 e y1.
x1,y1=0,0
 
# Limiar para ruído.
noiseth = 800
 
# Limiar para o limpador: o tamanho do contorno deve ser maior do que este valor para que possamos limpar a tela.
wiper_thresh = 4000
 
# Uma variável que indica quando limpar a tela.
clear = False
 
while(1):
    _, frame = cap.read()
    frame = cv2.flip( frame, 1 )
     
    # Inicialize a tela (canvas) como uma imagem preta.
    if canvas is None:
        canvas = np.zeros_like(frame)
         
    # Pegue o canto superior esquerdo do quadro e aplique o subtrator de fundo nele.   
    top_left = frame[0: 50, 0: 50]
    fgmask = backgroundobject.apply(top_left)
     
    # Observe o número de pixels que são brancos; esse é o nível de distúrbio.
    switch_thresh = np.sum(fgmask==255)
     
    # Se o distúrbio for maior do que o limiar de fundo e houver algum tempo após a troca anterior, então você pode mudar o tipo de objeto.
    if switch_thresh>background_threshold and (time.time()-last_switch) > 1:
 
        #Salve o tempo da troca.
        last_switch = time.time()
         
        if switch == 'Pen':
            switch = 'Eraser'
        else:
            switch = 'Pen'
 
    # Converta de BGR para HSV.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
    # Se você estiver lendo da memória, carregue os intervalos superior e inferior de lá.
    if load_from_disk:
            lower_range = penval[0]
            upper_range = penval[1]
             
    # Caso contrário, defina seus próprios valores personalizados para o intervalo superior e inferior.
    else:             
       lower_range  = np.array([89, 130, 136])
       upper_range = np.array([179, 255, 255])
       
     
    mask = cv2.inRange(hsv, lower_range, upper_range)
     
    # Realize operações morfológicas para eliminar o ruído.
    mask = cv2.erode(mask,kernel,iterations = 1)
    mask = cv2.dilate(mask,kernel,iterations = 2)
     
    # Localiza os contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
    cv2.CHAIN_APPROX_SIMPLE)
     
    # Certifique-se de que há um contorno presente e que seu tamanho seja maior do que o limiar de ruído.
    if contours and cv2.contourArea(max(contours,
                                      key = cv2.contourArea)) > noiseth:
                 
        c = max(contours, key = cv2.contourArea)    
        x2,y2,w,h = cv2.boundingRect(c)
         
        # Obtenha a área do contorno.
        area = cv2.contourArea(c)
        
         
        # Se não houver pontos anteriores, salve as coordenadas detectadas de x2, y2 como x1, y1.
        if x1 == 0 and y1 == 0:
            x1,y1= x2,y2
             
        else:
            if switch == 'Pen':
                # Desenhe a linha na tela (canvas).
                canvas = cv2.line(canvas, (x1,y1),
                (x2,y2), [255,0,0], 5)
                 
            else:
                cv2.circle(canvas, (x2, y2), 20,
                (0,0,0), -1)
             
             
         
        # Após a linha ser desenhada, os novos pontos se tornam os pontos anteriores.
        x1,y1= x2,y2
         
        # Agora, se a área for maior que o limite do limpador, defina a
        #variável clear como True.
        if area > wiper_thresh:
           cv2.putText(canvas,'Clearing Canvas',(0,200), 
           cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 1, cv2.LINE_AA)
           clear = True
 
    else:
        # Se nenhum contorno for detectado, defina x1 e y1 como 0.
        x1,y1 =0,0
     
    
    # Agora, este trecho de código é apenas para um desenho mais suave. (Opcional)
    _ , mask = cv2.threshold(cv2.cvtColor (canvas, cv2.COLOR_BGR2GRAY), 20, 
    255, cv2.THRESH_BINARY)
    foreground = cv2.bitwise_and(canvas, canvas, mask = mask)
    background = cv2.bitwise_and(frame, frame,
    mask = cv2.bitwise_not(mask))
    frame = cv2.add(foreground,background)
 
    # Altere as imagens dependendo do que estamos usando, caneta ou borracha.
    if switch != 'Pen':
        cv2.circle(frame, (x1, y1), 10, (255,255,255), -1)
        frame[0: 50, 0: 50] = eraser_img
    else:
        frame[0: 50, 0: 50] = pen_img
 
    cv2.imshow('image',frame)
 
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
     
    # Limpe a tela após 1 segundo, se a variável de limpeza for verdadeira.
    if clear == True: 
        time.sleep(1)
        canvas = None
         
        # E então defina a variável de limpeza como falsa.
        clear = False
         
cv2.destroyAllWindows()
cap.release()