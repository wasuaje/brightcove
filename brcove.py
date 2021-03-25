#!/usr/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import urllib,httplib
import urllib2
import simplejson as json
import math
import os
import datetime

#modulo para serializar el diccionario con la data
try:
    import cPickle as pickle
except ImportError:
    import pickle

#Variables necesarias
rtoken='2d_EENcDG2R81gfftbHHnICV52SOhqaDEQPT-IpQwioZcpzH8AQR-g..'
wtoken='2d_EENcDG2R81gfftbHHnICV52SOhqaDP_dzdMpwNzgQz9SUUzmgVQ..'
url='http://api.brightcove.com/services/library'
exportfilename='listado.csv'
titulos='id,name,shortDescription,longDescription,creationDate,publishedDate,lastModifiedDate,linkURL,linkText,tags,videoStillURL,thumbnailURL,referenceId,length,economics,playsTotal,playsTrailingWeek,FLVFullLength,videoFullLength'

def get_data(init=False):
	parametros={}
	parametros['command']='search_videos'
	parametros['token']=rtoken	
	parametros['get_item_count']='true'
	parametros['video_fields']='id'		

	video_data={}
	submitVarsUrlencoded = urllib.urlencode(parametros)	
	req = urllib2.Request(url,submitVarsUrlencoded)
	response = urllib2.urlopen(req)
	thePage = response.read()
	f=json.loads(thePage)	
	
	#obtengo por primera vez el conteo total de videos
	total_videos = f['total_count']
	#como puedo obtener 100 resultados obtengo el total de paginas
	paginas=math.ceil(total_videos/100)	
	paginas=int(paginas)
	
	#itero por cada pagina obtenido en el paso anterior
	for pg in range(0,paginas+1):
		parametros['page_number']=pg
		parametros['page_size']=100
		parametros['media_delivery']='http'
		#parametros.pop('video_fields')
		parametros['video_fields']=titulos
		submitVarsUrlencoded = urllib.urlencode(parametros)	
		req = urllib2.Request(url,submitVarsUrlencoded)
		response = urllib2.urlopen(req)
		thePage = response.read()
		f=json.loads(thePage)	
		#print f		
		print "pagina: %s" % pg		
		try:
			#itero por el contenido de cada pagina y lo salvo en un dict local
			for i in f['items']:
				#video_data[i['id']]={'nombre':i['name'],'url':i['FLVURL'],'descargado':0}
				video_data[i['id']]=i				
				
		except KeyError:
			print "Error obteniendo la informacion, tal vez deba ejecutar el script de nuevo"


	if init:
		#serializo el contenido del dict local
		os.remove("video_data.dat")
		fichero = file("video_data.dat", "w")
		pickle.dump(video_data, fichero, 2)
		fichero.close
	else:
		return video_data

def get_remote_recs():
	parametros={}
	parametros['command']='search_videos'
	parametros['token']=rtoken	
	parametros['get_item_count']='true'
	submitVarsUrlencoded = urllib.urlencode(parametros)	
	req = urllib2.Request(url,submitVarsUrlencoded)
	response = urllib2.urlopen(req)
	thePage = response.read()
	f=json.loads(thePage)	
	#obtengo por primera vez el conteo total de videos
	total_videos = f['total_count']
	return total_videos

def read_data():
	fichero = file("video_data.dat")
	data = pickle.load(fichero)
	fichero.close()
	return data

def update_data():
	print "Verificando informacion, espere..."
	remote_recs=0
	data=read_data()
	#print type(data)
	fisical_recs=len(data.keys())
	remote_recs=get_remote_recs()
	if remote_recs > fisical_recs:
		print "Es necesario actualizar, Videos locales: %s, Videos Remotos %s" % (fisical_recs,remote_recs)
		print "Este proceso puede tardar un poco, espere ..."
		mydict=get_data(False)				
		for i in mydict.keys():			
			if i not in data.keys():				
				#data[i]={}
				data[i]={'nombre':mydict[i]['nombre'],'url':mydict[i]['url'],'descargado':mydict[i]['descargado']}		
		
		fichero = file("video_data.dat", "w")
		pickle.dump(data, fichero, 2)
		fichero.close
		print "Actualizacion finalizada"
	else:
		print "No hay nada que actualizar"

def list_data_local():
	a=read_data()
	#titulos
	z=titulos+'\n'
	write_file(z)
	#lista con los titulos
	tit=titulos.split(',')
	#print tit
	for i in a.keys():
		x=''
		for t in tit:
			fld=a[i][t]						
			if isinstance(fld, long):		
				fld=str(fld)
			if fld == None:				
				fld=''
			if isinstance(fld, list):						
				fld=''
			if isinstance(fld, int):						
				fld=str(fld)
			if isinstance(fld, dict):						
				fld=''
			if 'Date' in t:
				pass
				#fld=datetime.datetime.fromtimestamp(int(fld)).strftime('%Y-%m-%d %H:%M:%S')
			fld = fld.replace('"',"'")
			fld = fld.encode('utf-8')			
			x+= '"'+fld+'",'
		#le agrego ultima comilla y el retorno de carro a efectos de mejor visibilidad
		x+='\n'
		write_file(x)

