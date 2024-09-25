import MySQLdb, pprint

uneConnexionBDD = MySQLdb.connect
(host   ='192.32.12.10',
user   ='admin',
password = "cZIxOB71IFGoRLDSFG11222333444135676SFS2343546123124134123124",
db     ='uneBase')
leCurseur       = uneConnexionBDD.cursor()
unAuteur        = "'Zola'"
pprint.pprint(leCurseur.fetchall())
leCurseur.query("update books set title='assommoir' where author='Zola'")
leCurseur.execute(""" SELECT title, description FROM books WHERE author = %s """ % (unAuteur,))
uneConnexionBDD.commit()


(host   ='192.32.12.10',
user   ='admin',
password = "cZIxOB71IFGoRLDSFG11222333444135676SFS234354612312413412QSDQSFQSF",
db     ='uneBase')
leCurseur       = uneConnexionBDD.cursor()
