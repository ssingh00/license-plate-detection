import os
import re
import pandas as pd
from google.cloud import storage


storage_client = storage.Client()



def get_gcs_files(file_dir):
    li = []
    prefix = "/".join(file_dir.split('/')[3:])
    for blob in storage_client.list_blobs(file_dir.split('/')[2], prefix=prefix): 
        li.append(blob.name)
    return li
        
    

def create_dataset(path,gcs=False):
    train_dir = os.path.join(path,'train','annot_csv')
    test_dir = os.path.join(path,'test','annot_csv')
    if gcs:
        train = get_gcs_files(train_dir)
        test  = get_gcs_files(test_dir)
        files = train + test
    final_df = pd.DataFrame()
    for file in files:
        df = pd.read_csv(os.path.join('gs://',path.split('/')[2],file))
        df['set'] = "TRAIN" if re.search("train", file) else "TEST"
        df['x1'] = df['xmin'] / df['width'] 
        df['x2'] = df['xmax'] / df['width'] 
        df['y1'] = df['ymin'] / df['height']
        df['y2'] = df['ymax'] / df['height']
        final_df = final_df.append(df)
    final_df = final_df.rename(columns = {'filename':'image_path','class':'label'})    
    final_df = final_df[['set','image_path','label','x1','y1','x2','y1','x2','y2','x1','y2']]
    return final_df