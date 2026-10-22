import json, os, subprocess, time, urllib.request, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if not Path(FONT).exists():
    import glob
    matches=glob.glob("/usr/share/fonts/**/*NotoSansCJK*.ttc",recursive=True)
    if not matches: raise RuntimeError("Japanese font not installed")
    FONT=matches[0]
def req(path, data=None):
    url="http://127.0.0.1:50021"+path
    request=urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"} if data is not None else {},method="POST" if data is not None else "GET")
    with urllib.request.urlopen(request, timeout=120) as r:return r.read()
def wrap(draw,text,font,maxwidth):
    lines=[]
    for paragraph in text.split("\n"):
        current=""
        for ch in paragraph:
            if draw.textbbox((0,0),current+ch,font=font)[2]>maxwidth and current:
                lines.append(current);current=ch
            else:current+=ch
        lines.append(current)
    return lines
def slide(i,role,text):
    im=Image.new("RGB",(1280,720),(245,248,252))
    d=ImageDraw.Draw(im)
    accent=(216,83,124) if role=="女性（質問）" else (48,91,156)
    d.rounded_rectangle((65,55,1215,665),radius=35,fill="white",outline=(215,225,238),width=4)
    d.rounded_rectangle((95,92,1185,190),radius=20,fill=accent)
    titlefont=ImageFont.truetype(FONT,44)
    bodyfont=ImageFont.truetype(FONT,49)
    d.text((130,107),role,font=titlefont,fill="white")
    lines=wrap(d,text,bodyfont,990)
    if len(lines)>6:raise ValueError("Too much text for one slide; split into shorter turns")
    y=235
    for line in lines:
        d.text((130,y),line,font=bodyfont,fill=(34,44,61));y+=70
    d.text((104,626),"介護福祉士試験対策ラジオ  |  無料テスト版",font=ImageFont.truetype(FONT,22),fill=(110,120,130))
    dest=OUT/f"slide_{i:03}.png";im.save(dest);return dest
def main():
    dialogue=json.loads((ROOT/"dialogue.json").read_text(encoding="utf-8"))
    if not isinstance(dialogue,list) or not dialogue:raise ValueError("dialogue.json must be a nonempty list")
    concat=[]
    for i,turn in enumerate(dialogue):
        role=turn["role"];text=turn["text"]
        if role not in ("女性（質問）","男性（解説）"):raise ValueError("Unknown role: "+role)
        speaker=2 if role=="女性（質問）" else 3
        query=req("/audio_query?"+urllib.parse.urlencode({"text":text,"speaker":speaker}),b"")
        wav=req("/synthesis?"+urllib.parse.urlencode({"speaker":speaker}),query)
        audio=OUT/f"voice_{i:03}.wav";audio.write_bytes(wav)
        img=slide(i,role,text)
        clip=OUT/f"clip_{i:03}.mp4"
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","25","-i",str(img),"-i",str(audio),"-c:v","libx264","-preset","ultrafast","-tune","stillimage","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(clip)],check=True)
        concat.append(f"file '{clip.name}'")
    playlist=OUT/"concat.txt";playlist.write_text("\n".join(concat)+"\n")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(playlist),"-c","copy",str(OUT/"care_radio.mp4")],check=True)
    print("CREATED",OUT/"care_radio.mp4")
if __name__=="__main__":main()
