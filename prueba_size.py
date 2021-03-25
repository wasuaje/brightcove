#!/usr/bin/python
# -*- coding: utf-8 -*-
from  brcove import *
from  datetime import datetime

titulos='id,name,renditions,shortDescription,longDescription,creationDate,publishedDate,lastModifiedDate,linkURL,linkText,tags,videoStillURL,thumbnailURL,referenceId,length,economics,playsTotal,playsTrailingWeek,FLVFullLength,videoFullLength'

def get_size():
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
	total=0.00
	#itero por cada pagina obtenido en el paso anterior	
	print 'ID,Nombre,Peso Original,Fecha Creacion,Suma Peso Renditions'
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
		#print f['items']['videoFullLength']['renditions']		
		#print "pagina: %s - Total hasta ahora %s GB" % (pg,total/1000/1000/1000)
		try:
			linea=''
			for i in f['items']:
				#print "\tVideo: %s " % i['name']
				fecha=datetime.strftime(datetime.fromtimestamp(int(i['creationDate'])/1000),'%Y-%m-%d')
				nombre='"'+i['name'].encode('utf-8')+'"'
				linea+=str(i['id'])+','+nombre+','+str(i['videoFullLength']['size'])+','+fecha+','
				total+=i['videoFullLength']['size']
				rnd=0
				subrnb=0.00
				for h in i['renditions']:				
					rnd+=1
					subrnb+=h['size']
					total+=h['size']
					#print "\t\trendition: %s - Peso: %s MB" % (rnd,h['size']/1000/1000)
				linea+=str(subrnb)+'\n'
			print linea
		except KeyError:
			print "Error obteniendo la informacion, tal vez deba ejecutar el script de nuevo"
	print total/1000/1000/1000


get_size()

#total=0
#total2=0
#for i in data.keys():
	#print data[i]['videoFullLength']['size'],data[i]['videoFullLength']['size']/1000/1000
#	total+=data[i]['videoFullLength']['size']
#	print data[i]
#	total_2+=data[i]['FLVFullLength']['size']
#print total,total/1000/1000,total/1000/1000/1000
#print total2,total2/1000/1000,total2/1000/1000/1000
#{'items': [
 