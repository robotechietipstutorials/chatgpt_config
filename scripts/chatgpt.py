import openai

# Set your OpenAI API key
api_key = 'your-api-key'
openai.api_key = api_key

def get_gpt3_response(prompt):

    response = openai.Completion.create(
        engine="text-davinci-002",  
        prompt=prompt,
        max_tokens=150  
    )
    
    return response.choices[0].text.strip()

# Example usage
user_prompt = "What is the difference between ROS1 and ROS2."
response = get_gpt3_response(user_prompt)
print("GPT-3.5 Response:", response)

