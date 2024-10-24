import json
from memory_bot_prompt import MEMORY_ANSWER_PROMPT, FACT_RETRIEVAL_PROMPT

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from langchain.memory import ConversationBufferMemory
import os


def get_fact_llm(user_input, api_key, openai_api_base):
    # 从用户的输入中提取事实、记忆和偏好，并用JSON格式输出

    # 创建prompt和模型并组成chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", FACT_RETRIEVAL_PROMPT),
        ("human", "{input}")
    ])
    model = ChatOpenAI(model="gpt-4o", api_key=api_key, openai_api_base=openai_api_base)
    chain = prompt | model
    # 执行chain
    response = chain.invoke({"input": user_input})
    return response.content


def add_json_file(facts):
    # 将LLM生成的偏好事实储存到json文件中
    # 输出一个包含所有记忆的字典

    # 创建或更新json文件
    filename = 'memory.json'
    try:
        # 读取现有数据
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        # 将新的事实添加到现有数据中
        existing_data['facts'].extend(facts['facts'])
        # 将更新后的数据写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        # 创建json文件并写入数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(facts, f, ensure_ascii=False, indent=4)
        existing_data = facts

    return existing_data


def chat_llm(user_input, history,  memory_str, api_key, openai_api_base):
    # 根据保存的偏好记忆回答用户提出的问题

    # 创建prompt和模型并组成chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", MEMORY_ANSWER_PROMPT+memory_str),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    model = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, openai_api_base=openai_api_base)
    chain = prompt | model
    # 执行chain
    response = chain.invoke({"input": user_input, "history": history}, )
    return response.content


def get_chat_response(user_input, history, api_key, openai_api_base):
    # 提取用户偏好并进行问答的完整bot

    # 从用户的输入里提取个性化信息
    facts_json = get_fact_llm(user_input, api_key, openai_api_base)

    # 判断是否从对话中提取出信息，如果提取出信息就进行储存
    # 提取出记忆数据
    facts = json.loads(facts_json)
    if len(facts["facts"]) != 0:
        memory = add_json_file(facts)
    else:
        filename = 'memory.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                memory = json.load(f)
        except FileNotFoundError:
            # 创建json文件并写入数据
            facts = {"facts": []}
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(facts, f, ensure_ascii=False, indent=4)
                memory = facts

    # 将提取出的记忆转换为字符串，将{转换为{{以免被识别为变量
    memory_str = str(memory).replace('{', '{{').replace('}', '}}')

    # 根据保存的偏好记忆回答用户提出的问题
    response = chat_llm(user_input, history, memory_str, api_key, openai_api_base)

    return response

'''
memory = ConversationBufferMemory(return_messages=True)
user_input = ("我喜欢吃甜食")
history = memory.buffer
response = get_chat_response(user_input, history, os.getenv("OPENAI_API_KEY"),
                  "https://api.aigc369.com/v1")

memory.save_context(
        {"input": user_input},
        {"output": response}
    )
print(response)
print(history)
'''