#Equipo 7
#Mauro Amarante
#Gonzalo Gutierrez

#FIFO
#Tamaño memoria real = 2048 bytes
#Tamaño meRMoia swap = 4096 bytes
#Tamaño páginas = 8 bytes

#librerias necesarias
import math
import time
import copy

#variables globales
RM = []								#memoria real
Sw = {}								#diccionario para memoria swap
pageFaults = {}						#diccionario de page faults
processPageOrderManager = {}		#diccionario que administra el indice de las paginas de los procesos
fileName = "entrada.txt"			#archivo de texto
nFreePages = int(2048/8)			#numero de paginas libres en memoria real
swIndex = 0							#indice que indica la 'ubicacion actual' en la memoria swap
swapOutCounter = 0					#contador de swapouts
swapInCounter = 0					#contador de swapins


#------------------------------------------------------------------------------------------------



#Estructura para cada marco de página en Memoria
class PageFrame():
	#variables
	nProcess = -1			#numero de proceso
	timestamp = -1.0		#timestamp en segundos
	pageFrame = -1		#marco de pagina en memoria real
	pageFrameSwap = -1	#marco de pagina en memoria swap
	pageOrderNum = -1	#numero de pagina del proceso
	
	#Función: constructor
	#Constructor de la clase PageFrame
	#Parámetros: 
	#	-self: a si mismo
	#	-pageFrame: marco de pagina en memoria real
	#Regresa:
	#	NADA
	def __init__(self, pageFrame):
		nProces = -1
		self.pageFrame = pageFrame
	
	#Función: modifyPageFrame
	#Modifica la informacion del marco de página y define el tiempo de acceso
	#Parámetros: 
	#	-self: a si mismo
	#	-nProcess: proceso al cual pertenece el marco de página
	#	-pageFrame: marco de pagina en memoria real
	#	-pageOrderNum: numero de pagina del proceso
	#Regresa:
	#	NADA
	def modifyPageFrame(self, nProcess, pageFrame, pageOrderNum):
		self.nProcess = nProcess
		self.timestamp = float(time.time())
		self.pageFrame = pageFrame
		self.pageOrderNum = pageOrderNum
	
	#Función: swapPageFrame
	#Modifica la informacion necesaria cuando el marco es enviado a memoria swap
	#Parámetros: 
	#	-self: a si mismo
	#	-pageFrameSwap: marco de pagina en memoria swap
	#Regresa:
	#	NADA
	def swapPageFrame(self, pageFrameSwap):
		self.pageFrameSwap = pageFrameSwap
		
	#Función: updateTime
	#Modifica el tiempo al tiempo actual
	#Parámetros: 
	#	-self: a si mismo
	#Regresa:
	#	NADA
	def updateTime(self):
		self.timestamp = float(time.time())

#END PageFrame



#------------------------------------------------------------------------------------------------



#Función: pProcess
#Proceso que carga un proceso a memoria real
#Parámetros: 
#	-nBytes: numero de bytes del proceso
#	-nProcess: numero de proceso
#Regresa:
#	NADA
def pProcess(nBytes, nProcess):
	#variables globales	
	global nFreePages
		
	#variables
	pages = 0		#numero de paginas necesarias en memoria real
	pagesNew = 0	#numero de paginas restantes por almacenar en memoria real
	
	#revisar si el proceso cabe en memoria
	if int(nBytes) > 2048:
		print ("Este proceso no cabe en toda la memoria disponible")
		return
		
	#calcular numero de paginas requeridas
	pages = math.ceil(int(nBytes)/(8))
	
	#revisar si existen paginas libres suficientes
	if nFreePages >= pages:
		#Encontrar el espacio libre en memoria
		pagesNew = findFreeSpace(pages, nProcess)
		
		#Si se logro acomodar todos los marcos de página
		if not pages == 0:
			#restar páginas almacenadas al total de páginas libres
			nFreePages -= (pages - pagesNew)
			pages = pagesNew
		#Si faltan páginas por almacenar
		else:
			#restar paginas almacenadas
			nFreePages -= pages
			
	#si no hay marcos de página libre suficientes, hacer remplazo (FIFO)
	else:
		#si hay marcos de pagina libre, usarlos
		if nFreePages > 0:
			#buscar y asignar los marcos de página libres
			pagesNew = findFreeSpace(pages, nProcess)
			#actualizar numero de páginas libres restantes
			nFreePages -= (pages - pagesNew)
			#definir marcos de pagina restantes
			pages = pagesNew
		
		#si faltaron marcos de pagina por llenar, aplicar FIFO
		if pages > 0:
			#FIFO
			FIFO(pages, nProcess, True)
	
	return	

