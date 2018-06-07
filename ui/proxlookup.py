# file proxlookup.py
import pyodbc


def get_hawkID(prox):
    with pyodbc.connect( DRIVER='{SQL Server}', 
        SERVER='idw.dna.its.uiowa.edu',DATABASE='IDW2', 
        UID='engr-idw-papercut', PWD='truma2a3rEpr@ph',SSL='require' 
        ) as conn:
        with conn.cursor() as job_total_cur:
            job_total_cur.execute('''
            DECLARE @hawkid VARCHAR(30)
            EXEC [directory].[uspLookupHawkIdForProxNumber] @proxNumber = '392-%s', @hawkid = @hawkid OUTPUT, @noError = 1
            SELECT @hawkid''' % prox)
            job_rows = job_total_cur.fetchall()
            id=job_rows[0][0]
            return id
            
            #conn.close()
if __name__ == '__main__':

    print('hi people')
    x=get_hawkID('0080486')
    print(x)
    x=get_hawkID('0158076')
    print(x)
    x=get_hawkID('0069405')
    print(x)