def write_file(newLine):	
	file = open(exportfilename, "a")
	file.write(newLine)
	file.close()

def delete_video(vidid):
	#en este caso el url es distinto		
	url="http://api.brightcove.com/services/post"
	parametros={}
	parametros['params']={'token':wtoken,'video_id':vidid,'cascade':'true'}
	parametros['method']='delete_video'	
	header = {"Content-Type":"application/x-www-form-urlencoded"}			
	submitVarsUrlencoded = urllib.urlencode({'json': json.dumps(parametros)})
	req = urllib2.Request(url,submitVarsUrlencoded,header)	
	response = urllib2.urlopen(req) 	
	thePage = response.read()
	f=json.loads(thePage)	
	#resutlado esperado en json 	{"result": {}, "error": null, "id": null}
	if f["error"] == None:
		print "Video eliminado"
	else:
		print "Error",f["error"]

def get_video_by_id(vidid):
	print "Buscando"
	parametros={}
	parametros['command']='find_video_by_id'
	parametros['token']=rtoken		
	parametros['video_id']=vidid

	submitVarsUrlencoded = urllib.urlencode(parametros)	
	req = urllib2.Request(url,submitVarsUrlencoded)
	response = urllib2.urlopen(req)
	thePage = response.read()
	f=json.loads(thePage)	
	if f:
		#obtengo por primera vez el conteo total de videos
		for i in f.keys():						
			if isinstance(f[i],dict):
				for h in f[i].keys():
					print '\t\t'+h+': \t\t',f[i][h]
			elif isinstance(f[i],str):			
				print i+': \t',f[i]
			elif isinstance(f[i],list):			
				print i
			else:
				print i+': \t',f[i]
	else:
		print "No se encontro video con id",vidid

def download_video(vidid):		
	data=read_data()	#local data 
	if vidid in data.keys():
		print "Archivo encontrado, descargando..."
		url=data[vidid]['FLVFullLength']['url']		
		file_name = url.split('/')[-1]
		tamano=data[vidid]['FLVFullLength']['size']/1000.00/1000.00
		print "Archivo: %s, tamaño: %s MB" % (file_name, tamano)
		print "Desde URL: ",url
		urllib.urlretrieve (url, file_name)
		print "Descarga finalizada"

def main():	
	usage = "utilizacion: %prog [options] "
	parser = OptionParser(usage)
	#parser.add_option("-h", "--help", action="help")
	parser.add_option("-l", "--local", action="store_true", dest="datalocal", help='Muestra la cantidad de registros en data local')
	parser.add_option("-i", "--init",  action="store_true", dest="init", help='Inicializa la data por primera vez, carga todo desde brightcove' )    
	parser.add_option("-r", "--remote",  action="store_true", dest="dataremote", help='Muestra la cantidad de registros en Brightcove' )    
	parser.add_option("-u", "--update",  action="store_true", dest="update", help='Actualiza la info local con la de Brightcove' )    
	parser.add_option("-t", "--list",  action="store_true", dest="list", help='Lista la data local separada por comas (,) Archivo: %s' % exportfilename )    	
	parser.add_option("-d", "--delete",  action="store", dest="id", type="int", help='Borra un video dado un id')    	
	parser.add_option("-s", "--show",  action="store", dest="id2", type="int", help='Muestra la data para un video que esta en Brightcove')    	
	parser.add_option("-w", "--download",  action="store", dest="id3", type="int", help='Descarga un video dado un ID ')    	
	
	(options, args) = parser.parse_args()	
	#if len(args) != 1:
	#	parser.error("numero incorrecto de argumentos")
	
	#Acciones sgun cada opcion elegida
	if options.datalocal:
		a=read_data()
		print "Numero de Registros locales:",len(a.keys())		
	
	if options.dataremote:
		a=get_remote_recs()
		print "Numero de Registros remotos:",a
	
	if options.update:
		update_data()		
	
	if options.init:
		get_data(True)
	
	if options.list:
		if os.path.exists(exportfilename):
			os.remove(exportfilename)
		list_data_local()
	
	if options.id > 0:
		delete_video(options.id)
	
	if options.id2 > 0:
		get_video_by_id(options.id2)

	if options.id3 > 0:
		download_video(options.id3)


if __name__ == "__main__":
    main()


