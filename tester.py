import pyodbc


def get_hawkID(prox):
    with pyodbc.connect( DRIVER='{SQL Server}', 
        SERVER='idw.dna.its.uiowa.edu',DATABASE='IDW2', 
        UID='engr-idw-papercut', PWD='truma2a3rEpr@ph',SSL='require' 
        #SERVER='idw.test.dna.its.uiowa.edu',DATABASE='IDW2', 
        #UID='engr-idw-emscontrol', PWD='Exu7zag6qypqnqs',SSL='require' 
        ) as conn:
        with conn.cursor() as job_total_cur:
            job_total_cur.execute('''
            DECLARE @hawkid VARCHAR(30)
            EXEC [directory].[uspLookupHawkIdForProxNumber] @proxNumber = '%s', @hawkid = @hawkid OUTPUT, @noError = 1
            SELECT @hawkid''' % prox)
            job_rows = job_total_cur.fetchall()
            print(job_rows)
            #conn.close()

print('hi people')
get_hawkID('392-0080486')
get_hawkID('392-0158076')
get_hawkID('392-0069405')
get_hawkID('392-0090001')
get_hawkID('392-0010371')
get_hawkID('392-0090031')
get_hawkID('392-0082301')
get_hawkID('392-0126170')

