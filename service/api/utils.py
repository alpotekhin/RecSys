import pandas as pd

def get_model_names():
    existing_models = ["dummy", "knn", "vector", "dssm", "encoder", "ranker"]
    return existing_models


def get_popular_rec(user_id, pop_recs):
    if user_id in pop_recs['user_id'].unique():
        recs = pop_recs[pop_recs['user_id'] == user_id]['item_id'].to_list()
        return recs
    
    else:
        return pop_recs['item_id'].value_counts().index.to_list()


def get_knn_online_reco(user_id, knn):
    if user_id in list(knn.users_mapping):
        recs = knn.predict(pd.DataFrame([user_id], columns=['user_id']))
        
        return recs['item_id'].to_list()
    else:
        return []


def get_model_offline_reco(user_id, model_recs):
    if user_id in model_recs.keys():
        recs = model_recs[user_id]
        return recs
    
    else:
        return []