#END pProcess


#------------------------------------------------------------------------------------------------



#Función: findFreeSpace
#Función que encuentra el espacio libre en memoria real
#Parámetros: 
#	-pages: numero de páginas necesarias
#	-nProcess: numero de proceso
#Regresa:
#	número de marcos de página despues de almacenar datos en memoria real
def findFreeSpace(pages, nProcess):
	#variables globales
	global RM		
	
	#variables
	pagefCounter = 0		#contador de marcos de página
	start = 0				#inicio de espacio libre
	countedPages = 0		#cantidad de paginas libres al momento
	
#buscar marcos de página libres en memoria real
	for i in range(2048):
		#si esta libre el marco de página
		if RM[i].nProcess == -1:
			#si es el primer marco de página libre
			if pagefCounter == 0:
				#asignar inicio de espacio libre
				start = i
			#agregar uno al contador de marcos de página libres
			pagefCounter += 1
		
		#si el marco de página esta ocupado
		else:
			#si ya se han encontrado marcos de página libre
			if pagefCounter > 0:
				#almacenar datos en los marcos de página encontrados antes
				pages = storeData(start, i, pages, nProcess, True)
				#reiniciar contado de marcos de página
				pagefCounter = 0
		
		countedPages = math.floor(pagefCounter/8)
		
		#si se encontraron los marcos de página necesarios
		if countedPages == pages:
			#almacenar datos en los marcos de página encontrados
			return storeData(start, i, pages, nProcess, True)
	
	#si hay marcos de página libres
	if pagefCounter > 0:
		#almacenar datos en los marcos de página encontrados
		pages = storeData(start, i, pages, nProcess, True)
	
	#regresar número de marcos de página restantes por almacenar en memoria real
	return pages

#END findFreeSpace



#------------------------------------------------------------------------------------------------

		



#Función: storeData
#Función que almacena datos en memoria
#Parámetros: 
#	-start: posicion inicial en memoria real para almacenar datos
#	-end: posicion final en memoria real para almacenar datos
#	-pages: numero de marcos de página necesarios
#	-nProcess: proceso al cual pertenece el marco de página
#	-doPrint: define si se debe imprimir resultados
#Regresa:
#	número de marcos de página despues de almacenar datos en memoria real
def storeData(start, end, pages, nProcess, doPrint):
	#variables globales
	global RM
	global swapInCounter
	global swapOutCounter
	global Sw
	global processPageOrderManager
	
	
	#variabes
	pagefCounter = 0			#contador de marcos de página
	dictionaryCheck = 0		#variable auxiliar para apoyo en busqueda de valores en diccionarios
	pageOrderIndex = 0		#indice de pagina dentro de un proceso
	
	#definir numero de pagina siguiente para el proceso
	#Revisar si esta en administrador de orden de paginas del proceso
	dictionaryCheck = processPageOrderManager.get(int(nProcess), -1)
	#Si esta en administrador
	if not dictionaryCheck == -1:
		#definir siguiente pagina del proceso
		pageOrderIndex = processPageOrderManager[int(nProcess)]
	
	#almacenar paginas disponibles
	for j in range(start, end+1):	
		#contar marcos de página para definir si ya lleno una pagina
		pagefCounter += 1
		
		#almacenar en memoria real
		RM[j].modifyPageFrame(int(nProcess), j, pageOrderIndex)
	
		#si ya se lleno una pagina
		if pagefCounter == 8:
			#incrementar indice de pagina
			pageOrderIndex += 1
			#reiniciar contador de marcos de pagina
			pagefCounter = 0
			#restar una pagina a las restantes por almacenar
			pages -= 1
		
		#si ya no faltan paginas
		if pages == 0:
			#si es necesario impirmir
			if doPrint:
				print("Se asignaron los marcos de página " + str(start) + "-" + str((end+1) - (8 - (pages%8))))
			#actualizar numero de pagina del proceso
			processPageOrderManager[int(nProcess)] = pageOrderIndex
			return pages
			
	#si es necesario imprimir
	if doPrint:
		print("Se asignaron los marcos de página " + str(start) + "-" + str((end+1) - ((pages%8))))
		
	#actualizar numero de pagina del proceso
	processPageOrderManager[int(nProcess)] = pageOrderIndex
	
	return pages	

#END storeData



#------------------------------------------------------------------------------------------------
	


