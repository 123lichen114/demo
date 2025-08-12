from openai import AzureOpenAI  # 注意导入方式变化

def askGPT(input, prompt):
    q = str(input)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": q}
    ]
    
    # 配置Azure客户端
    client = AzureOpenAI(
        api_key='d2ca2cab8f0f46da891dec75ae8b38ec',  # 替换为你的API Key
        api_version="2023-05-15",
        azure_endpoint='https://coe0522.openai.azure.com/'  # 注意：去掉URL末尾空格
    )
    
    # 调用GPT-4o模型
    response = client.chat.completions.create(
        model="gpt-4o",  # 直接使用model参数指定部署名
        messages=messages,
        temperature=0
    )
    
    return response.choices[0].message.content  # 访问响应的新方式


# 测试
prompt = "你是一个专业的Python工程师，请根据用户输入的问题，生成一段Python代码。"
input = "请帮我写一个函数，用于计算两个数的和。"
print(askGPT(input, prompt))