import pandas as pd
import numpy as np
import json
def get_scenario_info(df,scenario_related_func)  -> pd.DataFrame:
    df = df.replace(np.nan, None)
    all_scenario_info = pd.DataFrame(columns=df.columns)
    # 遍历DataFrame的每一行
    # 如果这一行与scenario相关，则将其加入到all_scenario_info表中
    # 遍历DataFrame的每一行
    for index,row in df.iterrows():
        if scenario_related_func(row):
            # 把这一行加入到 all_scenario_info表中，concat方法
            row_df = row.to_frame().T
            all_scenario_info = pd.concat([all_scenario_info, row_df], ignore_index=True)
    return all_scenario_info