from PIL import Image, ImageDraw, ImageFont
import math, os
W=1200; H=1200
img=Image.new('RGB',(W,H),(5,8,13))
d=ImageDraw.Draw(img)
for x in range(0,W,60):
    col=(10,20,30) if x%120 else (14,30,44)
    d.line((x,0,x,H), fill=col, width=1)
for y in range(0,H,60):
    col=(10,20,30) if y%120 else (14,30,44)
    d.line((0,y,W,y), fill=col, width=1)
cx,cy=W//2,H//2
for r in range(520,60,-8):
    alpha=(520-r)/520
    col=(int(5+alpha*8), int(8+alpha*44), int(13+alpha*54))
    d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=col, width=8)
for r, color, w in [(430,(18,150,165),4),(330,(80,220,210),3),(235,(35,90,160),3)]:
    d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=color, width=w)
nodes=[]
for i in range(12):
    ang=math.tau*i/12 - .3
    r=330 if i%2 else 430
    x=cx+math.cos(ang)*r; y=cy+math.sin(ang)*r
    nodes.append((x,y))
    d.ellipse((x-18,y-18,x+18,y+18), fill=(8,18,28), outline=(78,230,215), width=4)
for i in range(len(nodes)):
    x1,y1=nodes[i]; x2,y2=nodes[(i+3)%len(nodes)]
    d.line((x1,y1,x2,y2), fill=(18,80,105), width=2)
pts=[]
for i in range(6):
    a=math.tau*i/6+math.pi/6
    pts.append((cx+math.cos(a)*185, cy+math.sin(a)*185))
d.polygon(pts, fill=(8,24,36), outline=(75,235,220))
for off in [0,22,44]:
    pts2=[]
    for i in range(6):
        a=math.tau*i/6+math.pi/6
        pts2.append((cx+math.cos(a)*(185-off), cy+math.sin(a)*(185-off)))
    d.line(pts2+[pts2[0]], fill=(22,92,120), width=2)
bars=[80,130,55,160,105]
start=cx-115
for i,b in enumerate(bars):
    x=start+i*55
    d.rounded_rectangle((x,cy+105-b,x+30,cy+105), radius=8, fill=(37,210,190), outline=(140,255,235), width=2)
line=[]
for i,b in enumerate([70,40,88,55,115,80,145]):
    x=cx-145+i*48; y=cy+80-b
    line.append((x,y))
d.line(line, fill=(255,72,145), width=8)
for x,y in line:
    d.ellipse((x-8,y-8,x+8,y+8), fill=(255,72,145))
font_paths=['/system/fonts/Roboto-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf']
font_path=next((p for p in font_paths if os.path.exists(p)), None)
font_big=ImageFont.truetype(font_path,76) if font_path else ImageFont.load_default()
font_med=ImageFont.truetype(font_path,34) if font_path else ImageFont.load_default()
for text, y, font, fill in [('JUPITER', 110, font_big, (235,250,255)), ('SIGNAL LAB', 196, font_big, (82,245,225)), ('Read-only token intelligence', 985, font_med, (185,205,215))]:
    bbox=d.textbbox((0,0), text, font=font)
    d.text(((W-(bbox[2]-bbox[0]))/2,y), text, font=font, fill=fill)
accent=(82,245,225)
for sx,sy in [(80,80),(1120,80),(80,1120),(1120,1120)]:
    s=1 if sx<600 else -1; t=1 if sy<600 else -1
    d.line((sx,sy,sx+120*s,sy),fill=accent,width=8)
    d.line((sx,sy,sx,sy+120*t),fill=accent,width=8)
path='/data/data/com.termux/files/home/jupiter-signal-lab/project-logo.png'
img.save(path, optimize=True)
print(path)
print(os.path.getsize(path))
