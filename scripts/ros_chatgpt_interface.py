#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
import openai
import json
openai.api_key = 'your-api-key'
from geometry_msgs.msg import Twist
import time
import copy
from geometry_msgs.msg import Pose
import math
x = 0.0
y  = 0.0
theta  = 0.0
pose = Pose()
from tf.transformations import euler_from_quaternion, quaternion_from_euler

def move(linear_speed, distance, is_forward): 
    if is_forward:
        direction = 'forward'
    else:
        direction = 'backward'
    print('Start moving the robot ', direction, ' at ', linear_speed, 'm/s and for a distance ', distance, 'meter')
    ###Write code to move robot###

def go_to_goal(location): 
    print("Going to Goal")
    ###Write code to go to goal###

def rotate (angular_speed_degree, desired_relative_angle_degree, clockwise):
    print('Start Rotating the Robot ...')
    twist_msg=Twist()
    angular_speed_degree=abs(angular_speed_degree) #make sure it is a positive relative angle
    ###Write code to rotate robot###

    
def askGPT(text_command):

    # Create the GPT-3 prompt with example inputs and desired outputs
    prompt = '''Consider the following ontology:
                {"action": "go_to_goal", "params": {"location": {"type": "str", "value": location}}}
                {"action": "move", "params": {"linear_speed": linear_speed, "distance": distance, "is_forward": is_forward}}
                {"action": "rotate", "params": {"angular_velocity": angular_velocity, "angle": angle, "is_clockwise": is_clockwise}}

                You will be given human language prompts, and you need to return a JSON conformant to the ontology. Any action not in the ontology must be ignored. Here are some examples.

                prompt: "Move forward for 1 meter at a speed of 0.5 meters per second."
                returns: {"action": "move", "params": {"linear_speed": 0.5, "distance": 1, "is_forward": true, "unit": "meter"}}

                prompt: "Rotate 60 degree in clockwise direction at 10 degrees per second and make pizza."
                returns: {"action": "rotate", "params": {"angular_velocity": 10, "angle": 60, "is_clockwise": true, "unit": "degrees"}}
                
                prompt: "go to the bedroom, rotate 
                 degrees and move 1 meter then stop"
                returns: {"action": "sequence", "params": [{"action": "go_to_goal", "params": {"location": {"type": "str", "value": "bedroom"}}}, {"action": "rotate", "params": {"angular_velocity": 30, "angle": 60, "is_clockwise": false, "unit": "degrees"}}, {"action": "move", "params": {"linear_speed": 1, "distance": 1, "is_forward": true, "unit": "meter"}}, {"action": "stop"}]}
                
                '''
    prompt = prompt+'\nprompt: '+text_command
    

    # Create the message structure for the GPT-3 model
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    # Try to send the request to the GPT-3 model and handle any exceptions
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
    except openai.error.InvalidRequestError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    
    # Extract the GPT-3 model response from the returned JSON
    chatgpt_response = response.choices[0].message['content'].strip()

    # Find the start and end indices of the JSON string in the response
    start_index = chatgpt_response.find('{')
    end_index = chatgpt_response.rfind('}') + 1
    # Extract the JSON string from the response
    json_response_dict = chatgpt_response[start_index:end_index]

    json_object = json.loads(json_response_dict)
    return json_object

def chatgpt_callback(data):
    query = data.data
    res = askGPT(query)
    print(res)
    main_action = res["action"]
    print(main_action)
    if(main_action == 'sequence'):
        i=0
        for i in range(len(res["params"])):
            print(res["params"][i])
            action = res["params"][i]["action"]
            if(action == 'go_to_goal'):
                location = res["params"][i]['params']['location']['value']
                print(location)
                go_to_goal(location)
            elif(action == 'move'):
                linear_speed = res["params"][i]['params'].get('linear_speed', 0.2)
                distance = res["params"][i]['params'].get('distance', 1.0)
                is_forward = res["params"][i]['params'].get('is_forward', True)
                move(linear_speed, distance, is_forward)
            elif action == 'rotate':
                angular_velocity = res["params"][i]['params'].get('angular_velocity', 1.0)
                angle = res["params"][i]['params'].get('angle', 90.0)
                is_clockwise = res["params"][i]['params'].get('is_clockwise', True)
                rotate(angular_velocity, angle, is_clockwise)
    elif(main_action == 'rotate'):
        rotate(res["params"]["angular_velocity"], res["params"]["angle"], res["params"]["is_clockwise"])
    else:
        move(res["params"]["linear_speed"], res["params"]["distance"], res["params"]["is_forward"])
    
def listener():

    rospy.init_node('chatgpt', anonymous=True)

    rospy.Subscriber("query", String, chatgpt_callback)
    
    rospy.spin()

if __name__ == '__main__':
    listener()

