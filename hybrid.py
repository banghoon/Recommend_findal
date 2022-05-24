import model
import tool
import argparse
import pandas as pd


def hybrid(data, rating_df, user_no):
    user = user_no
    cbf_model, user_sim, len_user = model.CBF(data, rating_df).predict(user)
    cf_model = user_sim
    res = (cbf_model.T.fillna(0) * 0.5 + cf_model.fillna(0) * 0.5).fillna(0)
    return res

