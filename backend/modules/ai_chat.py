# modules/ai_chat.py

import subprocess
import time

def chat_with_ai(user_input: str) -> str:
    try:
        start_time = time.time()

        # Run Gemma 2B locally with Ollama
        process = subprocess.Popen(
            ["ollama", "run", "gemma:2b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, _ = process.communicate(user_input)

        end_time = time.time()
        print(f"⏱️ Time taken: {end_time - start_time:.2f} seconds")

        return output.strip() if output else "❌ No response from Gemma."

    except Exception as e:
        return f"❌ Local model error: {str(e)}"















# online API 


# #import think 
# '''
# requests     : For making  HTTP requests
# time         : To measure response time 
# os           : For accessing environment variables
# load_dotenv  : For loading . env file
# '''
# # modules/ai_chat.py

# import requests
# import time
# import os
# from dotenv import load_dotenv
# from typing import List,Dict,Any,Optional

# load_dotenv() #load API key from . env file 

# API_URL = "https://openrouter.ai/api/v1/chat/completions"
# API_KEY =   os.getenv("API_KEY")      #Get API key 


# def chat_with_ai(user_input : str) -> str:
#     try:

#         # Measures the time it take ( TEST )
#         start_time = time.time()


#         response = requests.post(
#             API_URL,
#             headers={
#                 "Authorization": f"Bearer {API_KEY}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "deepseek/deepseek-r1:free",              #AI Model
#                 "messages": [{"role": "user", "content": user_input}],  #Prompt
#                 "temperature": 0.53                                     # Controls randomness (0.53 = balanced)
#             }
#         )
#         response.raise_for_status()   #  Raises error for bad HTTP status
#         result = response.json()      #  Converts response to Python dict 

#         # Check if respone contains vaild data   
#         if "choices" not in result or not result["choices"]:
#             return "❌ Response error: No choices in response."

#         reply = result["choices"][0].get("message", {}).get("content")
#         if not reply:
#             return "❌ Response error: No content in message."
        
#         # Check how long it take (TEST)
#         end_time=time.time()
#         print(f"⏱️ Time taken: {end_time - start_time:.2f} seconds")
        
#         return reply.strip()
    
#     # Error Handling
    
#     # No internet , wrong API URL   
#     except requests.exceptions.RequestException as e:
#         return f"❌ API request failed: {str(e)}"
    
#     # Malformed JSON response 
#     except ValueError as e:
#         return f"❌ JSON decode error: {str(e)}"
    
#     # Any other unexpexted error 
#     except Exception as e:
#         return f"❌ Unexpected error: {str(e)}"
