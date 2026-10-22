import json, urllib.request, urllib.parse, pathlib, wave, subprocess
p=pathlib.Path("voice_samples");p.mkdir(exist_ok=True)
def post(url,data):
 with urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:50021"+url,data=data,headers={"Content-Type":"application/json"}),timeout=120) as r:return r.read()
samples=[("rin_original",2,"こんにちは！これから一緒に、介護福祉士の試験対策を始めましょう。"),("sato_a",11,"このチャンネルでは、試験に役立つ知識を、わかりやすく解説していきます。"),("sato_b",13,"このチャンネルでは、試験に役立つ知識を、わかりやすく解説していきます。"),("sato_c",21,"このチャンネルでは、試験に役立つ知識を、わかりやすく解説していきます。")]
for name,speaker,text in samples:
 q=json.loads(post("/audio_query?"+urllib.parse.urlencode({"speaker":speaker,"text":text}),b"").decode())
 q["speedScale"]=1.08
 if name=="sato_b":q["pitchScale"]=0.08
 wav=post("/synthesis?"+urllib.parse.urlencode({"speaker":speaker}),json.dumps(q).encode())
 (p/(name+".wav")).write_bytes(wav)
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(p/(name+".wav")),"-c:a","libmp3lame","-q:a","3",str(p/(name+".mp3"))],check=True)
print("done")
