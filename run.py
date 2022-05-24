import pandas as pd
import hybrid
import tool
import sql_connect
import model
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def main():  # 단순 필터링 요소 입력, 유저 번호
    # 사용 csv 파일(테이블)
    care, caregiver, review = tool.load_data()
    arg = hybrid.define_args()

    if tool.is_new(arg.user, care.user_no.to_list()):  # content based
        result = {"recommend_{1}": "New"}

    else:

        if tool.have_reviews(arg.user, review.user_no.to_list()):
            result = hybrid.hybrid(caregiver, review, arg)
            if result.shape[0] == 1:
                result = result.T.loc[tool.simple_filtering(caregiver, True, "B").caregiver_no]
            elif result.shape[0] == 0:
                result = {"recommend_{1}": None}
                return json.dumps(result)
            else:
                result = result.loc[tool.simple_filtering(caregiver, True, "B").caregiver_no]
            print(result)
            res = pd.concat([result.squeeze().sort_values(ascending=False), caregiver.set_index('caregiver_no').loc[result.squeeze().sort_values(ascending=False).index.tolist()]], axis=1).sort_values(by=[7, 'caregiver_career'])

            # try:
            #     res = []
            #     for a in result.squeeze().sort_values(ascending=False).index.tolist()[:arg.top+5]:
            #         res.append(a)
            #     result = {f"recommend_{i+1}": caregiver_number for i, caregiver_number in enumerate(res[:arg.top])}
            # except(TypeError, AttributeError):
            #     result = {"recommend_{1}": None}

        else:
            num = care[care.user_no == arg.user].caregiver_no.iloc[0]
            sim_metrix = cosine_similarity(tool.pre_filtering(caregiver),
                                           np.array(tool.pre_filtering(caregiver).loc[num]).reshape(1, -1))
            random_idx = np.random.randint(0, 10, 5)
            sim_df = pd.DataFrame(sim_metrix, index=caregiver.caregiver_no)
            sorted_sim_df = sim_df.sort_values(by=0, ascending=False)[:20].iloc[random_idx].index
            result = {f"recommend_{i}": caregiver_id for i, caregiver_id in enumerate(sorted_sim_df)}
    return json.dumps(result)


if __name__ == "__main__":
    main()

