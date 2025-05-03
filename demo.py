import os
import json
import sys
import subprocess
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(
	base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
	api_key=os.environ["GEMINI_API_KEY"]
)

class Item(BaseModel):
	name: str
	x: int
	y: int

class Output(BaseModel):
	data: list[Item]

# TODO don't hardcode the level type (currently 3d)
system_prompt="""
You make mario levels. You return json in the format `item: [{name: "", x: 0, y: 0}]`.
YOU MUST RETURN MORE THAN TEN (10) OBJECTS. Make sure your choices are diverse.
You can use x values between 5 and 15, and y values between 3 and 9. "x" starts at left, "y" starts at top.
You do not need to make the ground.
Your available names are listed below:
[
    'Ground', 'Steep Slope', 'Gentle Slope', 'Pipe', 'Clear Pipe', 'Spike Block', 'Semisolid Platform',
    'Block', '? Block', 'Hard Block', 'Hidden Block', 'Donut Block', 'Note Block', 'Cloud Block', 'Ice Block',
    'Coin', '10-Coin', 'Pink Coin', cc'Super Mushroom', 'Super Bell', 'Fire Flower', 'Super Star', '1-Up Mushroom',
    'Goomba', 'Koopa Troopa', 'Ant Trooper', 'Spiny', 'Spiny', 'Blooper', 'Cheep Cheep',
    'Skipsqueak', 'Stingbyc', 'Piranha Plant', 'Pirahna Creeper', 'Thwomp', 'Hammer Bro', 'Hop-Chops',
    'Boo', 'Lava Bubble', 'Bob-omb', 'Dry Bones', 'Fish Bone', 'Magikoopa',
    'Meowser', 'Boom Boom', 'Charvaargh', 'Bully', 'Porcupuffer', 'Koopa Troopa Car',
    'Bill Blaster', 'Banzai Bill', 'Icicle', 'Twister', 'ON/OFF Switch', 'Conveyor Belt', 'Crate',
    'Key', 'Warp Door', 'Warp Box', 'P Switch', 'POW Block', 'Trampoline', 'Arrow Sign', 'Checkpoint Flag',
    'Cloud Lift', '! Block', 'Snake Block', 'Blinking Block', 'Track Block', 'Tree', 'Mushroom Trampoline'
]
"""

prompt=""
resp = client.beta.chat.completions.parse(
	model="gemini-2.0-flash",
	messages=[
		{"role": "system", "content": system_prompt},
		{"role": "user", "content": sys.argv[0]}
	],
	response_format=Output
)

data = resp.choices[0].message.parsed
print(data)

new_data = []
x = data.data
for item in x:
	print("item =", item)
	new_data.append({"name": item.name, "x": item.x, "y": item.y})

with open("x.json", 'w') as f:
	json.dump(new_data, f)

subprocess.run(["python", "ctl.py"])