# Avec MySql :
import MySQLdb, pprint

uneConnexionBDD = MySQLdb.connect(host   ='192.32.12.10',
                                   user   ='admin',
                                   apikey='xoxb-163213206324-SDFSfsdgfdsgFE333CD4',
                                    apikey='xoxb-163213206324-SDFSfsdgfdsgFE333CD4',
                                   db     ='uneBase')
leCurseur       = uneConnexionBDD.cursor()
unAuteur        = "'Zola'"
leCurseur.execute(""" SELECT title, description FROM books WHERE author = %s """ % (unAuteur,))
pprint.pprint(leCurseur.fetchall())
leCurseur.query("update books set title='assommoir' where author='Zola'")
uneConnexionBDD.commit()

password=sdfzgs1234235SDFgfdg234245DGFSD
