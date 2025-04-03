import google.generativeai as genai
# from google import genai
from openai import OpenAI
import openai
import time

def call_llm(conversation_history,model_name, temperature):

    try:
        client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key="",
        )


        completion = client.chat.completions.create(
            model=model_name,
            messages=conversation_history,
            temperature=temperature,
        )

        model_output = completion.choices[0].message.content

        conversation_history.append({
            "role": "system",
            "content": model_output
        })
        # print(model_output)
        return model_output

    except openai.RateLimitError as e:
        retry_time = 60
        print(f"Rate limit exceeded. Retrying in {retry_time} seconds...")
        time.sleep(retry_time)
        return call_llm(conversation_history,model_name, temperature)

    except OSError as e:
        retry_time = 30  # Adjust the retry time as needed
        print(
        f"Connection error occurred: {e}. Retrying in {retry_time} seconds..."
        )
        time.sleep(retry_time)
        return call_llm(conversation_history,model_name, temperature)
    except Exception as e:
        print(f"{e}")
        retry_time = int(input("Retry time (seconds): "))
        print(f"Retrying in {retry_time} seconds...")
        time.sleep(retry_time)
        return call_llm(conversation_history,model_name, temperature)