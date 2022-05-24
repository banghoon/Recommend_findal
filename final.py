import pandas as pd
import hybrid
import tool
import json
import random
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def recommend_(user_no, top, caregiver_gender, caregiver_grade):
    care, caregiver, review = tool.load_data()
    new = len(care[care.user_no == user_no]) <= 1 and care[care.user_no == user_no].caregiver_no.values <= 0

    if bool(new):
        result = caregiver.set_index("caregiver_no").loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]
        result['work_list'] = result.work_ability.astype(str).apply(lambda x: len(x.split(',')))
        result['work_day'] = result[['group_re', 'group_am', 'group_ch', 'group_su', 'group_ku', 'group_etc']].sum(axis=1)
        result_caregiver = result.sort_values(by=['work_day', 'caregiver_career', 'work_list'], ascending=False).iloc[:top*3].sample(frac=1)
    else:
        used_caregiver = care[(care.user_no == user_no) & (care.caregiver_no > 0)].caregiver_no.values
        select_caregiver = used_caregiver[np.random.randint(len(used_caregiver))]
        careable_work = tool.careable_work(caregiver)
        similarity_workability = pd.DataFrame(cosine_similarity(careable_work.values, careable_work.loc[select_caregiver].values.reshape(1, -1)),index=caregiver.caregiver_no)
        # 리뷰가 존재하는 기존 유저
        if tool.have_reviews(user_no, review.user_no.to_list()):
            result = hybrid.hybrid(caregiver, review, user_no)

            if result.shape[0] == 1:
                result = result.T.loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]
            elif result.shape[0] == 0:
                return json.dumps({"data": {
                    "caregivers": ['']}})
            else:
                result = result.loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]
            result_caregiver = pd.concat([result,
                                          caregiver.set_index("caregiver_no").loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no],
                                          similarity_workability.loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]], axis=1).sort_values(by=[7, 0, "caregiver_career"], ascending=False)

        # 리뷰가 존재하지 않는 기존 유저
        else:
            result_caregiver = pd.concat([caregiver.set_index("caregiver_no").loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no],
                                          similarity_workability.loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]], axis=1).sort_values(by=[0, "caregiver_career"], ascending=False)

    print(json.dumps({"data": {"caregivers": [i for i in result_caregiver.iloc[:top].index.to_list()]}}))
    return json.dumps({"data": {
                                   "caregivers": [i for i in result_caregiver]}})


if __name__ == "__main__":
    recommend_(10, 15, 1, "A")
