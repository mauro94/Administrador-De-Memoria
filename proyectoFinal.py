#Equipo 7
#Mauro Amarante
#Gonzalo Gutierrez
#Otro

#FIFO
#Tamaño memoria real = 2048 bytes
#Tamaño meRMoia swap = 4096 bytes
#Tamaño páginas = 8 bytes

import math
import time
import copy

#variables
RM = []								#memoria real
Sw = {}								#swap
pageFaults = {}
fileName = "entrada.txt"			#archivo de text
nFreePageFrames = int(2048/8)		#numero de marcos de pagina libres en memoria real
swIndex = 0							#indice que indica la 'ubicacion actual' en la memoria swap
swapOutCounter = 0
swapInCounter = 0
currentProcessPageIndex = 0


#Estructura para un proceso
class PageFrame():
	nProcess = -1
	timestamp = -1.0
	pageFrame = -1
	pageFrameSwap = -1
	pageOrderNum = -1
	
	#constructor
	def __init__(self, pageFrame):
		nProces = -1
		self.pageFrame = pageFrame
	
	def modifyPageFrame(self, nProcess, pageFrame, pageOrderNum):
		self.nProcess = nProcess
		self.timestamp = float(time.time())
		self.pageFrame = pageFrame
		self.pageOrderNum = pageOrderNum
	
	def swapPageFrame(self, pageFrameSwap):
		self.pageFrameSwap = pageFrameSwap
		
	def updateTime(self):
		self.timestamp = float(time.time())
	
	
	
#Proceso para asignar memoria-----------------------------------------------------------------
#SE PUEDE VOLVER A CARGAR EL MISMO PROCESO?
def pProcess(nBytes, nProcess):
	#variables globales	
	global nFreePageFrames
		
	#variables
	blockSizeCounter = 0			#cuenta el espacio del bloque libre
	
	#revisar si el proceso cabe en memoria
	if int(nBytes) > 2048:
		print ("Este proceso no cabe en toda la memoria disponible")
		return
		
	#calcular numero de marcos de pagina requeridos
	pageFrames = math.ceil(int(nBytes)/(8))
	
    #si toda la memoria esta vacia
	#if pageFrames == 256:
	#	pageFrames = storeData(0, 2048, pageFrames, nProcess)
	#	nFreePageFrames -= (256 - pageFrames)
	
#	print("page frames: " + str(pageFrames))
#	print("free page frames: " + str(nFreePageFrames))
	
	#revisar si existen marcos de pagina libres suficientes
	if nFreePageFrames >= pageFrames:
		pageFramesNew = findFreeSpace(pageFrames, nProcess)
		if not pageFrames == 0:
			nFreePageFrames -= (pageFrames - pageFramesNew)
			pageFrames = pageFramesNew
		else:
			nFreePageFrames -= pageFrames
			
	#implementar politica de remplazo FIFO
	else:
		#si hay marcos de pagina libre, usarlos
		if nFreePageFrames > 0:
			pageFramesNew = findFreeSpace(pageFrames, nProcess)
			nFreePageFrames -= (pageFrames - pageFramesNew)
			pageFrames = pageFramesNew
		
		#si faltaron marcos de pagina por llenar, aplicar FIFO
		if pageFrames > 0:
			FIFO(pageFrames, nProcess, True)
	return	


		
def findFreeSpace(pageFrames, nProcess):
	#variables
	global RM
	byteCounter = 0			#cuenta el espacio del bloque libre
	countedPages = 0			#define los marcos de pagina actuales
	start = 0
	
	#buscar marco de pagina libre
	for i in range(2048):
		if RM[i].nProcess == -1:
			if byteCounter == 0:
				start = i
			byteCounter += 1
			
		else:
			if byteCounter > 0:
#				print("findfreespace")
#				print("bytecounter = " + str(byteCounter))
#				print("i = " + str(i))
				pageFrames = storeData(start, i, pageFrames, nProcess, True)
				byteCounter = 0
		
		countedPages = math.floor(byteCounter/8)
		
		if countedPages == pageFrames:
#			print("findfreespace2")
#			print("bytecounter = " + str(byteCounter))
#			print("i = " + str(i))
			return storeData(start, i, pageFrames, nProcess, True)
	
	if byteCounter > 0:
		pageFrames = storeData(start, i, pageFrames, nProcess, True)
	
	return pageFrames
		
		
		
		
		#si esta libre sumar a contador
