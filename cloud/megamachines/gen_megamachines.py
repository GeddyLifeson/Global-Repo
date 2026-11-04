# S6899 gen_megamachines.py: builds and validates the mega vehicle + megastructure catalogue (plans/MEGAMACHINES.md).
# python3 -I gen_megamachines.py <out_dir>   -> writes catalog.json + catalog.tsv, exits 1 on any validation error.
import json, sys, pathlib
AGES = ["I","II","III","IV","V","VI","VII","VIII","RODOS"]
# Specific excavation energy, MJ per m3 (real ranges: soil 1-3, clay 3-6, rock 20-100)
E = {"soil":2.0,"overburden":6.0,"rock":40.0,"ore":25.0,"regolith":60.0}
# id, name, age, class, mass_t, power_MW, medium, eta, rate_m3s_target (0 = not a digger), crew, deck_m2, real_basis
V = [
 ("treadwheel_crane","Treadwheel crane","III","crane",30,0.004,"soil",0.5,0,4,12,"Roman/medieval man-powered wheel crane; lifts 6 t"),
 ("steam_navvy","Steam navvy","V","shovel",25,0.04,"soil",0.35,0.007,2,10,"1840s Otis/Smith steam shovel, 0.6 m3 bucket"),
 ("walking_dragline","Walking dragline","V","dragline",1200,6.0,"overburden",0.55,0.55,3,60,"Bucyrus-Erie style; walks on shoes, 20-60 m3 bucket"),
 ("tunnel_borer","Tunnel boring machine","VI","tbm",900,3.5,"rock",0.45,0.04,6,80,"Channel Tunnel TBM 8.7 m bore, 5-10 m/hour in chalk"),
 ("haul_truck","Mining haul truck","VI","truck",400,3.0,"soil",0.0,0,1,25,"Belaz 75710 class, 450 t payload, 2 x 2.3 MW"),
 ("crawler_crane","Crawler crane","VI","crane",650,1.0,"soil",0.0,0,2,30,"Liebherr LR 13000 class, 3000 t lift"),
 ("bucket_wheel_excavator","Bucket-wheel excavator","VI","bwe",13500,16.5,"overburden",0.5,1.4,5,420,"Bagger 293: 14,200 t, 16.6 MW, ~240,000 m3/day"),
 ("crawler_transporter","Crawler transporter","VI","transporter",2700,4.0,"soil",0.0,0,2,500,"KSC crawler-transporter, 2,700 t, carries 8,000 t"),
 ("autonomous_wheel_excavator","Autonomous bucket-wheel excavator","VII","bwe",13500,16.5,"overburden",0.55,1.6,3,420,"Bagger 293 under remote autopilot, no operators"),
 ("autonomous_haul_fleet","Autonomous haul truck","VII","truck",400,3.0,"soil",0.0,0,1,25,"Komatsu FrontRunner driverless haulage"),
 ("mountain_strip_miner","Mountain strip miner","VIII","bwe",90000,120.0,"rock",0.6,1.5,4,2500,"Scaled-up BWE chain, fusion cell fed; removes ridge lines"),
 ("terraform_builder","Terraform builder","RODOS","builder",400000,900.0,"regolith",0.7,10.0,6,6000,"Planet-scale bulk builder; prints stone, soil, water from shard-fed feedstock"),
]
# id, name, age, kind, footprint_m, height_m, cost_t (bulk material tonnes), power_MW (net, +out/-in), blocks_est, real_basis
S = [
 ("aqueduct_arcade","Aqueduct arcade","III","water",300,25,9000,0.0,4000,"Pont du Gard: 275 m, 49 m, 50,000 t"),
 ("great_dam","Great dam","VI","power",400,120,2500000,500.0,60000,"Hoover Dam: 379 m x 221 m, 2.5 Mt concrete, 2.08 GW"),
 ("ship_lock_flight","Ship lock flight","V","water",600,40,300000,0.0,12000,"Three Gorges lock flight 113 m lift"),
 ("arcology_tower","Arcology tower","VII","habitat",200,500,1500000,-20.0,80000,"Burj Khalifa 828 m, 500 kt; settlement hub, 10,000 residents"),
 ("space_elevator","Space elevator","VIII","transport",100,36000,40000,-50.0,40000,"Tether to GEO 35,786 km; scaled 1:5 world height, climbers by laser power"),
 ("orbital_ring","Orbital ring","RODOS","transport",0,0,500000,-2000.0,90000,"Birch orbital ring: ring at ~300 km, towers to ground"),
 ("dyson_swarm","Dyson collector swarm","RODOS","power",0,0,200000,50000.0,70000,"Statite collector swarm; supplies the Gate launch bank"),
]
# Engine classes (diaithir-units Fuels/Engine ids, PR 257). First entry is the stock engine; arcane_motor is accepted from Age VI (matches the magic fuel gate).
KNOWN_ENGINES = {"draft_animal","steam_piston","petrol_engine","diesel_engine","avgas_piston","jet_turbine","electric_motor","fuel_cell","arcane_motor"}
ENGINES = {
 "treadwheel_crane":["draft_animal"], "steam_navvy":["steam_piston"], "walking_dragline":["steam_piston","electric_motor"],
 "tunnel_borer":["electric_motor","arcane_motor"], "haul_truck":["diesel_engine","electric_motor","arcane_motor"],
 "crawler_crane":["diesel_engine","electric_motor","arcane_motor"], "bucket_wheel_excavator":["electric_motor","arcane_motor"],
 "crawler_transporter":["diesel_engine","arcane_motor"], "autonomous_wheel_excavator":["electric_motor","arcane_motor"],
 "autonomous_haul_fleet":["electric_motor","fuel_cell","arcane_motor"], "mountain_strip_miner":["electric_motor","fuel_cell","arcane_motor"],
 "terraform_builder":["arcane_motor","fuel_cell"],
}
CAPABLE={"autonomous_wheel_excavator","autonomous_haul_fleet","mountain_strip_miner","terraform_builder"}
def vid(r): return "megamachines:"+r[0]
def validate(rows_v, rows_s):
    err=[]
    for r in rows_v:
        i,n,age,cls,m,P,med,eta,rate,crew,deck,_=r
        if age not in AGES: err.append(f"{i}: bad age {age}")
        if rate>0:
            calc=P*eta/E[med]
            if abs(calc-rate)/rate>0.25: err.append(f"{i}: dig rate {rate} m3/s vs power*eta/E = {calc:.3f}")
        if crew<=0: err.append(f"{i}: crew seats removed (seats stay; crewless run needs the autonomy module)")
        if (age in("VII","VIII","RODOS"))!=(i in CAPABLE): err.append(f"{i}: autonomy_capable must be set exactly for Age VII+")
        eng=ENGINES.get(i)
        if not eng or not set(eng)<=KNOWN_ENGINES: err.append(f"{i}: engines missing or unknown {eng}")
        elif "arcane_motor" in eng and AGES.index(age)<5: err.append(f"{i}: arcane_motor before Age VI")
        if deck<=0: err.append(f"{i}: no walkable deck")
        if P/m*1e6>10000: err.append(f"{i}: power/mass above 10 kW/t")
    for r in rows_s:
        i,n,age,kind,fp,h,cost,pw,bl,_=r
        if age not in AGES: err.append(f"{i}: bad age {age}")
        if bl>100000: err.append(f"{i}: block estimate over 100k")
    return err
