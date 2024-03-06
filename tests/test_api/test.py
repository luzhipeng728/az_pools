import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

def test():
    cookies = {
        '_ga': 'GA1.1.764944384.1708936219',
        '_ga_8PRS69JJRL': 'GS1.1.1708936218.1.1.1708936928.0.0.0',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    response = requests.get('http://localhost:8000/get-keys/', cookies=cookies, headers=headers)
    # 确保返回结果为JSON格式，并从中提取需要的信息
    return response.json()

num_requests = 500  # 请考虑服务器的负载能力来适配这个数值

key_indexes = []
import time  # 确保已经在文件顶部导入了time模块

start_time = time.time()  # 并发操作开始前的时间戳

with ThreadPoolExecutor(max_workers=min(20, num_requests)) as executor:
    future_to_index = {executor.submit(test): index for index in range(num_requests)}
    
    for future in as_completed(future_to_index):
        try:
            result = future.result()
            # print(result)
            # 假设result是一个字典格式，包含key_index
            key_indexes.append(result['key_index'])
        except Exception as exc:
            print(f'Request generated an exception: {exc}')

# 统计不同key_index的个数
key_index_counts = Counter(key_indexes)
end_time = time.time()  # 并发操作全部完成后的时间戳

total_time = end_time - start_time  # 总耗时，单位为秒

# 打印统计结果
for key_index, count in key_index_counts.items():
    print(f'key_index {key_index}: {count} times')
print(f'Total time taken: {total_time} seconds')