from openai import AzureOpenAI  # 注意导入方式变化
from openai import OpenAI
def ask_LLMmodel(input, prompt ,model_name = 'gpt4o'):
    if type(input) != str:
        input = str(input)
    if type(prompt) != str:
        prompt = str(prompt)
    if model_name == 'gpt4o':
        return askGPT(input, prompt)
    elif model_name == 'qwen':
        return askqwen(input, prompt)

    return "请输入正确的模型名称"
""" 
在下面添加调用模型的函数，并在上方函数添加elif分支
"""  


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


def askqwen(input, prompt):
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-f6b3d0960ade43c09e5d03d3676b6888",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",
        messages=[
            {"role": "system", "content": prompt },
            {"role": "user", "content": input },
        ],
        # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
        # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
        extra_body={"enable_thinking": False},
        temperature=0
    )
    # print(completion.model_dump_json())
    return completion.choices[0].message.content

if __name__ == "__main__":
    # 示例调用
    ans = ask_LLMmodel("What is the capital of China?", "You are a helpful assistant that answers questions about geography.",'qwen')
    print(ans)  # 输出模型的回答