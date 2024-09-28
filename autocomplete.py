import json 

with open("autocomplete.json", "r") as f:
    data = json.load(f)

obj = []

for el in data:    
    obj.append(el["name"])
    
with open("output.json", "w") as f:
    json.dump(obj, f, indent=4)