#Función: FIFO
#Función que inicia el procedimiento de remplazo FIFO
#Parámetros: 
#	-pages: numero de marcos de página necesarios
#	-nProcess: proceso al cual pertenece el marco de página
#	-fromRMtoSw: define si se esta pasando memoria de memoria real a swap o al reves
#Regresa:
#	la ubicacion de swapping
def FIFO(pages, nProcess, fromRMtoSw):
	#variables globales
	global RM
	global Sw
	
	#variables
	timestampsPF = []		#lista que almacenara en orden los procesos basado en tiempo
	lastSwapLocation = 0	#define la ultima ubicacion de cambio entre RM y swap
	minIndex = 3000			#indice minimo para la primer asignacion del proceso
			
	#copiar memoria real en nueva lista
	timestampsPF = copy.deepcopy(RM)
				
	#sortear lista basado en tiempo
	timestampsPF = sorted(timestampsPF, key=lambda pageFrame: pageFrame.timestamp)
	
	#si se requiere traspaso de memoria real a swap
	if fromRMtoSw:
		lastSwapLocation = swappingRMtoSw(pages, timestampsPF, nProcess)
	#si se requiere traspaso de memoria swap a real
	else:
		return timestampsPF[0]

	#impresión de resultado	
	for i in range(pages*8):
		#definir el marco de pagina inicial
		if minIndex > timestampsPF[i].pageFrame:
			minIndex = timestampsPF[i].pageFrame
		#si se llego al limite de memoria real
		if timestampsPF[i].pageFrame == 2047:
			print ("Se asignaron los marcos de página " + str(timestampsPF[0].pageFrame) + "-" + str(2047))
		
	#impresión
	print ("Se asignaron los marcos de página " + str(minIndex) + "-" + str(lastSwapLocation))
	
	return
	
#END storeData



#------------------------------------------------------------------------------------------------
	
	
	
#Función: swappingRMtoSw
#Función que hace el swapping de memoria real a memoria swap
#Parámetros:
#	-pages: numero de páginas necesarios
#	-timestampsPF: lista que almacenara en orden los procesos basado en tiempo
#	-nProcess: proceso al cual pertenece el marco de página
#Regresa:
#	la ubicacion ultima ubicacion del swap
def swappingRMtoSw(pages, timestampsPF, nProcess):
	#variables globales
	global RM
	global Sw
	global swIndex
	global swapInCounter
	
	#variables
	swapLocation = 0			#define la ubicacion de cambio entre RM y swap
	pFrame = None				#define el marco de pagina a swapear
	dictionaryCheck = 0		#variable auxiliar para apoyo en busqueda de valores en diccionarios

	#por cada pagina restante
	for i in range(pages):
		#definir ubicacion del siguiente marco de pagina a cambiar
		swapLocation = timestampsPF[i*8].pageFrame
		
		#definir el marco de pagina a mover
		pFrame = RM[swapLocation]	
			
		#definir al marco de pagina que sera almacenado
		pFrame.swapPageFrame(swIndex)
		
		#agregar a diccionario/memoria swap
		#revisar si ya existe en el diccionario
		dictionaryCheck = Sw.get(int(pFrame.nProcess), -1)
		if dictionaryCheck == -1:
			list = []
			list.append(pFrame)
			Sw[int(pFrame.nProcess)] = list
		
		#si el proceso ya existe en memoria swap
		else:
			#agregar a la memoria
			Sw[int(pFrame.nProcess)].append(pFrame)

		#almacenar nueva pagina en memoria real
		storeData(swapLocation, swapLocation+8, 1, nProcess, False)
		
		#imprimir operacion
		print("Página " + str(int(timestampsPF[i*8].pageOrderNum)) + " del proceso " + str(timestampsPF[i*8].nProcess) + " swappeada al marco " + str(swIndex) + " del área de swapping")
		
		#incrementar indice de memoria swap
		swIndex += 1
		
		#si se llega al limite de la memoria
		if swIndex >= 2048:
			#reiniciar indice de memoria swap
			swIndex = 0
	
	#contar swapins		
	swapInCounter += pages
	
	return swapLocation + 7

#END swappingRMtoSw



#------------------------------------------------------------------------------------------------
	
	
	
