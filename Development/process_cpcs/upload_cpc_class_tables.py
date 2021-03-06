import sys
import os
import pandas as pd
from sqlalchemy import create_engine
from warnings import filterwarnings
import csv
import re,os,random,string,codecs
import sys
sys.path.append('/project/Development')
sys.path.append('{}/{}'.format(os.getcwd(), 'Development'))
from helpers import general_helpers



def upload_cpc_small_tables(db_con,db,folder):
    '''
    db_conn: sql alchemy connection engine
    db : name of the database
    folder: where the cpc_group/subsection folders are
    '''
    #Upload CPC subsection data
    mainclass = csv.reader(open(os.path.join(folder,'cpc_subsection.csv'),'r'))
    counter =0
    for m in mainclass:
        towrite = [re.sub('"',"'",item) for item in m]
        query = 'insert into {}.cpc_subsection values("{}", "{}")'.format(db,towrite[0], towrite[1])
        db_con.execute(query)

    #Upload CPC group data
    subclass = csv.reader(open(os.path.join(folder,'cpc_group.csv')))
    exist = set()
    for m in subclass:
        towrite = [re.sub('"',"'",item) for item in m]
        if not towrite[0] in exist:
            exist.add(towrite[0])
            query = 'insert into {}.cpc_group values("{}", "{}")'.format(db,towrite[0],towrite[1])
            db_con.execute(query)

def upload_cpc_subgroup(db_con, db, folder):
    '''
    db_con : sql alchemy connection engine
    db: new/updated database
    folder: where the cpc_group/subsection folders are
    This is a separate function because the one-by-one insert is too slow
    So instead post-process and then upload as a csv
    '''
    subgroup = csv.reader(open(os.path.join(folder,'cpc_subgroup.csv'),'r'))
    subgroup_out = csv.writer(open(os.path.join(folder,'cpc_subgroup_clean.csv'),'w'),delimiter = '\t')
    subgroup_out.writerow(['id', 'title'])
    exist = set()
    for m in subgroup:
        towrite = [re.sub('"',"'",item) for item in m]
        if not towrite[0] in exist:
            exist.add(towrite[0])
            clean = [i if not i =="NULL" else "" for i in towrite]
            subgroup_out.writerow(clean)
    print('now uploading')
    data = pd.read_csv('{0}/{1}'.format(folder, 'cpc_subgroup_clean.csv'), delimiter = '\t', encoding ='utf-8')
    data.to_sql('cpc_subgroup',db_con, if_exists = 'append', index=False)
    
if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('/project/Development/config.ini')

    db_con = general_helpers.connect_to_db(config['DATABASE']['HOST'], config['DATABASE']['USERNAME'], 
                                            config['DATABASE']['PASSWORD'], config['DATABASE']['NEW_DB'])

    cpc_folder = '{}/{}'.format(config['FOLDERS']['WORKING_FOLDER'],'cpc_output')
    
    upload_cpc_small_tables(db_con,config['DATABASE']['NEW_DB'],cpc_folder)
    upload_cpc_subgroup(db_con,config['DATABASE']['NEW_DB'],cpc_folder)