#		if countedPages < pageFrames:
#			print("pag contadas = " + str(countedPages))
#			if RM[i].nProcess == -1:
#				byteCounter += 1
#			
#			else:
#				#calcular cuantos marcos de pagina van contados
#				countedPages = math.floor(byteCounter/8)
#				print("findfreespace")
#				print("bytecounter = " + str(byteCounter))
#				print("i = " + str(i))
#				pageFrames =  storeData(abs(byteCounter - i), i, pageFrames, nProcess)
#				#reiniciar contador
#				byteCounter = 0	
			
			#calcular cuantos marcos de pagina van contados
#			countedPages = math.floor(byteCounter/8)

#		else:
#			return pageFrames
		
#	return pageFrames


#funcion que almacena informacion en memoria
def storeData(start, end, pageFrames, nProcess, doPrint):
	#variables
	global RM
	global currentProcessPageIndex
	global swapInCounter
	global swapOutCounter
	
	
	byteCounter = 0		#contador de bytes
	
#	print("pageframes = " + str(pageFrames))
#	print("start = " + str(start))
#	print("end = " + str(end))

	
	#almacenar paginas disponibles
	for j in range(start, end+1):	
		#contar numero de bytes para definir si ya lleno una pagina
		byteCounter += 1
		
		#almacenar en memoria real
		RM[j].modifyPageFrame(int(nProcess), j, math.floor(currentProcessPageIndex/8))
		currentProcessPageIndex += 1
	
		#si ya se lleno un marco de pagina restar uno
		if byteCounter == 8:
			byteCounter = 0
			pageFrames -= 1
		
		if pageFrames == 0:
			if doPrint:
				print("Se asignaron los marcos de página " + str(start) + "-" + str((end+1) - (8 - (pageFrames%8))))
			
			return pageFrames
	if doPrint:
		print("Se asignaron los marcos de página " + str(start) + "-" + str((end+1) - (8 - (pageFrames%8))))
		
	

	return pageFrames	
	
	


def FIFO(pageFrames, nProcess, froRMMtoSw):
	#variables globales
	global RM
	global Sw
	
	#variables
	timestampsPF = []	#lista que almacenara en orden los procesos basado en tiempo
	lastSwapLocation = 0	#define la ubicacion de cambio entre RM y swap
			
	#copiar memoria real en nueva lista
	timestampsPF = copy.deepcopy(RM)
				
	#sortear lista basado en tiempo
	timestampsPF = sorted(timestampsPF, key=lambda pageFrame: pageFrame.timestamp)
	
	if froRMMtoSw:
		lastSwapLocation = swappingRMtoSw(pageFrames, timestampsPF, nProcess)
	else:
		return timestampsPF[0]

	#impresion de resultado	
	print ("Se asignaron los marcos de página " + str(timestampsPF[0].pageFrame) + "-" + str(lastSwapLocation) + "\n")
	
	return
	
def swappingRMtoSw(pageFrames, timestampsPF, nProcess):
	#variables globales
	global RM
	global Sw
	global swIndex
	global swapInCounter
	
	#variables
	swapLocation = 0	#define la ubicacion de cambio entre RM y swap
	
	pFrame = None					#define el marco de pagina a swapear
	check = 0
	pFrames = 0
	
#	for i in range(2048):
#		print(str(i) + " "+ str(timestampsPF[i].nProcess) + " " + str(timestampsPF[i].pageFrame) + " " + str(timestampsPF[i].timestamp)) 

	#por cada marco de pagina restante
	for i in range(pageFrames):
		#definir ubicacion del siguiente marco de pagina a cambiar
		swapLocation = timestampsPF[i*8].pageFrame
		
		#definir el marco de pagina a mover
		pFrame = RM[swapLocation]	
			
		#definir al marco de pagina que ser almacenado
		pFrame.swapPageFrame(swIndex)
		
		#agregar a diccionario
		#revisar si ya existe en el diccionario
		check = Sw.get(int(pFrame.nProcess), -1)
		if check == -1:
			list = []
			list.append(pFrame)
			Sw[int(pFrame.nProcess)] = list
#			print(list[0].nProcess)
#			print("n " + str(Sw[pFrame.nProcess][0].nProcess))
		
		#si el proceso ya existe en el diccionario
		else:
			Sw[int(pFrame.nProcess)].append(pFrame)
#			print(Sw[pFrame.nProcess][1].nProcess)
	#		print(str(Sw[int(pFrame.nProcess)][0].pageFrameSwap) + " " + str(pFrame.nProcess))

		#almacenar nuevo marco de pagina en memoria real
		storeData(swapLocation, swapLocation+8, 1, nProcess, False)
		
		#imprimir operacion
		print("Página " + str(int(timestampsPF[i*8].pageOrderNum)) + " del proceso " + str(timestampsPF[i*8].nProcess) + " swappeada al marco " + str(swIndex) + " del área de swapping")
		
		#incrementar indice de memoria swap
		swIndex += 1
		
		#si se llega al limite de la memoria
		if swIndex >= 2048:
			swIndex = 0
			
	swapInCounter += pageFrames
