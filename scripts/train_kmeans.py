import torch
import numpy as np
from kmeans_pytorch import kmeans
import pandas as pd
import torch, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NUM_CLUSTERS = 300

def extractYear(datestr):
    return datetime.strptime(datestr, '%m/%d/%Y').year

def extractMonth(datestr):
    return datetime.strptime(datestr, '%m/%d/%Y').month

def extractDay(datestr):
    return datetime.strptime(datestr, '%m/%d/%Y').day

fpath = os.path.join(os.path.join(BASE_DIR, "media"), "gv_cleaned.csv")
data = pd.read_csv(fpath)
print(data.head())

data['year'] = list(map(extractYear, data['date']))
data['month'] = list(map(extractMonth, data['date']))
data['day'] = list(map(extractDay, data['date']))

data = data.fillna(0)

data = data[(data.n_killed != 0) | (data.n_injured != 0)].reset_index(drop=True)
print(data)

def getDataPair(data):
    x = torch.Tensor([
        data['latitude'].values, 
        data['longitude'].values, 
        data['month'].values, 
        data['day'].values,
        data['n_killed'].values,
        data['n_injured'].values,
        data['n_guns_involved'].values,
        ]).transpose(0,1)
    return x

train_data = data.iloc[:int(data.shape[0]*0.9), :]
test_data = data.iloc[int(data.shape[0]*0.9):, :]

train_x = getDataPair(train_data)
test_x = getDataPair(test_data)

cluster_ids_x, cluster_centers = kmeans(
    X=train_x, num_clusters=NUM_CLUSTERS, distance='euclidean'
)

df = pd.DataFrame(cluster_centers.data.tolist(), columns=['lat', 'lng', 'month', 'day', 'n_killed', 'n_injured', 'n_guns_involved'])
fpath = os.path.join(os.path.join(BASE_DIR, "media"), f"cluster-{NUM_CLUSTERS}.csv")
df.to_csv(fpath, index = False)
