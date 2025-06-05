from langchain.llms import Ollama

llm = Ollama(model="mistral")

def summarize_logs(logs):
    joined_logs = "\n".join(logs[:20])
    prompt = f"Summarize the following application logs:\n{joined_logs}"
    return llm.invoke(prompt)
