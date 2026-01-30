from openai import OpenAI
from markrender import MarkdownRenderer


renderer = MarkdownRenderer()
client = OpenAI(base_url="https://api.groq.com/openai/v1/", api_key='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')

stream = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
    {
        "role": "system",
        "content": "You are a highly capable AI assistant that answers clearly and concisely."
    },
    {
        "role": "user",
        "content": "Give me those 1 - 10 emojis using markdown?"
    }
    ],
    stream=True
)
for chunk in stream:
    chu = chunk.choices[0].delta.content
    if chu: 
        renderer.render(chu)

renderer.finalize()