#Función: aProcess
#Función que accesa informacion en meoria real
#Parámetros:
#	-virtualDir: dirección virtual
#	-nProcess: proceso al cual pertenece el marco de página
#	-readModify: define si es solo lectura o escritura tambien
#Regresa:
#	NADA
def aProcess(virtualDir, nProcess, readModify):
	#variables globales
	global pageFaults
	
	#variables
	page = 0							#pagina calculada a partir de la direccion virtual
	displacement = 0					#desplazamiento calculado a partir de la direccion virtual
	realDir = 0						#direccion en memoria real
	realDirLocation = 0				#marco de pagina de la direccion real (direccion real sin desplazamiento)
	listTemp = None					#lista auxiliar
	dictionaryCheck = 0				#variable auxiliar para apoyo en busqueda de valores en diccionarios
	dictionaryCheckPageFault = 0	#variable auxiliar para apoyo en busqueda de valores en pagefaults
	aux = 0							#vairable auxiliar en la busqueda del proceso
	
	#calcular la pagina y desplazamiento (p, d)
	page = math.floor(int(virtualDir)/8)
	displacement = int(virtualDir)%8
	
	#imprimir instruccion
	print("Obtener la dirección real correspondiente a la dirección virtual " + str(virtualDir) + " del proceso " + str(nProcess))
	
	#calcular direccion real
	#revisar si pagina esta cargada en memoria swap
	dictionaryCheck = Sw.get(int(nProcess), -1)
	#si no esta en memoria swap
	if dictionaryCheck == -1:
		#buscar en memoria real
		for i in range(2048):
			#Encontrar marco de pagina con el mismo proceso y numero de pagina del proceso
			if RM[i].nProcess == int(nProcess) and RM[i].pageOrderNum == page:
				realDirLocation = RM[i].pageFrame
				break
				
		#calcular direccion real
		realDir = realDirLocation + displacement
		
		#si direccion real esta en memoria
		if realDir < 2048:
			#accesar informacion y actualizar tiempo en marcos de pagina
			for i in range((realDir - (realDir%8)), (realDir - (realDir%8))+8):
				#actualizar tiempo
				RM[i].updateTime()
				
	#si esta en memoria swapping
	else:
		for i in range(len(Sw[int(nProcess)])):
			#copiar lista a una temporal
			listTemp = copy.deepcopy(Sw[int(nProcess)])			
			print("p: " + str(nProcess)+" lista: " + str(listTemp[i].pageOrderNum) + "  page: " + str(page))
			
			#si la pagina del proceso es la buscada
			if listTemp[i].pageOrderNum == page:
				print("GFGFG")
				#revisar si existe existe el proceso en el diccionario pagefaults
				dictionaryCheckPageFaults = pageFaults.get(int(nProcess), -1)
				
				#si no existe
				if dictionaryCheckPageFaults == -1:
					#asignar un pagefault
					pageFaults[int(nProcess)] = 1
					
				#si existe
				else:
					#sumar un pagefault
					pageFalults[int(nProcess)] += 1
					
				#calcular direccion real	
				realDirLocation = swappingSwtoRM(8, nProcess, page, i)
				realDir = int(realDirLocation) + displacement
				
				#borrar lista temporal
				del listTemp[i]
				break
				
	#imprimir direccion virtual y real
	#si la direccion esta en memoria
	if realDir <= 2048:
		#si solo se lee
		if int(readModify) == 0:
			print("Dirección virtual: " + str(virtualDir) + ". Dirección real: " + str(realDir)) 
		#si se modifica tambien	
		else:
			print("Dirección virtual: " + str(virtualDir) + ". Dirección real: " + str(realDir) + " y modificar dicha dirección")
			print("Página " + str(math.floor(int(virtualDir)/8)) + " del proceso " + str(nProcess) + " modificada") 
	
	#si la direccion real no esta en memoria
	else:
		print("La direccion virtual " + str(virtualDir) + " no se encuentra en memoria.")
	
	return
	
#END aProcess



#------------------------------------------------------------------------------------------------
	
#-------------NO FUNCIONA CORRECTAMENTE---------------------
	
