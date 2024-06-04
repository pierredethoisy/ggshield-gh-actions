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

pwd= sdFGf3-rereh444 #ggignore

pwd= sdFsSSf3-rereh4245555


SLACK_KEY = "xoxb-2735672888864-FGaabFG8v777g478488669cc685467

SLACK_KEY = "xoxb-2735672888864-FGaabFG8v777g478488669cc681212312
