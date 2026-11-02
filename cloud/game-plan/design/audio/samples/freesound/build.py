import json,subprocess,os
B='/mnt/project-files/game-plan/design/audio/samples/freesound'
S=json.load(open(B+'/sources.json'))
os.makedirs(B+'/sfx',exist_ok=True);os.makedirs(B+'/ambience',exist_ok=True);os.makedirs(B+'/music',exist_ok=True)
# layer: (key, delay_s, gain_db, opts) opts: p=pitch ratio, t=trim s, f=extra filter, loop=bool
R={
'sfx/sword_light':(1.4,[('whoosh',0,0,{}),('sword_clash',.12,0,{}),('flesh_hit',.13,-10,{'f':'lowpass=f=3000','t':.6})]),
'sfx/greathammer_slam':(2.6,[('heavy_whoosh',0,0,{}),('anvil',.45,-2,{'p':.7}),('debris',.45,-3,{}),('boom',.44,-3,{'f':'lowpass=f=220','t':2})]),
'sfx/meridian_rifle':(1.6,[('gunshot',0,0,{'t':1.4}),('zap',0,-8,{'f':'highpass=f=2000'}),('bolt',.55,-6,{})]),
'sfx/shard_cast_bloom':(3.2,[('whoosh',0,-8,{'f':'areverse'}),('glass_ring',.2,-2,{'t':3}),('choir',.35,-12,{'f':'lowpass=f=3000','t':2.6})]),
'sfx/ward_break':(2.2,[('glass_shatter',0,0,{}),('electric_crackle',0,-6,{'t':1.5}),('boom',0,-12,{'f':'lowpass=f=180','t':1.5})]),
'sfx/ember_spell':(2.2,[('fire_whoosh',0,0,{}),('anvil',.3,-6,{'p':.8}),('amb_ash',0,-6,{'t':1.8})]),
'sfx/frost_spell':(2.6,[('cold_wind',0,-8,{'t':2.2}),('ice_crack',.4,0,{}),('glass_ring',.4,-14,{'p':1.5,'t':2})]),
'sfx/storm_spell':(3.5,[('zap',0,0,{}),('electric_crackle',.1,-4,{'t':1.5}),('thunder',.35,-3,{'t':3})]),
'sfx/ember_pickup':(1.6,[('heartbeat',0,-2,{'t':1.3}),('coins',0,-6,{'t':1.5})]),
'sfx/enemy_hollowed':(3.2,[('growl',0,0,{'p':.82}),('wet_breath',.3,-4,{'t':2.6})]),
'sfx/enemy_remnant_drone':(2.4,[('servo',0,0,{}),('robot_beep',.4,-6,{'t':1.2}),('zap',1.0,-10,{})]),
'sfx/enemy_thorn_raider':(2.4,[('growl',0,0,{'p':1.12}),('bone_rattle',.2,0,{}),('heavy_whoosh',.35,-4,{})]),
'sfx/boss_roar':(4.0,[('monster_roar',0,0,{}),('rumble',0,-2,{'p':.6,'loop':1,'t':3}),('boom',.2,-6,{'f':'lowpass=f=200','t':3})]),
'sfx/hush_voice':(5.0,[('whisper',0,0,{'t':4.6}),('whisper',.037,-2,{'p':1.02,'t':4.6}),('choir',0,-16,{'f':'lowpass=f=1500','p':.89,'t':4.6})]),
}
A=45
def bed(*l): return (A,[(k,d,g,dict(o,loop=1)) for k,d,g,o in l])
R.update({
'ambience/REG_01_cinderreach':bed(('amb_ash',0,0,{}),('amb_forge',0,-12,{'f':'lowpass=f=1500,aecho=0.8:0.6:300:0.4'}),('cold_wind',0,-16,{'f':'highpass=f=4000'})),
'ambience/REG_02_saltmere':bed(('amb_surf',0,0,{}),('amb_gulls',0,-8,{}),('amb_bells',0,-18,{})),
'ambience/REG_03_thornwood':bed(('amb_forest',0,0,{}),('amb_frogs',0,-6,{}),('mus_drums',0,-22,{'f':'lowpass=f=300'})),
'ambience/REG_04_glasswaste':bed(('amb_desert_wind',0,0,{}),('glass_ring',0,-18,{'f':'aecho=0.8:0.7:500:0.5'}),('servo',0,-24,{'f':'lowpass=f=2500'})),
'ambience/REG_05_rimefall':bed(('amb_snow',0,-2,{}),('amb_wolves',12,-12,{'f':'aecho=0.8:0.7:700:0.4'}),('ice_crack',25,-10,{})),
'ambience/REG_06_hollowdeep':bed(('amb_cave',0,0,{}),('amb_machine',0,-14,{'f':'lowpass=f=200'}),('growl',20,-18,{'p':.7,'f':'aecho=0.8:0.8:900:0.5'})),
'ambience/REG_Q_the_quiet':bed(('amb_ship',0,0,{}),('amb_alarm',0,-20,{'f':'lowpass=f=1200'}),('whisper',0,-16,{})),
'ambience/REG_U_undervault':bed(('amb_machine',0,0,{}),('amb_steam',0,-6,{}),('robot_beep',0,-16,{})),
'ambience/REG_HUB_lantern_hold':bed(('amb_market',0,0,{}),('amb_bells',0,-12,{}),('amb_forge',0,-14,{})),
})
M=60
def mus(*l): return (M,[(k,d,g,dict(o,loop=1)) for k,d,g,o in l])
R.update({
'music/explore_bed':mus(('mus_drone',0,0,{}),('mus_pad',0,-6,{}),('mus_bowed_metal',0,-10,{})),
'music/combat_bed':mus(('mus_taiko',0,0,{}),('mus_strings',0,-3,{}),('mus_brass',8,-8,{}),('mus_brass',24,-8,{}),('mus_brass',40,-8,{})),
'music/boss_bed':mus(('mus_strings',0,0,{}),('mus_drums',0,-2,{}),('mus_choir_pad',0,-4,{}),('boom',16,-6,{'f':'lowpass=f=200'}),('boom',32,-6,{'f':'lowpass=f=200'}),('mus_brass',48,-4,{})),
'music/hush_bed':mus(('mus_drone',0,-2,{'p':.94}),('whisper',0,-10,{}),('mus_choir_pad',0,-8,{'p':.89})),
})
# one-shot brass/boom in beds should not loop
for k,(d,ls) in R.items():
    R[k]=(d,[(a,b,c,{**o,'loop':0} if a in('mus_brass','boom') and o.get('loop') else o) for a,b,c,o in ls])
