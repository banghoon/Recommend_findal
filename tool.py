import pandas as pd
import numpy as np
from sql_connect import get_sql
import datetime


def clip_group(x):
    if x == 0:
        return 0

    elif x <= 50:
        return .5

    elif x <= 100:
        return .75

    else:
        return 1


def clip_career(x):
    if x < 2:
        return 1

    else:
        return 2


def clip_rate(x):
    if x >= 4:
        return 1
    elif x >= 3:
        return .9
    elif x > 0:
        return 0.7
    else:
        return 1


def locale(x):
    try:
        locale = {
            "서울특별시": 16,
            "인천광역시": 15,
            "경기도": 9,
            "경상남도": 11,
            "부산광역시": 14,
            "전라남도": 18,
            "전라북도": 17,
        }
        return locale[x]
    except:
        return 0


def careable_work(x):
    res = np.zeros((x.shape[0], 6))
    for idx, i in enumerate(x.careable_work):
        for j in str(i).split(','):
            if j == "re":
                res[idx][0] = 1
            if j == "am":
                res[idx][1] = 1
            if j == "su":
                res[idx][2] = 1
            if j == "ch":
                res[idx][3] = 1
            if j == "ku":
                res[idx][4] = 1
            if j == "etc":
                res[idx][5] = 1
    return pd.DataFrame(res, columns=["re", "am", "su", "ch", "ku", "etc"], index=x.caregiver_no)


def load_data():  # rank 와 data 의 크기 차이 문제
    today = datetime.date.today()
    caregiver = get_sql('select * from tb_caregiver')
    care = get_sql('select * from tb_care')
    review = get_sql('select * from tb_review')

    caregiver.care_time_type = caregiver.care_time_type.fillna('01').replace("", "01")
    caregiver.caregiver_career = caregiver.caregiver_career.fillna(today.year).replace("", today.year)
    caregiver.caregiver_career = (today.year - caregiver.caregiver_career.astype('int64')).apply(clip_career)
    caregiver.work_ability = caregiver.work_ability.fillna(0).replace("", 0) ###############
    caregiver.community_ability = caregiver.community_ability.fillna(2).replace("", 2)
    caregiver.community_style = caregiver.community_style.fillna(1).replace("", 1)
    caregiver.smoking_yn = caregiver.smoking_yn.fillna('N')

    caregiver.group_re = caregiver.group_re.fillna(0)
    caregiver.group_am = caregiver.group_am.fillna(0)
    caregiver.group_ch = caregiver.group_ch.fillna(0)
    caregiver.group_su = caregiver.group_su.fillna(0)
    caregiver.group_ku = caregiver.group_ku.fillna(0)
    caregiver.group_etc = caregiver.group_etc.fillna(0)

    caregiver.group_re = caregiver.group_re.apply(clip_group)
    caregiver.group_am = caregiver.group_am.apply(clip_group)
    caregiver.group_ch = caregiver.group_ch.apply(clip_group)
    caregiver.group_su = caregiver.group_su.apply(clip_group)
    caregiver.group_ku = caregiver.group_ku.apply(clip_group)
    caregiver.group_etc = caregiver.group_etc.apply(clip_group)

    caregiver.rate_re = caregiver.rate_re.fillna(0).apply(clip_rate)
    caregiver.rate_am = caregiver.rate_am.fillna(0).apply(clip_rate)
    caregiver.rate_ch = caregiver.rate_ch.fillna(0).apply(clip_rate)
    caregiver.rate_su = caregiver.rate_su.fillna(0).apply(clip_rate)
    caregiver.rate_ku = caregiver.rate_ku.fillna(0).apply(clip_rate)
    caregiver.rate_etc = caregiver.rate_etc.fillna(0).apply(clip_rate)

    care.caregiver_no = care.caregiver_no.fillna(0).replace("", 0)   # 확인
    care.care_addr1 = care.care_addr1.fillna("대한민국").replace("", "대한민국")
    care["add"] = care.care_addr1.apply(lambda x: locale(x.split()[0]))

    # review
    review = review.merge(care[['care_no', 'user_no']], on='care_no', how='left')[['caregiver_no', 'user_no', 'review_point']]

    return care, caregiver, review


def pre_filtering(caregiver):
    caregiver_result = caregiver[['caregiver_career', 'community_ability', 'community_style',
                                  'group_re', 'group_am', 'group_ch', 'group_su', 'group_ku', 'group_etc', 'rate_re',
                                  'rate_am', 'rate_ch', 'rate_su', 'rate_ku', 'rate_etc']]

    d1 = caregiver_result[['group_re', 'group_am', 'group_ch', 'group_su', 'group_ku', 'group_etc']]
    d2 = caregiver_result[['rate_re', 'rate_am', 'rate_ch', 'rate_su', 'rate_ku', 'rate_etc']]
    d1.columns = [''] * 6
    d2.columns = [''] * 6
    processing_rate = d1*d2
    processing_rate.columns = ['new_re', 'new_am', 'new_ch', 'new_su', 'new_ku', 'new_etc']
    caregiver_result = pd.concat([caregiver_result, processing_rate], axis=1)
    caregiver_result = caregiver_result[['caregiver_career', 'community_ability', 'community_style',
                                         'new_re', 'new_am', 'new_ch', 'new_su', 'new_ku', 'new_etc']]
    caregiver_result.index = caregiver.index
    return caregiver_result


# 단순 필터링 코드
def simple_filtering(data, gender: bool, rating=None):
    # 흡연여부 N, 일일 간병 시간 01,
    # data.careable_locale.astype(str).apply(lambda x: ('9' in x))
    if (gender == 1) & (rating is not None):
        return data[(data.caregiver_gender == '1') & (data.caregiver_grade == rating)]

    elif (gender == 1) & (rating is None):
        return data[(data.caregiver_gender == '1')]

    elif (gender == 2) & (rating is not None):
        return data[(data.caregiver_gender == '2') & (data.caregiver_grade == rating)]

    elif (gender == 2) & (rating is None):
        return data[(data.caregiver_gender == '2')]

    elif (gender == 3) & (rating is not None):
        return data[(data.caregiver_grade == rating)]

    else:
        return data


def is_new(user_id, tb):
    if user_id not in tb:
        return True
    else:
        return False


def have_reviews(user_id, tb):
    if user_id in tb:
        return True
    else:
        return False
