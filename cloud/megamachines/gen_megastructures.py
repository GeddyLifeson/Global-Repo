# S6917 gen_megastructures.py: staged-construction blueprints for the 7 megastructures (plans/MEGASTRUCTURES.md).
# python3 -I gen_megastructures.py <catalog_dir> <out_dir>   reads catalog.json (S6899), writes blueprints.json, stages.tsv, codex_megastructures.tsv
# python3 -I gen_megastructures.py --selftest                validator must reject each injected fault
# Exit 1 on any validation error. Physics: lift t/s = P*eta/(g*h); dig m3/s from the catalogue; remote lift = P*eta/(MJ per t to orbit).
import json, sys, math, pathlib, copy
AGES = ["I","II","III","IV","V","VI","VII","VIII","RODOS"]
G = 9.81
HOIST_ETA = 0.4          # hoist efficiency when the vehicle row has eta 0 (cranes, trucks, transporters)
REMOTE_ETA = 0.5         # beam/launch efficiency for data-driven remote stages
PLACE_H_CAP_M = 500      # literal blocks stop here; sky parts are remote stages
MAX_FLEET = 64           # builders working one stage at once
MAX_STAGE_H = 168        # one stage must finish within a week of fleet work
PALLET_T, CONTAINER_T = 1.0, 20.0   # pallet and bulk-container payload, tonnes (MUNITIONS_CONTAINERS.md ids, c: container tags)
# MJ per tonne lifted: LEO 33, GEO 57, Earth escape 62.5 (orbital energy per kg, real)
# material tag -> (earliest Age, packing: pallet|bulk, source plan)
MAT = {
 "c:stone/cut":(  "III","pallet","proposed"),   "c:timber/beam":("III","pallet","proposed"),
 "c:mortar/lime":( "III","bulk","BUILDING_MATERIALS"), "c:brick/fired":("III","pallet","BUILDING_MATERIALS"),
 "c:beams/steel":( "V","pallet","BUILDING_MATERIALS"), "c:rebar":("V","pallet","BUILDING_MATERIALS"),
 "c:concrete/precast":("VI","pallet","BUILDING_MATERIALS"), "c:cement/bulk":("VI","bulk","BUILDING_MATERIALS"),
 "c:glass_blocks":("VI","pallet","BUILDING_MATERIALS"), "c:plate/steel":("V","pallet","Foundry"),
 "c:tether/ultrahigh":("VIII","pallet","proposed"), "c:composite/panel":("VII","pallet","BUILDING_MATERIALS"),
 "c:feedstock/shard":("RODOS","bulk","MEGAMACHINES terraform"),
}
# Site office (blueprint table) evolves with Age; it is the only crafting surface, no grid recipe.
OFFICE = {"III":"drafting floor","V":"drawing office","VI":"engineering office","VII":"design studio","VIII":"planning hall","RODOS":"shard plotter"}
# structure -> (dig/placement width m, remote_power_MW, remote MJ per t, station Age)
# stage: (key, name, kind dig|place|remote, builder, work (dig m3 | mass fraction), blocks_frac, {mat:frac}, func_frac, real_phase)
D, P, R = "dig", "place", "remote"
B = {
"aqueduct_arcade": dict(station="III", stages=[
 ("piers","Piers and lower tier",P,"treadwheel_crane",.30,.35,{"c:stone/cut":.9,"c:timber/beam":.1},0,"Pont du Gard lower tier: 6 arches on river piers"),
 ("mid","Middle tier",P,"treadwheel_crane",.28,.30,{"c:stone/cut":.9,"c:timber/beam":.1},0,"11 arches carried on the lower tier"),
 ("top","Upper tier",P,"treadwheel_crane",.32,.25,{"c:stone/cut":.9,"c:timber/beam":.1},0,"35 small arches carrying the channel"),
 ("channel","Water channel and lining",P,"treadwheel_crane",.10,.10,{"c:mortar/lime":.7,"c:stone/cut":.3},1.0,"Waterproof specus lined with hydraulic mortar"),
]),
"ship_lock_flight": dict(station="V", stages=[
 ("cut","Excavate the flight",D,"walking_dragline",600*60*40,0.15,{},0,"Three Gorges: lock chambers cut into granite, 5 steps"),
 ("floor","Chamber floors and culverts",P,"steam_navvy",.30,.30,{"c:brick/fired":.5,"c:stone/cut":.5},0,"Culverts fill and drain each chamber"),
 ("walls","Chamber walls",P,"steam_navvy",.40,.35,{"c:stone/cut":.6,"c:brick/fired":.4},0,"Masonry walls hold the water head"),
 ("gates","Gates and sluices",P,"steam_navvy",.20,.15,{"c:beams/steel":.7,"c:plate/steel":.3},0.5,"Miter gates on iron frames"),
 ("fit","Capstans and filling system",P,"steam_navvy",.10,.05,{"c:beams/steel":1.0},1.0,"Operating machinery; ships can transit"),
]),
"great_dam": dict(station="VI", stages=[
 ("tunnels","Diversion tunnels",D,"tunnel_borer",4*math.pi*8.5**2*900,0.05,{},0,"Hoover Dam: 4 diversion tunnels, 17 m bore"),
 ("cut","Excavate foundation and abutments",D,"bucket_wheel_excavator",400*150*40,0.05,{},0,"Canyon walls cut back to sound rock"),
 ("lower","Lower concrete blocks",P,"crawler_crane",.35,.30,{"c:concrete/precast":.8,"c:cement/bulk":.2},0,"Poured in columns with cooling pipes"),
 ("upper","Upper blocks and crest",P,"crawler_crane",.35,.30,{"c:concrete/precast":.8,"c:cement/bulk":.2},0,"Crest road on the arch-gravity wall"),
 ("penstocks","Intake towers and penstocks",P,"crawler_crane",.10,.10,{"c:plate/steel":.6,"c:beams/steel":.4},0,"Steel penstocks to the powerhouse"),
 ("hall","Powerhouse and turbines",P,"crawler_crane",.20,.20,{"c:concrete/precast":.5,"c:rebar":.2,"c:plate/steel":.3},1.0,"Turbine halls start generating one by one"),
]),
"arcology_tower": dict(station="VII", stages=[
 ("cut","Excavate foundation",D,"autonomous_wheel_excavator",200*200*30,0.02,{},0,"Burj Khalifa: 192 piles, 3.7 m mat"),
 ("mat","Foundation mat and piles",P,"crawler_crane",.15,.12,{"c:concrete/precast":.6,"c:rebar":.4},0,"Piled raft foundation"),
 ("core1","Core and frame to one third",P,"crawler_crane",.22,.22,{"c:concrete/precast":.5,"c:rebar":.3,"c:beams/steel":.2},.25,"Buttressed core; lower floors open as the hub"),
 ("core2","Core and frame to two thirds",P,"crawler_crane",.25,.24,{"c:concrete/precast":.5,"c:rebar":.3,"c:beams/steel":.2},.60,"Setbacks reduce wind load"),
 ("crown","Crown and spire",P,"crawler_crane",.13,.12,{"c:beams/steel":.7,"c:composite/panel":.3},.85,"Steel spire on the top"),
 ("skin","Glazed skin and fit-out",P,"crawler_crane",.25,.28,{"c:glass_blocks":.5,"c:composite/panel":.5},1.0,"Curtain wall; 10,000 residents"),
]),
"space_elevator": dict(station="VIII", remote=(3000,57000), stages=[
 ("cut","Excavate the anchor",D,"mountain_strip_miner",100*100*60,0.03,{},0,"Anchor at the equator, ocean platform in the real proposals"),
 ("anchor","Anchor and base station",P,"crawler_crane",.12,.40,{"c:concrete/precast":.5,"c:rebar":.3,"c:beams/steel":.2},0,"Ground terminal and climber platform"),
 ("column","Guide column to 500 m",P,"crawler_crane",.08,.57,{"c:beams/steel":.6,"c:composite/panel":.4},.2,"Literal blocks end here; the rest is data"),
 ("tether1","Tether lift, first third",R,"crawler_transporter",.28,0.0,{"c:tether/ultrahigh":1.0},.45,"Carbon-nanotube tether, climbers by laser power"),
 ("tether2","Tether lift, second third",R,"crawler_transporter",.28,0.0,{"c:tether/ultrahigh":1.0},.75,"Tether reaches geostationary height"),
 ("counter","Counterweight and climbers",R,"crawler_transporter",.24,0.0,{"c:tether/ultrahigh":.5,"c:composite/panel":.5},1.0,"35,786 km tether to GEO"),
]),
"orbital_ring": dict(station="RODOS", remote=(20000,33000), stages=[
 ("tower","Anchor towers",P,"terraform_builder",.10,.50,{"c:feedstock/shard":.6,"c:beams/steel":.4},0,"Birch ring: towers to ground at intervals"),
 ("seg1","Ring segments, first quarter",R,"terraform_builder",.225,.125,{"c:feedstock/shard":1.0},.25,"Ring at ~300 km, spun to hold itself up"),
 ("seg2","Ring segments, second quarter",R,"terraform_builder",.225,.125,{"c:feedstock/shard":1.0},.50,"Segments joined edge to edge"),
 ("seg3","Ring segments, third quarter",R,"terraform_builder",.225,.125,{"c:feedstock/shard":1.0},.75,"Segments joined edge to edge"),
 ("seg4","Ring segments, closure",R,"terraform_builder",.225,.125,{"c:feedstock/shard":1.0},1.0,"Ring closes; transit opens"),
]),
"dyson_swarm": dict(station="RODOS", remote=(20000,62500), stages=[
 ("seed","Seed collectors",R,"terraform_builder",.25,.25,{"c:feedstock/shard":1.0},.15,"Statite collectors on solar-radiation pressure"),
 ("ring1","First collector shell",R,"terraform_builder",.25,.25,{"c:feedstock/shard":1.0},.40,"Swarm density grows with each launch"),
 ("ring2","Second collector shell",R,"terraform_builder",.25,.25,{"c:feedstock/shard":1.0},.70,"Collectors beam power to the Gate launch bank"),
 ("full","Full swarm",R,"terraform_builder",.25,.25,{"c:feedstock/shard":1.0},1.0,"Supplies the Shardfall Gate launch bank"),
]),
}
def ai(a): return AGES.index(a)
def vrate(v, kind, h_m, remote_mj=0, rp=0):
    """work rate per vehicle: m3/s (dig), t/s (place, remote)."""
    if kind=="dig": return v["dig_m3_s_calc"]
    if kind=="place":
        eta=v["eta"] or HOIST_ETA
        return v["power_MW"]*1e6*eta/(G*h_m)/1000
    return rp*REMOTE_ETA/remote_mj   # remote: t/s from the shared beam/launch power, not per vehicle
