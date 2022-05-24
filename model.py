from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import tool


def similarity_matrix(a, b=None):
    sim = None
    if b is None:
        sim = cosine_similarity(a.values, a.values)
    else:
        sim = cosine_similarity(a.values, b.values)
    return pd.DataFrame(data=sim, columns=a.index.values, index=a.index)


def rating(rating_df, sim_df, user, rating_col='review_point', user_col='user_no', item_col='caregiver_no'):
    user_sim = sim_df.loc[rating_df[rating_df[user_col] == user][item_col]]
    user_rating = rating_df[rating_df[user_col] == user][rating_col]
    sim_sum = user_sim.sum(axis=0)
    predict_ratings = np.matmul(user_rating, user_sim.to_numpy()) / sim_sum
    return predict_ratings, user_sim, len(user_rating)


class CBF:
    def __init__(self, data, rating_df):
        self.data = tool.pre_filtering(data)
        self.index = data['caregiver_no']
        self.rating_df = rating_df
        self.sim_df = None

    def predict(self, user, sim_func='cosine', rating_col='review_point', user_col='user_no', item_col='caregiver_no'):
        self.sim_df = similarity_matrix(self.data, self.data)
        result, user_sim, len_user = rating(self.rating_df, self.sim_df, user, rating_col, user_col, item_col)
        return pd.Series(result, index=self.index), user_sim, len_user


class CF:
    def __init__(self, rating_df):
        self.data = None
        self.sim_df = None
        self.rating_df = rating_df

    def predict(self, user, sim_func='cosine', rating_col='review_point', user_col='user_no', item_col='caregiver_no'):
        self.data = self.rating_df.pivot_table(rating_col, item_col, user_col,  aggfunc='mean').fillna(0)
        self.sim_df = similarity_matrix(self.data, self.data)
        result, user_sim, len_user = rating(self.rating_df, self.sim_df, user, rating_col, user_col, item_col)
        return result, user_sim, len_user