#	print("swapins: " + str(swapInCounter))
	return swapLocation + 7

#Proceso para asignar memoria TERMINA-------------------------------------------------------
	
	
	
#Proceso que modifica datos en cierta ubicación
def aProcess(virtualDir, nProcess, readModify):
	#global variables
	global pageFaults
	
	#variables
	page = 0
	displacement = 0
	realDir = 0
	realDirLocation = 0
	listTemp = None
	check = 0
	checkPageFault = 0
	
#	for i in range(2048):
#		print(str(i) + " "+ str(RM[i].nProcess) + " " + str(RM[i].pageFrame) + " " + str(RM[i].pageOrderNum)) 
		
	
	#revisar si proceso esta en memoria real o swapping, si no salir
	if not int(nProcess) in Sw:
		for i in range(2048):
			if RM[i].nProcess == int(nProcess):
				break
		
		if not RM[i].nProcess == int(nProcess):
			print("El proceso " + str(nProcess) + " no se encuentra en memoria.")
			return
	
	#imprimir instruccion
	print("Obtener la dirección real correspondiente a la dirección virtual " + str(virtualDir) + " del proceso " + str(nProcess))
	
	#calcular la pagina y desplazamiento (p, d)
	page = math.floor(int(virtualDir)/2048)
	displacement = int(virtualDir)%2048
	
	#calcular direccion real
	#revisar si pagina esta cargada en memoria
	check = Sw.get(int(nProcess), -1)
	
	if check == -1:
		for i in range(2048):
			if RM[i].nProcess == int(nProcess) and RM[i].pageOrderNum == int(page):
				realDirLocation = RM[i].pageFrame
				break
				
		realDir = realDirLocation + displacement
		
		if realDir < 2048:
			for i in range((realDir - (realDir%8)), (realDir - (realDir%8))+8):
				RM[i].updateTime()
		
	else:
		for i in range(len(Sw[int(nProcess)])):
			listTemp = Sw[int(nProcess)]	
			if listTemp[i].pageOrderNum == page:
#				print("WRWERW")
				#si no existe el proceso en pagefaults
				checkPageFaults = pageFaults.get(int(nProcess), -1)
				if checkPageFaults == -1:
#					print("DFSDFADSDFASDF")
					pageFaults[int(nProcess)] = 1
				else:
					print("aRGARTETARTAERTWTERT")
					pageFalults[int(nProcess)] += 1
				realDirLocation = swappingSwtoRM(8, nProcess, page, i)
				realDir = int(realDirLocation) + displacement
				del listTemp[i]
				break
				
		#if not listTemp[len(Sw[nProcess])-1].pageOrderNum == page:
		#	print("La direccion virtual " + str(virtualDir) + " no se encuentra en memoria.")
		#	return
	
	#imprimir direccion virtual y real
	if realDir <= 2048:
		if int(readModify) == 0:
			print("Dirección virtual: " + str(virtualDir) + ". Dirección real: " + str(realDir)) 
		else:
			print("Dirección virtual: " + str(virtualDir) + ". Dirección real: " + str(realDir) + " y modificar dicha dirección")
			print("Página " + str(math.floor(int(virtualDir)/8)) + " del proceso " + str(nProcess) + " modificada") 
	else:
		print("La direccion virtual " + str(virtualDir) + " no se encuentra en memoria.")
	
	return
	
def swappingSwtoRM(pageFrames, nProcess, page, swListLocation):
	#variables globales
	global RM
	global Sw
	global swIndex
	global swapOutCounter
	
	#variables
	processInRM = None
	swapLocation = 0
	pFrame = None					#define el marco de pagina a swapear
	check = 0
	
	processInRM = FIFO(pageFrames, nProcess, False)
	
	#definir ubicacion del siguiente marco de pagina a cambiar
	swapLocation = processInRM.pageFrame
	
	#definir el marco de pagina a mover
	pFrame = RM[swapLocation]
	
	#definir al marco de pagina que ser almacenado
	pFrame.swapPageFrame(swIndex)
	
	#agregar a diccionario
	#revisar si ya existe en el diccionario
	check = Sw.get(int(pFrame.nProcess), -1)
	if check == -1:
		list = []
		list.append(pFrame)
		Sw[int(pFrame.nProcess)] = list
	
	#si el proceso ya existe en el diccionario
	else:
		Sw[int(pFrame.nProcess)].append(pFrame)

	#almacenar nuevo marco de pagina en memoria real
	storeData(swapLocation, swapLocation+8, 1, nProcess, False)
	swapOutCounter += pageFrames
