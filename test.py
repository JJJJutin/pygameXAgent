import openai
from dotenv import load_dotenv
import os

load_dotenv()

# 確保 API 金鑰正確載入
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("未找到 OPENAI_API_KEY，請檢查環境變數設定。")

openai.api_key = api_key

# 發送請求至 OpenAI API
response = openai.completions.create(
    model="gpt-4",
    prompt="You are a coding assistant that talks like a pirate.\nUser: "
    + input("你: ")
    + "\nAssistant:",
    max_tokens=150,
)

# 輸出回應
print(response["choices"][0]["text"].strip())
# 輸出回應
print(response["choices"][0]["message"]["content"])