#Función: swappingSwtoRM
#Función que hace el swapping de memoria swap a memoria swap
#Parámetros:
#	-pageFrames: numero de marcos de pagina
#	-nProcess: proceso al cual pertenece el marco de página
#	-page : numero de página del proceso
#	-swListLocation: ubicación en memoria swap
#Regresa:
#	Ubicacion del ultimo swap
def swappingSwtoRM(pageFrames, nProcess, page, swListLocation):
	#variables globales
	global RM
	global Sw
	global swIndex
	global swapOutCounter
	
	#variables
	processInRM = None		#siguiente proceso a swapear en memoria real
	swapLocation = 0			#ubicacion del marco de pagina a swapear a memoria real
	pFrame = None				#almacena el marco de pagina a swapear
	dictionaryCheck = 0		#variable auxiliar para apoyo en busqueda de valores en diccionarios
	
	#pedir siguiente proceso a remplazar en memoria real utilizando politica FIFO
	processInRM = FIFO(pageFrames, nProcess, False)
	
	#definir ubicacion del siguiente marco de pagina de memoria real a swapear
	swapLocation = processInRM.pageFrame
	
	#almacenar el marco de pagina de memoria real a mover a memoria swap
	pFrame = RM[swapLocation]
	
	#definir ubicacion en memoria swap a donde se mandara este marco de pagina
	pFrame.swapPageFrame(swIndex)
	
	print("ver: " + str(swapLocation))
	
	#agregar a memoria swap
	#revisar si proceso del marco de pagina de memoria real ya existe en el memoria swap
	dictionaryCheck = Sw.get(int(pFrame.nProcess), -1)
	#si no esta en memoria swap
	if dictionaryCheck == -1:
		#agregar a memoria swap
		list = []
		list.append(pFrame)
		Sw[int(pFrame.nProcess)] = list
	
	#si el proceso del marco de pagina de memoria real ya existe en la memoria swap
	else:
		Sw[int(pFrame.nProcess)].append(pFrame)

	#almacenar nuevo marco de pagina en memoria real
	storeData(swapLocation, swapLocation+8, 1, nProcess, False)
	swapOutCounter += pageFrames
	
	#incrementar indice de memoria swap
	swIndex += 1
	
	#si se llega al limite de la memoria
	if swIndex >= 2048:
		#reiniciar indice de memoria swap
		swIndex = 0
		
	
	return swapLocation
	
#END swappingSwtoRM



#------------------------------------------------------------------------------------------------
		
	
	
#Función: lProcess
#Función que libera la memoria real y memoria swap de un proceso
#Parámetros:
#	-nProcess: proceso al cual pertenece el marco de página
#Regresa:
#	NADA
def lProcess(nProcess):
	#variables globales
	global RM
	global Sw
	
	#variables
	counter = 0				#contador para el rango de borrado
	start = 0					#inicio del rango
	list = []					#lista temporal para impresion de marcos de pagina eliminados en memoria swap
	dictionaryCheck = 0		#variable auxiliar para apoyo en busqueda de valores en diccionarios
	
	print ("Liberar los marcos de página ocupados por el proceso " + str(nProcess))
	
	#buscar marco de pagina ocupados por el proceso
	for i in range(2048):
		#encontrar marcos de pagina del proceso
		if RM[i].nProcess == int(nProcess):
			#contar rango de marcos de pagina a borrar
			if counter == 0:
				start = i
			counter += 1
			RM[i] = PageFrame(i)
			
		else:
			#imprimir resultados
			if counter > 0:
				print("Se liberan los marcos de página de memoria real: [" + str(start) + ", " + str(start + counter) + "]")
				counter = 0
	
	#encontrar en memoria swap proceso y elminarlo
	dictionaryCheck = Sw.get(int(nProcess), -1)
	if not dictionaryCheck == -1:
		list = Sw[int(nProcess)]
		start = dictionaryCheck[0].pageFrameSwap
		temp = []
		for i in range(len(dictionaryCheck)):
			temp.append(dictionaryCheck[i].pageFrameSwap)
			
		print("Se liberan los marcos de página de memoria swapping: {" + str(temp) + "}")
		
		del Sw[int(nProcess)]
		
	return

#END lProcess



#------------------------------------------------------------------------------------------------
	
	
	
	
#Función: finish
#Función que imprime resultados al momento
#Parámetros:
#	NADA
#Regresa:
#	NADA
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
		
	
	return

def end():
	print ("MUCHAS GRACIAS")
	return

#END finish



#------------------------------------------------------------------------------------------------

#Función: main
#Función main del programa
#Parámetros:
#	NADA
#Regresa:
#	NADA

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
	
	for i in range(2048):
		print(str(i) + " " + str(RM[i].nProcess) + " " + str(RM[i].pageOrderNum))
	
	#iniciar un proceso
	if words[0] == "P":
		try:
			p1 = int(words[1])
			p2 = int(words[2])
		except ValueError:
			print("COMANDO INVALIDO")
			print()
			continue
		pProcess(words[1], words[2])
	elif words[0] == "A":
		try:
			p1 = int(words[1])
			p2 = int(words[2])
			p2 = int(words[3])
		except ValueError:
			print("COMANDO INVALIDO")
			print()
			continue
		aProcess(words[1], words[2], words[3])
	elif words[0] == "L":
		try:
			p1 = int(words[1])
		except ValueError:
			print("COMANDO INVALIDO")
			print()
			continue
		lProcess(words[1])
	elif words[0] == "F":
		finish()
	elif words[0] == "E":
		end()
	else:
		print("COMANDO INVALIDO")
	print()
	print()
	
#END main



#------------------------------------------------------------------------------------------------