#	print("swapout: " + str(swapOutCounter))
	
	
	return swapLocation
	
	
	
#Proceso que libera memoria
def lProcess(nProcess):
	#variables globales
	global RM
	global Sw
	
	#variables
	counter = 0
	start = 0
	list = []
	check = 0
	
	print ("Liberar los marcos de página ocupados por el proceso " + str(nProcess))
	
	#buscar marco de pagina libre
	for i in range(2048):
		if RM[i].nProcess == int(nProcess):
			if counter == 0:
				start = i
			counter += 1
			RM[i] = PageFrame(i)
			
		else:
			if counter > 0:
				print("Se liberan los marcos de página de memoria real: [" + str(start) + ", " + str(start + counter) + "]")
				counter = 0
	
	check = Sw.get(int(nProcess), -1)
	if not check == -1:
		list = Sw[int(nProcess)]
		start = check[0].pageFrameSwap
		temp = []
		for i in range(len(check)):
			temp.append(check[i].pageFrameSwap)
			
		print("Se liberan los marcos de página de memoria swapping: {" + str(temp) + "}")
	return
	
	
	
	
	

def finish():
	global pageFaults
	global swapInCounter
	global swapOutCounter
	
	#variables
	timestampsPF = []	#lista que almacenara en orden los procesos basado en tiempo
	printList = []
	currentProcess = 0
	minTime = 0
	turnaround = 0
	averageTurnaround = 0
	processCounter = 0
	timeSum = 0
	line = None
	keys = []
			
	#copiar memoria real en nueva lista
	timestampsPF = copy.deepcopy(RM)
				
	#sortear lista basado en tiempo
	timestampsPF = sorted(timestampsPF, key=lambda pageFrame: pageFrame.nProcess, reverse=True)
	
	currentProcess = timestampsPF[0].nProcess
	minTime = timestampsPF[0].timestamp
	
#	for i in range(2048):
#		print(str(i) + " "+ str(timestampsPF[i].nProcess)) 
	
	for i in range(2048):
		if not currentProcess == -1:
			if currentProcess == timestampsPF[i].nProcess:
				if minTime > timestampsPF[i].timestamp:
					minTime = timestampsPF[i].timestamp
				
			else:
				turnaround = time.time() - minTime
				line = ("Turnaround del proceso " + str(currentProcess) + ": " + str(turnaround))
				printList.append(line)
				currentProcess = timestampsPF[i].nProcess
				minTime = timestampsPF[i].timestamp
				processCounter += 1
				timeSum += turnaround
	
	printList.reverse()
	
	for i in range(len(printList)):
		print(printList[i])
		
	averageTurnaround = timeSum/processCounter
	print()
	print("Turnaround promedio: " + str(averageTurnaround))
	print()
	
	keys = pageFaults.keys()
	
	for i in keys:
		print("El proceso " + str(i) + " tiene " + str(pageFaults[i]) + " page fault(s)")
	
	print()
	print("Número de swap ins: " + str(swapInCounter))
	print("Número de swap outs: " + str(swapOutCounter))
	
	swapInCounter = 0
	swapOutCounter = 0
		
	
	return

def end():
	print ("4")
	return


#inicializar memoria real con 2048 espacios
for i in range(2048):
	pageFrame = PageFrame(i)
	RM.append(pageFrame)

#abrir archivo lectura
txtFile = open(fileName)

#por cada linea de texto en el archivo
for line in txtFile:
	#dividir la linea en palabras
	words = line.split()
	#imprimir comando
	print(line)
#	for i in range(2048):
#				print(str(i) + " "+ str(RM[i].nProcess)) 
	#iniciar un proceso
	if words[0] == "P":
		pProcess(words[1], words[2])
#		for i in range(1000):
#			check = Sw.get(int(i), -1)
#			print(str(i) + " " + str(check))
#			if not check == -1:
#				list = Sw[i]
#				print("n = " + str(i))
#				for j in range(len(list)):
#					print(str(list[j].nProcess) + " " + str(list[j].pageFrameSwap))
	elif words[0] == "A":
		aProcess(words[1], words[2], words[3])
	elif words[0] == "L":
		lProcess(words[1])
	elif words[0] == "F":
		finish()
	else:
		end()
	print()
	print()
	currentProcessPageIndex = 0
	