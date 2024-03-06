from openai import AsyncAzureOpenAI
import asyncio

async def request_azure(resourcename, key):
    try:
        async with AsyncAzureOpenAI(
            api_version="2023-07-01-preview",
            azure_endpoint=f"https://{resourcename}.openai.azure.com",
            api_key=key
        ) as client:
            completion = await client.models.list()
    except Exception as e:
        if 'Unauthorized' in str(e):
            print('Unauthorized')
            
        

# 替换 YOUR_RESOURCE_NAME 和 YOUR_KEY 为你的Azure资源名称和密钥
resourcename = "0233-in"
key = "d320664941784092b134afcd695b4de3"

# 运行异步函数
loop = asyncio.get_event_loop()
loop.run_until_complete(request_azure(resourcename, key))