for out,(dur,ls) in R.items():
    cmd=['ffmpeg','-y','-loglevel','error'];fc=[]
    for i,(k,d,g,o) in enumerate(ls):
        if o.get('loop'): cmd+=['-stream_loop','-1']
        cmd+=['-i',S[k]['file']]
        ch=f'[{i}]aformat=channel_layouts=stereo,aresample=48000'
        if 'p' in o: ch+=f",asetrate={int(48000*o['p'])},aresample=48000"
        if 't' in o: ch+=f",atrim=0:{o['t']},afade=t=out:st={max(o['t']-.15,0):.3f}:d=0.15"
        if 'f' in o: ch+=','+o['f']
        ch+=f",volume={g}dB,adelay={int(d*1000)}:all=1[a{i}]";fc.append(ch)
    n=len(ls);fade=1.5 if dur>20 else .1
    fc.append(''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0:duration=longest,atrim=0:{dur},afade=t=in:d={min(fade,.005) if dur<20 else fade},afade=t=out:st={dur-fade}:d={fade},'+('loudnorm=I=-20:TP=-1.5:LRA=11' if dur>20 else 'alimiter=limit=0.89:level=1')+',aresample=48000[o]')
    cmd+=['-filter_complex',';'.join(fc),'-map','[o]','-ar','48000','-c:a','pcm_s16le',f'{B}/{out}.wav']
    r=subprocess.run(cmd,capture_output=True,text=True)
    print(out,"OK" if r.returncode==0 else r.stderr[:600])
json.dump({k:[l[0] for l in v[1]] for k,v in R.items()},open(B+'/recipes_used.json','w'),indent=1)
