import pandas as pd
import hybrid
import tool
import model
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def recommend(user_no, top, caregiver_gender, caregiver_grade):  # 단순 필터링 요소 추가 해야함
    care, caregiver, review = tool.load_data()
    if tool.is_new(user_no, care.user_no.to_list()):  # 신규 고객
        result = caregiver.set_index("caregiver_no").loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]
        result['work_list'] = result.work_ability.astype(str).apply(lambda x: len(x.split(',')))
        result['work_day'] = result[['group_re', 'group_am', 'group_ch', 'group_su', 'group_ku', 'group_etc']].sum(axis=1)
        result['attr_'] = result.careable_locale.astype(str).apply(lambda x: x)
        result_caregiver = result.sort_values(by=['work_day', 'caregiver_career', 'work_list'], ascending=False)[:top].index.to_list()

    else:  # 기존 유저
        length = len(care[(care.user_no == user_no) & (care.caregiver_no > 0)].caregiver_no.values)
        print(care[(care.user_no == user_no) & (care.caregiver_no > 0)].caregiver_no.values[np.random.randint(length)])  # 기존 사용 간병인 번호
        # 리뷰가 존재
        if tool.have_reviews(user_no, review.user_no.to_list()):
            result = hybrid.hybrid(caregiver, review, user_no)
            if result.shape[0] == 1:
                # 성별 확인, 현재 Boolean 으로 구분
                result = result.T.loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]
            elif result.shape[0] == 0:
                return json.dumps({"data": {
                                   "caregivers": ['']}})
            else:
                result = result.loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]
        else:
            # 리뷰가 존재 X -> rule based(우선 순위 기준)
            pass
        result_caregiver = pd.concat([result, caregiver.set_index("caregiver_no").loc[tool.simple_filtering(caregiver, caregiver_gender, caregiver_grade).caregiver_no]], axis=1)

    print(json.dumps({"data": {"caregivers": [i for i in result_caregiver]}}))
    return json.dumps({"data": {
                                   "caregivers": [i for i in result_caregiver]}})


if __name__ == "__main__":
    simple_ = {"caregiver_gender": True, "caregiver_grade": "A"}
    recommend(2, top=5, **simple_)