def main(out):
    err=validate(V,S)
    if err: print("\n".join(err)); sys.exit(1)
    out=pathlib.Path(out); out.mkdir(parents=True,exist_ok=True)
    vk="id name age class mass_t power_MW medium eta dig_m3_s crew deck_m2 real_basis".split()
    sk="id name age kind footprint_m height_m cost_t power_MW blocks real_basis".split()
    cat={"vehicles":[dict(zip(vk,("megamachines:"+r[0],)+r[1:])) for r in V],
         "structures":[dict(zip(sk,("megamachines:"+r[0],)+r[1:])) for r in S],
         "specific_energy_MJ_m3":E}
    for v in cat["vehicles"]:
        v["engines"]=ENGINES[v["id"].split(":")[1]]
        v["autonomy_capable"]=v["id"].split(":")[1] in CAPABLE
        v["dig_m3_s_calc"]=round(v["power_MW"]*v["eta"]/E[v["medium"]],3) if v["eta"] else 0
    (out/"catalog.json").write_text(json.dumps(cat,indent=1))
    lines=["kind\t"+"\t".join(vk)]+["vehicle\t"+"\t".join(str(x) for x in ("megamachines:"+r[0],)+r[1:]) for r in V]
    lines+=["structure\t"+"\t".join(str(x) for x in ("megamachines:"+r[0],)+r[1:]) for r in S]
    (out/"catalog.tsv").write_text("\n".join(lines)+"\n")
    print(f"ok {len(V)} vehicles {len(S)} structures")
main(sys.argv[1] if len(sys.argv)>1 else ".")