def build(cat):
    vs={v["id"].split(":")[1]:v for v in cat["vehicles"]}
    ss={s["id"].split(":")[1]:s for s in cat["structures"]}
    out={}; err=[]
    for sid,spec in B.items():
        s=ss.get(sid)
        if not s: err.append(f"{sid}: not in catalogue"); continue
        sa=s["age"]; rp,rmj=spec.get("remote",(0,0))
        if ai(spec["station"])>ai(sa): err.append(f"{sid}: site office {spec['station']} later than Age {sa}")
        if spec["station"] not in OFFICE: err.append(f"{sid}: no site office for {spec['station']}")
        h=max(1,min(s["height_m"] or PLACE_H_CAP_M,PLACE_H_CAP_M)/2)
        mf=sum(st[4] for st in spec["stages"] if st[2]!=D); bf=sum(st[5] for st in spec["stages"])
        if abs(mf-1)>1e-6: err.append(f"{sid}: mass fractions sum {mf:.3f}")
        if abs(bf-1)>1e-6: err.append(f"{sid}: block fractions sum {bf:.3f}")
        last=-1; stages=[]; tot_h=0; tot_blocks=0
        for key,name,kind,bld,work,blk,mats,func,phase in spec["stages"]:
            v=vs.get(bld)
            if not v: err.append(f"{sid}/{key}: builder {bld} not in catalogue"); continue
            if ai(v["age"])>ai(sa): err.append(f"{sid}/{key}: builder {bld} (Age {v['age']}) later than structure Age {sa}")
            if kind==D and v["dig_m3_s_calc"]<=0: err.append(f"{sid}/{key}: {bld} cannot dig")
            if kind==R and not rp: err.append(f"{sid}/{key}: remote stage without remote power")
            if kind!=D and abs(sum(mats.values())-1)>1e-6: err.append(f"{sid}/{key}: material split not 1")
            if kind==D and mats: err.append(f"{sid}/{key}: dig stage lists materials")
            for m in mats:
                if m not in MAT: err.append(f"{sid}/{key}: unknown material tag {m}")
                elif ai(MAT[m][0])>ai(sa): err.append(f"{sid}/{key}: {m} not available until Age {MAT[m][0]}")
            if func<last: err.append(f"{sid}/{key}: function share falls")
            last=func
            rate=vrate(v,kind,h,rmj,rp)
            if kind==D: amount=work; unit="m3"
            else: amount=work*s["cost_t"]; unit="t"
            if rate<=0: err.append(f"{sid}/{key}: zero work rate"); continue
            fleet=1 if kind==R else min(MAX_FLEET,max(1,math.ceil(amount/rate/3600/MAX_STAGE_H)))
            if kind==R: fleet=1
            hours=amount/(rate*fleet)/3600
            if hours>MAX_STAGE_H+1e-9: err.append(f"{sid}/{key}: {hours:.0f} h at {fleet} builders (limit {MAX_STAGE_H} h)")
            pallets=bulk=0
            for m,fr in mats.items():
                t=amount*fr
                if MAT[m][1]=="pallet": pallets+=math.ceil(t/PALLET_T)
                else: bulk+=math.ceil(t/CONTAINER_T)
            blocks=round(blk*s["blocks"]); tot_blocks+=blocks
            tot_h+=hours
            stages.append(dict(key=key,name=name,kind=kind,builder="megamachines:"+bld,amount=round(amount,1),unit=unit,
              materials={m:round(amount*fr,1) for m,fr in mats.items()},pallets=pallets,bulk_containers=bulk,blocks=blocks,
              data_only=(kind==R),fleet=fleet,hours=round(hours,1),crew_hours=round(hours*fleet*v["crew"],1),
              function_share=func,real_phase=phase))
        if tot_blocks>100000: err.append(f"{sid}: {tot_blocks} blocks over 100k")
        out[sid]=dict(id=s["id"],name=s["name"],age=sa,kind=s["kind"],site_office=OFFICE[spec["station"]],station_age=spec["station"],
          cost_t=s["cost_t"],power_MW=s["power_MW"],blocks=tot_blocks,total_fleet_hours=round(tot_h,1),
          pallet_t=PALLET_T,container_t=CONTAINER_T,real_basis=s["real_basis"],stages=stages)
    return out,err
