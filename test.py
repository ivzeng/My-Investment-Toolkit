from os import path as osp
import json
    

if not osp.exists("test1.json"):
    jf = open("test1.json", "w+")
    jf.write("{}")
    jf.close()
jf = open("test1.json", "r")
jd = json.load(jf)
print(jd)
jf.close()