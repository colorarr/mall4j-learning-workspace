from typing import TypeVar

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.intent import IntentResult

MODEL_NAME = settings.MODEL_NAME
BASE_URL = settings.BASE_URL
API_KEY = settings.API_KEY

StructuredSchema = TypeVar("StructuredSchema", bound=BaseModel)

def get_glm_model():
    llm = ChatOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_NAME,
    )

    return llm

def get_model_with_structured(schema: type[StructuredSchema]):
    """Return a model chain whose response is validated against ``schema``."""
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
你是一个结构化信息提取助手。
请根据用户输入完成指定任务，并严格按照输出 schema 返回结果。
只填写 schema 中定义的字段，不要增加额外字段，不要输出 Markdown、解释文字或代码块。
无法确定的字段使用 schema 允许的空值或默认值，不要猜测事实。
            """,
        ),
        ("user", "{input}"),
    ])
    llm = ChatOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_NAME,
    )
    llm_with_structured = llm.with_structured_output(
        schema,
        method="function_calling",
        strict=True,
    )

    return prompt | llm_with_structured


if __name__ == "__main__":
    chain = get_model_with_structured(IntentResult)

    result = chain.invoke({
        "input": "我想查询我的物流信息"
    })

    print(result)
