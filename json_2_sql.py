import json

# 设置输入和输出文件的名称
input_json_file = 'fast.json'
output_sql_file = 'output.sql'

# 开始处理
try:
    # 从 JSON 文件中读取数据
    with open(input_json_file, 'r') as file:
        records = json.load(file)

    # 准备 SQL 插入语句的开始部分
    insert_query = "INSERT INTO az_keys (resourceName, key, status, addTime, is_in_use) VALUES\n"

    # 为每条记录生成对应的值字符串
    values_list = []
    for record in records:
        resourceName = record['resourceName']
        key = record['key']
        status = record['status']
        addTime = record['addTime']
        is_in_use = record['is_in_use']
        values_str = f"('{resourceName}', '{key}', '{status}', '{addTime}', {is_in_use>0})"
        values_list.append(values_str)

    # 将所有记录的值连接成一条完整的 SQL 语句
    insert_query += ",\n".join(values_list) + ";"

    # 将生成的 SQL 语句写入输出文件
    with open(output_sql_file, 'w') as file:
        file.write(insert_query)

    print(f"SQL 插入语句已经成功生成并保存到 {output_sql_file}")
except Exception as e:
    print(f"处理过程中发生错误：{e}")
