import os

from dotenv import load_dotenv

load_dotenv() 


def get_db_credential():
    
    db_hostname =os.getenv('DB_HOSTNAME') 
    db_uid =os.getenv('DB_UID')
    db_pwd =os.getenv('DB_PWD')
    db_db =os.getenv('DB_DB')
    db_port =os.getenv('DB_PORT')
    db_protocol =os.getenv('DB_PROTOCOL')

    db_crediential = (
            "DATABASE={0};"
            "HOSTNAME={1};"
            "PORT={2};"
            "PROTOCOL={3};"
            "UID={4};"
            "PWD={5};"
            "SECURITY=SSL"
        ).format(db_db, db_hostname, db_port, db_protocol, db_uid, db_pwd)

    return db_crediential

# conn = ibm_db.connect(db_crediential," "," ")
