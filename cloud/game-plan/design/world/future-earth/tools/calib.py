# Fit FMG's world.png to Natural Earth land as Web Mercator; prints (IoU, x0, k, y0, projection) for make_heightmap.py
# Usage: python3 calib.py world.png ne_50m_land.geojson
import json, sys, numpy as np
from PIL import Image, ImageDraw
a=np.array(Image.open(sys.argv[1])).astype(int); H,W=a.shape
land=a>=51
polys=[]
for f in json.load(open(sys.argv[2]))['features']:
    g=f['geometry']; cs=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for p in cs:
        if len(p[0])>80: polys.append(np.array(p[0])[::4])
def merc(lat): lat=np.clip(lat,-85,85); return np.log(np.tan(np.pi/4+np.radians(lat)/2))
def render(x0,k,y0,proj):
    im=Image.new('L',(W,H)); d=ImageDraw.Draw(im)
    for p in polys:
        x=x0+k*np.radians(p[:,0]); y=y0-k*(merc(p[:,1]) if proj=='m' else np.radians(p[:,1]))
        d.polygon(list(zip(x,y)),fill=1)
    return np.array(im)>0
def iou(m): return (m&land).sum()/(m|land).sum()
best=(0,)
for proj in 'me':
  for k in np.arange(84,126,4):
    for x0 in np.arange(W/2-60,W/2+60,8):
      for y0 in np.arange(90,230,8):
        s=iou(render(x0,k,y0,proj))
        if s>best[0]: best=(s,x0,k,y0,proj)
  print(proj,best,flush=True)
s,x0,k,y0,proj=best
for step in (2,1,.5):
  for dk in (-step,0,step):
    for dx in (-step,0,step):
      for dy in (-step,0,step):
        v=iou(render(x0+dx,k+dk,y0+dy,proj))
        if v>best[0]: best=(v,x0+dx,k+dk,y0+dy,proj)
  s,x0,k,y0,proj=best
print(best)