def codex(out):
    rows=["id\tname\tage\tsite_office\tstages\treal_basis\tpanscriptum_text"]
    for sid,o in out.items():
        rows.append("\t".join([o["id"],o["name"],o["age"],o["site_office"]," > ".join(s["name"] for s in o["stages"]),o["real_basis"],"pending: real page text only"]))
    return "\n".join(rows)+"\n"
def selftest(cat):
    faults={
     "builder too late":lambda b:b["aqueduct_arcade"]["stages"].__setitem__(0,b["aqueduct_arcade"]["stages"][0][:3]+("great_dam".replace("great_dam","crawler_crane"),)+b["aqueduct_arcade"]["stages"][0][4:]),
     "material too late":lambda b:b["aqueduct_arcade"]["stages"].__setitem__(0,b["aqueduct_arcade"]["stages"][0][:6]+({"c:rebar":1.0},)+b["aqueduct_arcade"]["stages"][0][7:]),
     "mass fractions off":lambda b:b["great_dam"]["stages"].__setitem__(2,b["great_dam"]["stages"][2][:4]+(.5,)+b["great_dam"]["stages"][2][5:]),
     "function falls":lambda b:b["ship_lock_flight"]["stages"].__setitem__(4,b["ship_lock_flight"]["stages"][4][:7]+(0.1,)+b["ship_lock_flight"]["stages"][4][8:]),
     "stage too slow":lambda b:b["dyson_swarm"].__setitem__("remote",(100,62500)),
    }
    bad=0
    for name,f in faults.items():
        saved=copy.deepcopy(B); f(B); _,err=build(cat)
        B.clear(); B.update(saved)
        if not err: print("selftest MISSED:",name); bad+=1
        else: print("selftest caught:",name,"->",err[0])
    _,err=build(cat)
    if err: print("clean data fails:",err); bad+=1
    sys.exit(1 if bad else 0)
def main():
    if sys.argv[1:]==["--selftest"]:
        selftest(json.load(open(pathlib.Path(__file__).resolve().parents[2]/"plans/megamachines/catalog.json")))
    cat=json.load(open(pathlib.Path(sys.argv[1])/"catalog.json")); out,err=build(cat)
    if err: print("\n".join(err)); sys.exit(1)
    o=pathlib.Path(sys.argv[2]); o.mkdir(parents=True,exist_ok=True)
    (o/"blueprints.json").write_text(json.dumps(out,indent=1))
    k="structure stage kind builder amount unit pallets bulk_containers blocks fleet hours crew_hours function_share real_phase".split()
    rows=["\t".join(k)]
    for sid,s in out.items():
        for i,st in enumerate(s["stages"],1): rows.append("\t".join(str(x) for x in [s["id"],i]+[st[c] if c!="builder" else st["builder"] for c in k[2:]]))
    (o/"stages.tsv").write_text("\n".join(rows)+"\n")
    (o/"codex_megastructures.tsv").write_text(codex(out))
    for s in out.values(): print(f"{s['id']:34} Age {s['age']:5} {len(s['stages'])} stages {s['blocks']:6} blocks {s['total_fleet_hours']:8.1f} fleet-h")
main()
