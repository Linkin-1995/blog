# 原始数据
s = [
    {'name': 'leader-2', 'belong_to': None},
    {'name': 'Jack', 'belong_to': 'leader-2'},
    {'name': 'leader-1', 'belong_to': None},
    {'name': 'lili', 'belong_to': 'leader-1'},
    {'name': 'tom', 'belong_to': 'leader-1'},
]
# 目标数据
d = [
    {'name': 'leader-1', 'team': [{'name': 'lili'}, {'name': 'tom'}]},
    {'name': 'leader-2', 'team': [{'name': 'Jack'}]},
]

#将 belong_to分成两类进行操作

def find_team(s):
    leader_data = []
    m_dict={}
    for item in s:
        if item['belong_to'] == None:
            # 分队
            leader_data.append({'name':item['name'],'team':[]})
        else:
            # 队员
            #键不存在，添加键值对;键存在，不做任何操作
            m_dict.setdefault(item['belong_to'],[])
            #在值添加中键
            m_dict[item['belong_to']].append({'name':item['name']})

    for l in leader_data:
        if l["name"] in m_dict:
            l["team"]=m_dict[l['name']]

    return leader_data


if __name__ == "__main__":
    print(find_team(s))
