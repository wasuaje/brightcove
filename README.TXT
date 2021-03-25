# En produccion SPRO necesitas instalar simplejson 
# Ya esta instalado en WEB01, que fue donde hice las pruebas
# Metodo:

tar xzvf simplejson-2.1.0.tar.gz
cd simplejson-2.1.0
python setup.py install

# Si solicita instalar setuptolls nuevo, adelante que lo instale automaticamente, PERO SI FALLA, en el directorio esta descargado
# Instalar usando:

easy_install setuptools-0.6c11-py2.4.eg

# Ejecutar de nuevo la instalacion de simplejson

# Ambos paquetes estan adjuntos al tar
