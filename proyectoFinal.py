#Equipo 7
#Mauro Amarante
#Gonzalo Gutierrez
#Otro

#FIFO
#Tamaño memoria real = 2048 bytes
#Tamaño memroia swap = 4096 bytes
#Tamaño páginas = 8 bytes

import math
import time

#variables
MR = []								#memoria real
Sw = []								#swap
fileName = "entrada.txt"		#archivo de text
nFreePageFrames = 2048/8		#numero de marcos de pagina libres en memoria real


#Estructura para un proceso
class Process():
	id = -1
	timestamp = time.time()
	rBit = 0
	mBit = 0

#Proceso para asignar memoria
#SE PUEDE VOLVER A CARGAR EL MISMO PROCESO?
def pProcess(nBytes, nProcess):
	#variables
	blockSize = 0						#tamaño del espacio disponible
	blockSizeCounter = 0			#cuenta el espacio del bloque libre
	initialPageFrameBlock = 0	#1 marco de página libre del bloque disponible
        counter = 0                 #contador de bytes
	
	#calcular numero de marcos de pagina requeridos
	pageFrames = math.ceil(int(nBytes)/(8))
	
	#revisar si existen marcos de pagina libres suficientes
	if nFreePageFrames >= pageFrames:
		#buscar marco de pagina libre
		for i in xrange(2048):
			#si esta libre sumar a contador
			if MR[i] == -1:
				blockSizeCounter += 1
			else:
                #almacenar paginas disponibles
                for j in xrange((i - blockSizeCounter), i):
                    #contar numero de bytes para definir si ya lleno una pagina
                    counter++
    
                    #Actucalizar numero de paginas por almacenar restantes
                    if counter == 8
                        #si faltan paginas del proceso por almacenar
                        if pageFrames > 0:
                            MR[j] = int(nProcess)
                            pageFrames--
                        #si ya se almacenaron todas las paginas
                        else
                            break
                        #reiniciar contador
                        counter = 0
 
                if pageFrames == 0
                #if blockSizeCounter >
                #	initialPageFrameBlock = i - blockSizeCounter - 2
                #	blockSize = blockSizeCounter
                
				#reiniciar contador
				blockSizeCounter = 0
		
		#si se encontro espacio, cargar a memoria el proceso
		if blockSize > 0:
			#asignar marcos de pagina
			for i in xrange(initialPageFrameBlock, (initialPageFrameBlock + blockSize + 1)):
				MR[i] = int(nProcess)
			nFreePageFrames -= pageFrames
				
    #si toda la memoria esta vacia
    elif nFreePageFrames == 256:
        #almacenar paginas disponibles
        for i in xrange(0, 2048):
            #contar numero de bytes para definir si ya lleno una pagina
            counter++
                
            #Actucalizar numero de paginas por almacenar restantes
            if counter == 8
                #si faltan paginas del proceso por almacenar
                if pageFrames > 0:
                    MR[i] = int(nProcess)
                        pageFrames--
                    #si ya se almacenaron todas las paginas
                    else
                        break
                #reiniciar contador
                counter = 0


	#implementar politica de remplazo FIFO
	else:
		
	#impresion de resultado	
	print ("Se asignaron los marcos de página ")
	return
	
#Proceso que modifica datos en cierta ubicación
def aProcess(virtualDir, nProcess, readModify):
	print ("2")
	return
	
#Proceso que libera memoria
def lProcess(nProcess):
	print ("3")
	return

def finish():
	print ("4")
	return

def end():
	print ("4")
	return


#inicializar memoria real con 2048 espacios
MR = [-1]*2048

#inicializar memoria swap con 4096 espacios
Sw = [-1]*4096

#abrir archivo lectura
txtFile = open(fileName)

#por cada linea de texto en el archivo
for line in txtFile:
	#dividir la linea en palabras
	words = line.split()
	#iniciar un proceso
	if words[0] == "P":
		pProcess(words[1], words[2])
	elif words[0] == "A":
		aProcess(words[1], words[2], words[3])
	elif words[0] == "L":
		lProcess(words[1])
	elif words[0] == "F":
		finish()
	else:
		end()
	