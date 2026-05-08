from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os, textwrap, json
BASE=Path('/data/data/com.termux/files/home/jupiter-signal-lab')
OUT=BASE/'video_frames'
OUT.mkdir(exist_ok=True)
W,H=1280,720
font_paths=['/system/fonts/Roboto-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf']
font_path=next((p for p in font_paths if os.path.exists(p)), None)
def font(size): return ImageFont.truetype(font_path,size) if font_path else ImageFont.load_default()
F_TITLE=font(58); F_SUB=font(34); F_BODY=font(30); F_MONO=font(23); F_SMALL=font(24)
BG=(5,8,13); CYAN=(82,245,225); WHITE=(235,250,255); GRAY=(170,190,205); PINK=(255,72,145); GREEN=(80,230,160)

def bg():
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    for x in range(0,W,64): d.line((x,0,x,H), fill=(10,20,30), width=1)
    for y in range(0,H,64): d.line((0,y,W,y), fill=(10,20,30), width=1)
    d.rectangle((34,34,W-34,H-34), outline=(20,80,100), width=2)
    d.line((34,110,W-34,110), fill=(20,80,100), width=2)
    return im,d

def wrap_text(d, text, f, maxw):
    lines=[]
    for para in text.split('\n'):
        words=para.split(); line=''
        for w in words:
            test=(line+' '+w).strip()
            if d.textbbox((0,0),test,font=f)[2] <= maxw:
                line=test
            else:
                if line: lines.append(line)
                line=w
        if line: lines.append(line)
        if not words: lines.append('')
    return lines

def draw_lines(d, lines, x,y,f,fill=GRAY,lh=40):
    for ln in lines:
        d.text((x,y), ln, font=f, fill=fill)
        y+=lh
    return y

def save_slide(name,title,subtitle='',body='',code='',accent=PINK):
    im,d=bg()
    d.text((70,58), 'JUPITER SIGNAL LAB', font=F_SMALL, fill=CYAN)
    d.text((70,155), title, font=F_TITLE, fill=WHITE)
    if subtitle:
        draw_lines(d, wrap_text(d,subtitle,F_SUB,1080), 74,235,F_SUB,fill=CYAN,lh=44)
    if body:
        draw_lines(d, wrap_text(d,body,F_BODY,1080), 74,330,F_BODY,fill=GRAY,lh=42)
    if code:
        d.rounded_rectangle((70,210,1210,650), radius=18, fill=(2,6,10), outline=(50,120,140), width=2)
        y=232
        for line in code.splitlines()[:18]:
            color=CYAN if line.startswith('Jupiter') or line.startswith('Generated') else (205,225,230)
            d.text((96,y), line[:105], font=F_MONO, fill=color)
            y+=30
    d.rectangle((70,655,70+330,662), fill=accent)
    im.save(OUT/f'{name}.png')

cli=(BASE/'demo-cli-output.txt').read_text()
save_slide('demo_01','Read-only Solana intelligence','Built with Jupiter Tokens API V2 + Price API V3','A safe research layer for builders and agents before any wallet, signing, swap, or order execution.')
save_slide('demo_02','What the tool does','','Fetch top-trending and top-traded tokens. Deduplicate mints. Pull fresh prices. Rank tokens with explainable signals: liquidity, organic score, holder count, buy/sell pressure, momentum, and holder drift.', accent=CYAN)
save_slide('demo_03','Live CLI output',code=cli, accent=GREEN)
save_slide('demo_04','Why it matters','','Trending is not enough. Jupiter Signal Lab explains why a token looks interesting or risky, so agent workflows can start with research instead of unsafe execution.', accent=PINK)
save_slide('demo_05','Safety-first by design','','No wallet connection. No private keys. No transaction signing. No swaps. No automated trading. The current prototype is analysis-only and reproducible from the public repo.', accent=GREEN)

save_slide('pitch_01','Jupiter Signal Lab','Read-only intelligence for safer DeFi agents','Most token dashboards show movement without enough reasoning. For builders and AI agents, that is risky.', accent=CYAN)
save_slide('pitch_02','The problem','','A trending token should not automatically become an executed trade. Agents need transparent research, scoring, and human-readable reasons first.', accent=PINK)
save_slide('pitch_03','The solution','','We combine Jupiter Tokens API V2 and Price API V3 to rank Solana tokens with explainable signals, then show why each token looks interesting or risky.', accent=GREEN)
save_slide('pitch_04','Why us / why now','','We are approaching DeFi automation from a safety-first agent perspective. Before swaps or trigger orders, agents need a read-only research step.', accent=CYAN)
print(OUT)
