#!/usr/bin/env python3
"""Generate design/controls/*.csv: input map, remap rules, timing, aim assist,
camera spec and game-feel spec for Shardfall. All values are Shardfall design
choices (3 Oct 2026) unless a column says where they came from. Frames are 60 fps.
Run: python3 design/controls/tools/gen_controls.py  (from game-plan/)."""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
DATA = os.path.join(OUT, '..', '..', 'data')

def rd(p):
    with open(os.path.join(DATA, p), newline='') as f:
        return list(csv.DictReader(f))

def wr(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f'{name}: {len(rows)} rows')

# ---------------------------------------------------------------- contexts
CTX = [  # id, name, priority, active when, stacks on, camera mode
 ('CTX_GLOBAL','Global system',100,'Always','-','-'),
 ('CTX_ONFOOT','On foot (explore and melee)',10,'Player pawn walking, running or fighting','-','CAM_EXPLORE / CAM_COMBAT / CAM_LOCKON'),
 ('CTX_ADS','Aim down sights (first person)',20,'Aim held or toggled with a firearm','CTX_ONFOOT','CAM_ADS_1P'),
 ('CTX_LOWGRAV','Low gravity overlay',15,'Inside REG_Q low-gravity volumes (orbital act)','CTX_ONFOOT','CAM_LOWGRAV'),
 ('CTX_LADDER','Ladder',30,'Attached to a ladder','-','CAM_LADDER'),
 ('CTX_SWIM','Swimming (surface only)',30,'Water deeper than 1.4 m; no diving (choice)','-','CAM_SWIM'),
 ('CTX_MOUNT','Strider mount',30,'Riding the Strider','-','CAM_MOUNT'),
 ('CTX_VEH_DRIVE','Ground vehicle driver',30,'Driver seat of skimmer or hauler','-','CAM_VEH_SKIMMER / CAM_VEH_HAULER'),
 ('CTX_VEH_GUNNER','Hauler turret',30,'Hauler gunner seat','-','CAM_VEH_GUNNER'),
 ('CTX_VEH_PASSENGER','Vehicle passenger',30,'Any passenger seat; own weapons usable','-','CAM_VEH_PASSENGER'),
 ('CTX_VEH_FLYER','Flyer pilot',30,'Hijacked enemy flyer','-','CAM_VEH_FLYER'),
 ('CTX_DOWNED','Downed (co-op)',40,'Health 0 with a living ally in session','-','CAM_DOWNED'),
 ('CTX_SPECTATE','Dead, spectating',40,'All players down or dead waiting on revive','-','CAM_SPECTATE'),
 ('CTX_LOCKPICK','Lockpick',50,'Pick Lock prompt accepted','-','CAM_LOCKPICK'),
 ('CTX_DIALOGUE','Dialogue',50,'Talking to an NPC or Ostra choice','-','CAM_DIALOGUE'),
 ('CTX_RADIAL','Radial wheel',55,'Quick item wheel or social wheel held open','CTX_ONFOOT','unchanged; time slows to 0.3 solo, normal online'),
 ('CTX_MENU','Menus',60,'Pause, inventory, skills, perks, crafting, vendors, journal, options, Shard-note composer','-','CAM_MENU_INSPECT'),
 ('CTX_MAP','World map',60,'Map open','-','none (2D)'),
 ('CTX_PHOTO','Photo mode',70,'STR_PAUSE_PHOTO chosen; offline or solo pause only, online freezes local view only','-','CAM_PHOTO'),
 ('CTX_CINEMATIC','Cinematic',80,'In-engine cutscene or boss intro','-','CAM_CINEMATIC / CAM_BOSS_INTRO'),
 ('CTX_TEXT','Text entry',90,'Chat, character name, Shard-note search, mod hub search','-','-'),
 ('CTX_FORGE','Forgeframe editor',60,'Creation tools sandbox (plan 3.12)','-','CAM_FORGE'),
]
wr('input_contexts.csv', ['ctx_id','name','priority','active_when','stacks_on','camera_mode','enhanced_input_context'],
   [(c[0],c[1],c[2],c[3],c[4],c[5],'IMC_'+c[0][4:]) for c in CTX])

# ---------------------------------------------------------------- actions
# (ctx, action_key, btn_token, trigger, hold_s, xbox, ps, kbm, kbm_alt, buffer_f, notes)
L = 'LB+'; P = 'L1+'
A = [
 # global
 ('GLOBAL','pause','pause','press','', 'Menu','Options','Esc','', '', 'Esc is fixed on KBM (always pause/back); a second key may be added'),
 ('GLOBAL','chat','chat','press','', '-','-','Enter','', '', 'Opens CTX_TEXT; pads use the platform keyboard from the social wheel'),
 ('GLOBAL','push_to_talk','ptt','hold','', 'unbound','unbound','N','', '', 'Voice default is open mic with gate on pad; PTT optional'),
 # on foot
 ('ONFOOT','move','move','axis','', 'LS','Left stick','WASD','Arrow keys','', 'Walk below 0.5 tilt, run above'),
 ('ONFOOT','look','look','axis','', 'RS','Right stick','Mouse','', '', 'Flick switches lock-on target when locked'),
 ('ONFOOT','walk','walk','hold','', 'stick tilt','stick tilt','Left Alt','', '', 'KBM has no analog walk'),
 ('ONFOOT','light','light','press','', 'RB','R1','LMB','', 12, 'Light chain 1-2-3 (ITM_ATK_*_LIGHT_n); while sprinting = running attack; in air = jump attack'),
 ('ONFOOT','heavy','heavy','release','', 'RT','R2','F','Mouse5', 12, 'Release before 0.35 s = heavy; hold = charged heavy'),
 ('ONFOOT','charged','heavy','hold',0.35, 'RT (hold)','R2 (hold)','F (hold)','Mouse5 (hold)', 12, 'Fires at full charge or on release after 0.35 s (ITM_ATK_*_CHARGED)'),
 ('ONFOOT','guard_counter','heavy','press','', 'RT after a block','R2 after a block','F after a block','', 20, 'Valid 20 frames after a blocked hit while block is held (ITM_ATK_*_GUARD)'),
 ('ONFOOT','block','block','hold','', 'LB','L1','Q','', '', 'Also the Weave modifier on pad (see chords)'),
 ('ONFOOT','parry','parry','press','', 'LB','L1','Q','', 4, 'Parry active frames 0-5 of a block press (+4 in Assist); needs a parry-capable off-hand or Fist/Dagger/Shield class'),
 ('ONFOOT','aim','aim','hold','', 'LT','L2','RMB','', 6, 'Enters CTX_ADS (first person); toggle option'),
 ('ONFOOT','jump','jump','press','', 'A','Cross','Space','', 6, 'Jump 10 Breath'),
 ('ONFOOT','roll','roll','press','', 'B','Circle','Left Shift','', 8, 'Tap with direction = roll, no direction = backstep; fires on release before 0.25 s'),
 ('ONFOOT','sprint','sprint','hold',0.25, 'B (hold)','Circle (hold)','Left Shift (hold)','', '', 'Sprint 8 Breath/s; toggle option'),
 ('ONFOOT','crouch','crouch','press','', 'LS click','L3','C','', '', 'Toggle sneak (Infiltration); hold option'),
 ('ONFOOT','interact','interact','press','', 'X','Square','E','', '', 'Tap; hold ring 0.8 s for steal, pickpocket, revive, hijack (STR_PROMPT_*)'),
 ('ONFOOT','reload','reload','press','', 'X','Square','R','', 10, 'Pad: X reloads only when no interact prompt is on screen'),
 ('ONFOOT','swap','swap','press','', 'Y','Triangle','Mouse wheel','1 / 2', '', 'Primary 1 <-> Primary 2; holster 0.4 s + ads_ms (loops DR-006)'),
 ('ONFOOT','sidearm','swap','hold',0.3, 'Y (hold)','Triangle (hold)','3','', '', 'Draw sidearm (Pistol slot)'),
 ('ONFOOT','lock','lock','press','', 'RS click','R3','MMB','', '', 'Lock-on toggle; hold 0.4 s = recentre camera with no target'),
 ('ONFOOT','lock_switch','look','flick','', 'RS flick','Right stick flick','Mouse flick','Mouse wheel (when locked)', '', 'See camera_rules LOCK_SWITCH_*'),
 ('ONFOOT','cast','cast','chord','', L+'X',P+'Square','G','', 10, 'Cast slot (ABL_*_CAST)'),
 ('ONFOOT','strike','strike','chord','', L+'Y',P+'Triangle','V','', 10, 'Strike slot (ABL_*_STRIKE)'),
 ('ONFOOT','step','step','chord','', L+'B',P+'Circle','Left Ctrl','', 8, 'Step slot (ABL_*_STEP), 10 i-frames'),
 ('ONFOOT','resonance','resonance','chord','', L+'A',P+'Cross','B','', 10, 'Equipped Resonance (RES_*)'),
 ('ONFOOT','surge','surge','chord','', 'LB+RB','L1+R1','X','', 10, 'Surge at 100 charge (ABL_*_SURGE)'),
 ('ONFOOT','weapon_art','art','chord','', L+'RT',P+'R2','Mouse4','', 10, 'Weapon Art (ITM_ART_*); after a blocked hit LB+RT is guard counter instead'),
 ('ONFOOT','tonic','tonic','press','', 'D-pad up','D-pad up','4','', 10, 'Drink Tonic (0.8 s, cancellable by roll after frame 30)'),
 ('ONFOOT','strider','strider','hold',0.5, 'D-pad up (hold)','D-pad up (hold)','T','', '', 'Summon or dismiss Strider'),
 ('ONFOOT','belt_use','belt','press','', 'D-pad down','D-pad down','5','', 10, 'Use selected belt item'),
 ('ONFOOT','belt_next','belt_next','press','', 'D-pad right','D-pad right','6 / 7 / 8','', '', 'Pad cycles 4 belt slots; KBM 5-8 use slots 1-4 directly'),
 ('ONFOOT','quick_wheel','wheel','hold',0.3, 'D-pad down (hold)','D-pad down (hold)','Caps Lock (hold)','', '', 'Opens CTX_RADIAL with 8 consumables'),
 ('ONFOOT','ping','ping','press','', 'D-pad left','D-pad left','Z','', '', 'Context ping: enemy, item, place; 3 per 5 s'),
 ('ONFOOT','social_wheel','social','hold',0.3, 'D-pad left (hold)','D-pad left (hold)','Z (hold)','', '', 'Emotes, Shard-note, quick chat'),
 ('ONFOOT','map','map','press','', 'View','Touchpad','M','', '', ''),
 ('ONFOOT','journal','journal','hold',0.4, 'View (hold)','Touchpad (hold)','J','', '', ''),
 ('ONFOOT','inventory','inventory','press','', 'via pause hub','via pause hub','Tab','I', '', 'Pause hub opens on last tab'),
 ('ONFOOT','skills','skills','press','', 'via pause hub (skills tab)','via pause hub (skills tab)','K','', '', 'Skills and perks'),
 # ADS
 ('ADS','fire','fire','hold','', 'RT','R2','LMB','', 4, 'Semi-auto fires on press; autos while held'),
 ('ADS','gun_bash','light','press','', 'RB','R1','F','', 6, 'Quick gun melee; stays first person'),
 ('ADS','reload','reload','press','', 'X','Square','R','', 10, ''),
 ('ADS','steady','steady','hold','', 'LS click','L3','Left Shift (hold)','', '', 'Scout and Sniper: hold breath 4 s, sway x0.2, drains 10 Breath/s'),
 ('ADS','zoom_step','zoom','press','', 'RS click','R3','MMB','', '', 'Sniper and Shard Lance 2-step zoom'),
 ('ADS','exit_roll','roll','press','', 'B','Circle','Left Shift (tap)','', 8, 'Roll exits ADS; ADS resumes if aim still held after recovery'),
 ('ADS','exit_block','block','press','', 'LB','L1','Q','', 4, 'Drops to block or parry in third person'),
 # low gravity
 ('LOWGRAV','jump_long','jump','press','', 'A','Cross','Space','', 6, 'Jump height x2.5'),
 ('LOWGRAV','thrust','glide','hold','', 'A (hold, airborne)','Cross (hold, airborne)','Space (hold, airborne)','', '', 'Suit thruster hover 2 s, refills on landing'),
 ('LOWGRAV','air_dash','roll','press','', 'B (airborne)','Circle (airborne)','Left Shift (airborne)','', 8, 'One air dash per jump, 15 Breath'),
 # ladder
 ('LADDER','climb','move','axis','', 'LS','Left stick','W / S','', '', 'Hold sprint to slide down'),
 ('LADDER','ladder_atk_up','light','press','', 'RB','R1','LMB','', '', 'Kick upward'),
 ('LADDER','ladder_atk_down','heavy','press','', 'RT','R2','F','', '', 'Stomp downward'),
 ('LADDER','let_go','roll','press','', 'B','Circle','Left Shift','', '', 'Drop off'),
 # swim
 ('SWIM','swim','move','axis','', 'LS','Left stick','WASD','', '', 'No combat; weapons holstered'),
 ('SWIM','swim_fast','sprint','hold','', 'B (hold)','Circle (hold)','Left Shift (hold)','', '', '6 Breath/s; at 0 Breath swim slows, no drowning'),
 ('SWIM','climb_out','interact','press','', 'X','Square','E','', '', 'Auto-ledge also works'),
 # mount
 ('MOUNT','steer','move','axis','', 'LS','Left stick','WASD','', '', ''),
 ('MOUNT','gallop','sprint','hold','', 'B (hold)','Circle (hold)','Left Shift (hold)','', '', 'Strider stamina, separate from Breath'),
 ('MOUNT','m_jump','jump','press','', 'A','Cross','Space','', 6, 'Second press in air = double jump'),
 ('MOUNT','glide','glide','hold','', 'A (hold, falling)','Cross (hold, falling)','Space (hold, falling)','', '', 'STR_PRM_FALL_T prompt'),
 ('MOUNT','m_light','light','press','', 'RB','R1','LMB','', 12, 'Mounted light attack'),
 ('MOUNT','m_heavy','heavy','press','', 'RT','R2','F','', 12, 'Mounted heavy attack'),
 ('MOUNT','m_aim','aim','hold','', 'LT','L2','RMB','', '', 'Mounted ADS, stability -20%'),
 ('MOUNT','dismount','interact','hold',0.4, 'X (hold)','Square (hold)','E (hold)','', '', ''),
 # ground vehicle driver
 ('VEH_DRIVE','v_steer','move','axis','', 'LS','Left stick','A / D','', '', ''),
 ('VEH_DRIVE','throttle','throttle','axis','', 'RT','R2','W','', '', 'Analog on pad'),
 ('VEH_DRIVE','brake','brake','axis','', 'LT','L2','S','', '', 'Reverse when stopped'),
 ('VEH_DRIVE','boost','boost','press','', 'A','Cross','Left Shift','', '', 'Skimmer: 3 s boost, 6 s recharge (STR_TIP_040). Hauler: horn'),
 ('VEH_DRIVE','handbrake','handbrake','hold','', 'RB','R1','Space','', '', ''),
 ('VEH_DRIVE','seat_swap','seat','press','', 'B','Circle','Q','', '', ''),
 ('VEH_DRIVE','look_back','lookback','hold','', 'RS click','R3','C','', '', ''),
 ('VEH_DRIVE','exit','interact','hold',0.4, 'X (hold)','Square (hold)','E (hold)','', '', 'Exit at speed above 15 m/s rolls the player out'),
 # gunner
 ('VEH_GUNNER','turret_aim','look','axis','', 'RS','Right stick','Mouse','', '', ''),
 ('VEH_GUNNER','turret_fire','fire','hold','', 'RT','R2','LMB','', '', 'Overheats after 4 s (STR_TIP_041)'),
 ('VEH_GUNNER','turret_zoom','aim','hold','', 'LT','L2','RMB','', '', 'x2 zoom'),
 ('VEH_GUNNER','seat_swap','seat','press','', 'B','Circle','Q','', '', ''),
 ('VEH_GUNNER','exit','interact','hold',0.4, 'X (hold)','Square (hold)','E (hold)','', '', ''),
 # passenger
 ('VEH_PASSENGER','p_aim','aim','hold','', 'LT','L2','RMB','', '', 'Own firearms, Halo-style'),
 ('VEH_PASSENGER','p_fire','fire','hold','', 'RT','R2','LMB','', '', ''),
 ('VEH_PASSENGER','p_reload','reload','press','', 'X','Square','R','', '', ''),
 ('VEH_PASSENGER','p_swap','swap','press','', 'Y','Triangle','Mouse wheel','', '', ''),
 ('VEH_PASSENGER','seat_swap','seat','press','', 'B','Circle','Q','', '', ''),
 ('VEH_PASSENGER','exit','interact','hold',0.4, 'X (hold)','Square (hold)','E (hold)','', '', ''),
 # flyer
 ('VEH_FLYER','f_move','move','axis','', 'LS','Left stick','WASD','', '', 'Forward thrust and strafe'),
 ('VEH_FLYER','f_aim','look','axis','', 'RS','Right stick','Mouse','', '', 'Heading follows aim'),
 ('VEH_FLYER','f_fire','fire','hold','', 'RT','R2','LMB','', '', 'Twin bolts'),
 ('VEH_FLYER','f_alt','aim','press','', 'LT','L2','RMB','', '', 'Homing charge, 8 s cooldown'),
 ('VEH_FLYER','ascend','jump','hold','', 'A','Cross','Space','', '', ''),
 ('VEH_FLYER','descend','crouch','hold','', 'B','Circle','Left Ctrl','', '', ''),
 ('VEH_FLYER','f_boost','boost','hold','', 'RB','R1','Left Shift','', '', ''),
 ('VEH_FLYER','f_evade','roll','press','', 'LB','L1','Q','', '', 'Barrel roll, 3 s cooldown'),
 ('VEH_FLYER','eject','interact','hold',0.4, 'X (hold)','Square (hold)','E (hold)','', '', ''),
 # downed / spectate
 ('DOWNED','crawl','move','axis','', 'LS','Left stick','WASD','', '', 'Crawl at 0.8 m/s'),
 ('DOWNED','call_help','ping','press','', 'D-pad left','D-pad left','Z','', '', ''),
 ('DOWNED','give_up','giveup','hold',2.0, 'B (hold)','Circle (hold)','Left Shift (hold)','', '', 'Respawn at Anchor'),
 ('SPECTATE','next','next','press','', 'RB','R1','LMB','', '', 'STR_PRM_SPECTATE_T'),
 ('SPECTATE','prev','prev','press','', 'LB','L1','RMB','', '', ''),
 ('SPECTATE','leave','giveup','hold',2.0, 'B (hold)','Circle (hold)','Esc (hold)','', '', ''),
 # lockpick
 ('LOCKPICK','pick_turn','look','axis','', 'RS','Right stick','Mouse','', '', 'STR_TUT_LOCKPICK_B'),
 ('LOCKPICK','lock_turn','confirm','hold','', 'A','Cross','E','Enter', '', 'Turn the lock; pick breaks after 1.5 s of forcing'),
 ('LOCKPICK','pick_exit','back','press','', 'B','Circle','Esc','', '', ''),
 # dialogue
 ('DIALOGUE','choose','move','axis','', 'LS / D-pad','Left stick / D-pad','Mouse','1-6', '', ''),
 ('DIALOGUE','select','confirm','press','', 'A','Cross','E','Enter / LMB', '', ''),
 ('DIALOGUE','skip_line','skip','press','', 'B','Circle','Space','', '', 'Skips the current line only'),
 ('DIALOGUE','history','log','press','', 'X','Square','L','', '', 'Dialogue log'),
 # radial
 ('RADIAL','r_select','look','axis','', 'RS','Right stick','Mouse','', '', 'Release the open button to confirm'),
 ('RADIAL','r_cancel','back','press','', 'B','Circle','RMB','', '', ''),
 # menus
 ('MENU','navigate','move','axis','', 'LS / D-pad','Left stick / D-pad','Mouse','Arrow keys', '', ''),
 ('MENU','confirm','confirm','press','', 'A','Cross','E','Enter / LMB', '', 'Cross/Circle swap option for Japan-style confirm'),
 ('MENU','back','back','press','', 'B','Circle','Esc','RMB', '', ''),
 ('MENU','tab_prev','tab_prev','press','', 'LB','L1','Q','', '', ''),
 ('MENU','tab_next','tab_next','press','', 'RB','R1','3','', '', ''),
 ('MENU','sub_prev','sub_prev','press','', 'LT','L2','Z','', '', ''),
 ('MENU','sub_next','sub_next','press','', 'RT','R2','C','', '', ''),
 ('MENU','junk','junk','press','', 'X','Square','X','', '', 'Mark as junk / context action'),
 ('MENU','compare','compare','hold','', 'Y (hold)','Triangle (hold)','Left Shift (hold)','', '', ''),
 ('MENU','details','details','press','', 'RS click','R3','Tab','', '', 'Extended stats'),
 ('MENU','rotate_preview','look','axis','', 'RS','Right stick','LMB drag','', '', 'Character and item inspect'),
 ('MENU','sort','sort','press','', 'View','Touchpad','R','', '', ''),
 ('MENU','close','close','press','', 'Menu','Options','Esc (hold 0.4 s)','', '', 'Close all menus'),
 # map
 ('MAP','cursor','move','axis','', 'LS','Left stick','Mouse','WASD', '', ''),
 ('MAP','zoom_in','zoom','press','', 'RT','R2','Mouse wheel up','', '', ''),
 ('MAP','zoom_out','zoom','press','', 'LT','L2','Mouse wheel down','', '', ''),
 ('MAP','layer','layer','press','', 'LB / RB','L1 / R1','Q / E','', '', 'Surface, Undervault, the Quiet'),
 ('MAP','waypoint','confirm','press','', 'A','Cross','LMB','', '', 'Waypoint, or fast travel on a lit Anchor'),
 ('MAP','filters','filters','press','', 'X','Square','F','', '', ''),
 ('MAP','to_journal','journal','press','', 'Y','Triangle','J','', '', ''),
 ('MAP','center','center','press','', 'RS click','R3','Space','', '', ''),
 ('MAP','map_close','back','press','', 'B','Circle','M / Esc','', '', ''),
 # photo
 ('PHOTO','ph_move','move','axis','', 'LS','Left stick','WASD','', '', 'Tether 8 m from player'),
 ('PHOTO','ph_look','look','axis','', 'RS','Right stick','Mouse (RMB held)','', '', ''),
 ('PHOTO','ph_down','down','hold','', 'LT','L2','Left Ctrl','', '', ''),
 ('PHOTO','ph_up','up','hold','', 'RT','R2','Space','', '', ''),
 ('PHOTO','ph_roll','roll_cam','hold','', 'LB / RB','L1 / R1','Q / E','', '', ''),
 ('PHOTO','ph_take','take','press','', 'A','Cross','Enter','', '', 'STR_PHOTO_TAKE'),
 ('PHOTO','ph_hide_ui','hide_ui','press','', 'X','Square','H','', '', ''),
 ('PHOTO','ph_hide_player','hide_player','press','', 'Y','Triangle','P','', '', 'STR_PHOTO_HIDE_PLAYER'),
 ('PHOTO','ph_panel','panel','press','', 'D-pad','D-pad','LMB on panel','', '', ''),
 ('PHOTO','ph_reset','reset','press','', 'RS click','R3','R','', '', ''),
 ('PHOTO','ph_exit','back','press','', 'B','Circle','Esc','', '', ''),
 # cinematic
 ('CINEMATIC','skip_cine','skip','hold',1.0, 'A (hold)','Cross (hold)','Space (hold)','', '', 'Any cutscene, first viewing included (A17)'),
 ('CINEMATIC','cine_pause','pause','press','', 'Menu','Options','Esc','', '', 'Solo only'),
 # text
 ('TEXT','send','confirm','press','', 'platform keyboard','platform keyboard','Enter','', '', ''),
 ('TEXT','cancel_text','back','press','', 'B','Circle','Esc','', '', ''),
 # forge
 ('FORGE','fg_move','move','axis','', 'LS','Left stick','WASD','', '', ''),
 ('FORGE','fg_orbit','look','axis','', 'RS','Right stick','Mouse (RMB held)','', '', ''),
 ('FORGE','fg_place','confirm','press','', 'A','Cross','LMB','', '', ''),
 ('FORGE','fg_delete','delete','press','', 'B','Circle','Delete','', '', ''),
 ('FORGE','fg_dup','duplicate','press','', 'X','Square','Ctrl+D','', '', ''),
 ('FORGE','fg_props','properties','press','', 'Y','Triangle','Tab','', '', ''),
 ('FORGE','fg_cat','category','press','', 'LB / RB','L1 / R1','Q / E','', '', ''),
 ('FORGE','fg_rotate','rotate','hold','', 'LT / RT','L2 / R2','Z / C','', '', '15 degree steps, hold LS click for free rotate'),
 ('FORGE','fg_height','raise','press','', 'D-pad up / down','D-pad up / down','Page Up / Page Down','', '', ''),
 ('FORGE','fg_grid','grid','press','', 'D-pad left / right','D-pad left / right','G','', '', '0.25, 0.5, 1, 2 m'),
 ('FORGE','fg_undo','undo','press','', 'View','Touchpad left','Ctrl+Z','', '', 'Redo: View hold / Touchpad right / Ctrl+Y'),
 ('FORGE','fg_test','test','press','', 'Menu (hold)','Options (hold)','F5','', '', 'Test play'),
]
rows = []
for i, a in enumerate(A, 1):
    ctx, key, tok, trig, hold, xb, ps, kb, kb2, buf, note = a
    rows.append((f'IA_{ctx}_{key.upper()}', 'CTX_'+ctx, key, 'BTN_'+tok, trig, hold, xb, ps, kb, kb2, buf,
                 'N' if (ctx == 'GLOBAL' and key == 'pause') else 'Y', note))
wr('input_actions.csv', ['action_id','ctx_id','action','btn_token','trigger','hold_s','xbox','ps5','kbm','kbm_alt','buffer_frames','remappable','notes'], rows)

# preset bindings: per-action overrides of the default map; columns use input_actions vocabulary
import re
def preset_rows():
    out, by_id = [], {r[0]: r for r in rows}
    def put(pre, aid, col, binding, trig='', hold='', why=''):
        out[:] = [r for r in out if r[:3] != (pre, aid, col)]
        out.append((pre, aid, col, binding, trig, hold, why))
    def subst(pre, col, idx, table, chords='keep'):
        for r in rows:
            base, sep, note = r[idx].partition(' (')
            new = '-' if chords == 'drop' and '+' in base else table.get(base, base)
            if new != base:
                put(pre, r[0], col, new + (sep + note if new != '-' else ''))
    S = 'PRE_SHOOTER'
    for aid, b, t, h in [('IA_ONFOOT_CAST', 'LB', 'press', ''), ('IA_ONFOOT_STRIKE', 'Y (hold)', 'hold', '0.3'),
                         ('IA_ONFOOT_SIDEARM', 'D-pad right (hold)', 'hold', '0.3'), ('IA_ONFOOT_STEP', 'B', 'double_tap', ''),
                         ('IA_ONFOOT_SURGE', 'LB+RB', 'chord', ''), ('IA_ONFOOT_BLOCK', 'LS click', 'hold', ''),
                         ('IA_ONFOOT_PARRY', 'LS click', 'press', ''), ('IA_ONFOOT_CROUCH', 'B (hold)', 'hold', '0.25'),
                         ('IA_ADS_EXIT_BLOCK', 'LS click', 'press', '')]:
        put(S, aid, 'pad', b, t, h)
    D = 'PRE_DIRECT'
    for aid, b, t, h, why in [('IA_ONFOOT_CAST', 'D-pad up', 'press', '', ''), ('IA_ONFOOT_STRIKE', 'D-pad right', 'press', '', ''),
                              ('IA_ONFOOT_STEP', 'D-pad left', 'press', '', ''), ('IA_ONFOOT_SURGE', 'D-pad down', 'press', '', ''),
                              ('IA_ONFOOT_RESONANCE', 'D-pad right (hold)', 'hold', '0.3', 'off the chord too'),
                              ('IA_ONFOOT_WEAPON_ART', 'LS click (hold)', 'hold', '0.3', 'off the chord too'),
                              ('IA_ONFOOT_TONIC', 'Y (hold)', 'hold', '0.3', ''), ('IA_ONFOOT_SIDEARM', 'X (hold)', 'hold', '0.3', 'Y hold is Tonic'),
                              ('IA_ONFOOT_BELT_USE', 'Y', 'double_tap', '', ''), ('IA_ONFOOT_BELT_NEXT', 'unbound', '', '', 'pick belt items on the quick wheel'),
                              ('IA_ONFOOT_PING', 'RS click (hold)', 'hold', '0.3', 'D-pad left is Step')]:
        put(D, aid, 'pad', b, t, h, why)
    for r in rows:  # southpaw: mirror every left/right stick, bumper and trigger
        new = re.sub(r'\b([LR])([SBT])\b', lambda m: 'RL'[m[1] == 'R'] + m[2], r[6])
        if new != r[6]:
            put('PRE_SOUTHPAW', r[0], 'pad', new)
    # one-handed: chorded abilities and D-pad items move to the quick wheel
    dpad_off = {f'D-pad {d}': '-' for d in ('up', 'down', 'left', 'right')}
    subst('PRE_ONEHAND_L', 'pad', 6, {**dpad_off, 'RS': 'D-pad', 'RS flick': 'D-pad', 'RS click': 'LB+LS click',
          'A': 'LB+D-pad down', 'B': 'LB+D-pad right', 'X': 'LB+D-pad left', 'Y': 'LB+D-pad up', 'RB': 'LT', 'RT': 'LB+LT',
          'LT': 'LS click', 'LS click': 'View', 'Menu': 'View (hold)', 'View': '-', 'LB / RB': '-', 'LT / RT': '-'}, 'drop')
    put('PRE_ONEHAND_L', 'IA_ONFOOT_QUICK_WHEEL', 'pad', 'LB+View', 'chord', '', 'D-pad is look')
    subst('PRE_ONEHAND_R', 'pad', 6, {**dpad_off, 'LS': 'Face buttons', 'A': 'RB+A', 'B': 'RB+B', 'X': 'RB+X', 'Y': 'RB+Y',
          'LB': 'RB', 'RB': 'RT', 'RT': 'RB+RT', 'LT': 'RS click', 'RS click': 'RB+RS click', 'LS click': 'Menu',
          'Menu': 'Menu (hold)', 'View': '-', 'LB / RB': '-', 'LT / RT': '-'}, 'drop')
    put('PRE_ONEHAND_R', 'IA_ONFOOT_QUICK_WHEEL', 'pad', 'RB+Menu', 'chord', '', 'D-pad is out of reach')
    for r in rows:  # simplified: light auto-chains on hold, heavy charges by tap, short hold-rings on unshared keys become taps
        if r[0] in ('IA_ONFOOT_LIGHT', 'IA_ONFOOT_HEAVY'):
            for col, i in (('pad', 6), ('kbm', 8)):
                put('PRE_SIMPLE', r[0], col, r[i], 'hold' if r[0] == 'IA_ONFOOT_LIGHT' else 'press', '',
                    'auto-chain 1-2-3 while held' if r[0] == 'IA_ONFOOT_LIGHT' else 'tap to start charging, tap to release')
        elif r[0] == 'IA_ONFOOT_CHARGED':
            for col in ('pad', 'kbm', 'kbm_alt'):
                put('PRE_SIMPLE', r[0], col, '-', why='charge comes from heavy taps')
        elif r[4] == 'hold' and r[5] and 0.4 <= float(r[5]) <= 1.0:
            for col, i in (('pad', 6), ('kbm', 8)):
                base = r[i].partition(' (')[0]
                if not any(o is not r and o[1] == r[1] and o[i].partition(' (')[0] == base for o in rows):
                    put('PRE_SIMPLE', r[0], col, base, 'press', '', 'hold-ring becomes a tap')
    subst('PRE_KBM_LEFTY', 'kbm', 8, KBM_LEFTY)
    subst('PRE_KBM_LEFTY', 'kbm_alt', 9, KBM_LEFTY)
    return out

KBM_LEFTY = {'W': 'I', 'A': 'J', 'S': 'K', 'D': 'L', 'WASD': 'IJKL', 'W / S': 'I / K', 'A / D': 'J / L', 'Q': 'U', 'E': 'O',
             'Q / E': 'U / O', 'R': 'P', 'F': 'Semicolon', 'T': 'Y', 'C': 'Right Ctrl', 'Z': 'Slash', 'Z / C': 'Slash / Right Ctrl',
             'G': 'Num1', 'V': 'Num2', 'Left Ctrl': 'Num3', 'B': 'Num4', 'X': 'Num5', 'Space': 'Num0', 'Left Shift': 'Right Shift',
             'Left Alt': 'Right Alt', 'Caps Lock': 'Apostrophe', 'J': 'Home', 'K': 'End', 'I': '-', 'Ctrl+D': 'Ctrl+L', 'Ctrl+Z': 'Ctrl+Slash'}
wr('input_preset_bindings.csv', ['preset_id','action_id','column','binding','trigger','hold_s','why'], preset_rows())

# conflict check: same context, same physical binding and same trigger
seen = {}; bad = []
for r in rows:
    for dev, col in (('xbox', 6), ('ps5', 7), ('kbm', 8)):
        k = (r[1], dev, r[col], r[4])
        if r[col] in ('-', 'unbound', '') or r[4] == 'axis': continue
        if k in seen and r[2] not in ('parry','block','reload','interact','heavy','guard_counter'):
            bad.append((r[0], seen[k], dev, r[col]))
        seen[k] = r[0]
if bad:
    print('BINDING CONFLICTS:', bad)
tokens_used = sorted({r[3] for r in rows})

# ---------------------------------------------------------------- presets
wr('input_presets.csv', ['preset_id','name','device','changes_from_default','why'], [
 ('PRE_DEFAULT','Shardfall Default','pad, kbm','-','Souls melee on bumpers, shooter aim on LT, abilities on the block chord'),
 ('PRE_SHOOTER','Shooter','pad','LB = Cast, RB = light, RT = heavy (fire when aiming), Y (hold) = Strike, B double-tap = Step, LB+RB = Surge; block and parry move to LS click; crouch to B (hold while still); swap to Y tap','Destiny and Halo players'),
 ('PRE_DIRECT','Direct Abilities','pad','Abilities move off the chord: D-pad up Cast, right Strike, left Step, down Surge; Tonic moves to Y (hold 0.3 s), belt to Y double-tap','Players who cannot chord (A05)'),
 ('PRE_SOUTHPAW','Southpaw','pad','Swap LS and RS; swap LB/RB and LT/RT pairs','Left-handed play'),
 ('PRE_ONEHAND_L','One-handed (left)','pad','All actions on LS, D-pad, LB, LT, L3, View; face buttons via LB+D-pad layer','A05'),
 ('PRE_ONEHAND_R','One-handed (right)','pad','All actions on RS, face buttons, RB, RT, R3, Menu; face buttons move, their actions via RB+face layer','A05'),
 ('PRE_SIMPLE','Simplified combo','pad, kbm','Hold light = auto-chain light 1-2-3; hold-ring prompts become taps; mash prompts become holds; charged heavy is tap-to-start, tap-to-release','A05, A16'),
 ('PRE_KBM_LEFTY','Left-handed keyboard','kbm','IJKL move, numpad abilities, mouse in left hand','Left-handed KBM'),
])

# ---------------------------------------------------------------- remap rules
R = [
 ('Scope','Every action in input_actions.csv is remappable on pad and KBM, per context, except IA_GLOBAL_PAUSE on KBM (Esc stays; a second key can be added). Accessibility A01.'),
 ('Reserved','Never bindable: Xbox Guide and Share, PS button, Create and mute, Steam and Quick Access buttons, Windows key, Alt+Tab, Alt+F4, F12 (Steam screenshot).'),
 ('Separate profiles','Pad and KBM bindings are stored separately in the profile save and cloud save. One pad profile is shared by Xbox and PS layouts by position.'),
 ('Conflict scope','A conflict only exists inside one context or between contexts that stack (CTX_ONFOOT with CTX_ADS, CTX_LOWGRAV and CTX_RADIAL). Different contexts may reuse keys.'),
 ('Conflict prompt','On conflict show STR_OPT_REMAP_CONFLICT and swap the two bindings on confirm; cancel keeps the old binding.'),
 ('Shared keys by design','Pairs that share a key by trigger type and stay valid after a remap only if moved together: block + parry (hold/press), heavy + charged + guard counter, interact + reload on pad, roll + sprint, swap + sidearm. Moving one moves its partners; the UI lists them as one row with sub-rows.'),
 ('Chord modifier','The Weave modifier (default LB/L1 = block) can be moved to any button. If it moves off block, block keeps LB and the modifier button loses its tap action while chords are pending (4-frame chord window).'),
 ('Hold or toggle','Each hold action offers Hold or Toggle: sprint, aim, block, crouch, steady, gallop, walk. Charged heavy offers Hold or Tap-start/Tap-release. A02.'),
 ('Hold rings','Interact hold-ring time 0.8 s, adjustable 0.4-1.6 s; option "Hold prompts become taps". A16.'),
 ('Mash prompts','No mash prompts in Shardfall. Any repeated-press QTE (grab escapes) accepts hold instead. A16.'),
 ('Axes','Sticks can be swapped (southpaw) and inverted per axis (STR_OPT_INVERT_X/Y) for look, aim, flyer, turret and photo separately. Movement axes cannot bind to buttons on pad; on KBM movement is four keys.'),
 ('Glyphs','Glyphs follow the last device used, with 0.5 s debounce; mouse movement under 4 px does not switch to KBM. Glyph sets: Xbox, PS5, KBM, Steam Deck (UV-079). BTN_ tokens in strings resolve to the bound key, never to the default.'),
 ('Steam Input','PC ships Steam Input action sets mirroring every context, plus native XInput and DualSense. Gyro aim (DualSense and Steam Deck) optional, off by default, active only in CTX_ADS and CTX_VEH_GUNNER.'),
 ('Reset','STR_OPT_REMAP_RESET resets the current device; per-context reset is a button on each context header.'),
 ('Unbound','An action may be left unbound except: move, look, light, roll, interact, confirm, back, pause. The menu blocks exit while any of these is unbound.'),
 ('Fairness','No macros or turbo in any mode. Fire rate is always capped by rpm in firearm_classes.csv, so rapid-fire hardware gives no gain. Aim assist off in PvP Arena (STR_OPT_AIM_ASSIST_D); input device is reported to matchmaking for crossplay pools.'),
 ('Persistence','Bindings save on leaving the Remap tab (STR_OPT_UNSAVED if unsaved). Version field in the profile: new actions added in patches take their default unless the default key is taken, then stay unbound and flag a one-time banner.'),
]
wr('remap_rules.csv', ['rule_id','rule','detail'], [(f'RMP_{i:02d}', a, b) for i, (a, b) in enumerate(R, 1)])

# ---------------------------------------------------------------- timing
T = [
 ('TIM_BUFFER_ATTACK','Attack input buffer',12,'frames','Light, heavy, art and ability inputs pressed during the last 12 frames of recovery fire on the first cancel frame'),
 ('TIM_BUFFER_ROLL','Roll buffer',8,'frames','Roll can be buffered in the last 8 frames of recovery (melee_frame_data note: roll cancel after recovery-8)'),
 ('TIM_BUFFER_JUMP','Jump buffer and coyote time',6,'frames','Jump pressed 6 frames before landing fires on landing; jump allowed 6 frames after leaving a ledge'),
 ('TIM_CHORD','Chord window',4,'frames','LB+button within 4 frames counts as a chord; the LB press still opens a parry window'),
 ('TIM_TAP_HOLD','Tap vs hold threshold',0.25,'s','roll vs sprint, ping vs wheel'),
 ('TIM_CHARGE','Charged heavy threshold',0.35,'s','Full charge at 0.9 s; release between 0.35 and 0.9 s scales motion value linearly to the charged value'),
 ('TIM_SIDEARM_HOLD','Sidearm hold',0.3,'s',''),
 ('TIM_HOLD_RING','Interact hold ring',0.8,'s','From STR_PROMPT_* notes'),
 ('TIM_DOUBLE_TAP','Double tap window',0.25,'s','Used by PRE_DIRECT only'),
 ('TIM_GUARD_COUNTER','Guard counter window',20,'frames','After a blocked hit while block held'),
 ('TIM_PARRY','Parry active frames',6,'frames','loops/01-combat.md; +4 in Assist (STR_OPT_ASSIST_D)'),
 ('TIM_RIPOSTE','Riposte window',60,'frames','After a successful parry (loops/01-combat.md)'),
 ('TIM_COMMIT','Animation commit frame',6,'frames','Plan 3.4: attacks commit after frame 6 of startup; before that, roll or block cancels'),
 ('TIM_GLYPH_DEBOUNCE','Device switch debounce',0.5,'s',''),
 ('DZ_LS_INNER','Left stick inner deadzone',0.12,'radial','STR_OPT_DEADZONE_L range 0.00-0.30'),
 ('DZ_LS_OUTER','Left stick outer deadzone',0.95,'radial',''),
 ('DZ_RS_INNER','Right stick inner deadzone',0.10,'radial','STR_OPT_DEADZONE_R range 0.00-0.30'),
 ('DZ_RS_OUTER','Right stick outer deadzone',0.97,'radial',''),
 ('DZ_TRIGGER','Trigger threshold',0.15,'axis','Digital press point for RT/LT'),
 ('LOOK_CURVE','Right stick response curve exponent',2.0,'power','Options: Linear 1.0, Default 2.0, Precise 3.0'),
 ('LOOK_YAW_PAD','Pad yaw speed at full tilt',300,'deg/s','Sensitivity 1-10, default 5 = 300; each step +-12%'),
 ('LOOK_PITCH_PAD','Pad pitch speed at full tilt',200,'deg/s',''),
 ('LOOK_RAMP','Pad full-tilt acceleration ramp',0.25,'s','Yaw rises from 70% to 100% over 0.25 s at >0.95 tilt'),
 ('LOOK_MOUSE','Mouse sensitivity',0.07,'deg/count','Raw input, no OS acceleration; default 0.07 deg per count'),
 ('ADS_SENS','ADS sensitivity scaling',1.33,'coefficient','Monitor-distance matching at 133% so mouse feel stays the same across zoom; pad uses (1/zoom)^0.6'),
 ('LOCK_SWITCH_FLICK','Lock switch flick magnitude',0.6,'tilt','Must return under 0.3 before the next flick'),
 ('LOCK_SWITCH_CD','Lock switch cooldown',0.2,'s',''),
 ('MOUSE_FLICK','Mouse lock switch',220,'counts in 0.1 s',''),
]
wr('input_timing.csv', ['id','name','value','unit','notes'], T)

# ---------------------------------------------------------------- aim assist per firearm class
FC = rd('items/firearm_classes.csv')
AA = {'PST':(4.0,0.40,30),'ARF':(3.5,0.35,25),'SCT':(2.5,0.30,20),'SMG':(4.5,0.40,30),'SHG':(5.0,0.45,35),
      'SNP':(1.5,0.25,10),'LCH':(3.0,0.30,15),'LNC':(2.5,0.30,20)}
rows = []
for f in FC:
    c = f['class_id'][-3:]; ang, fr, pull = AA[c]
    rng = float(f['falloff_end_m']) if float(f['falloff_end_m']) > 0 else 60
    rows.append((f['class_id'], f['name'], ang, rng, fr, pull, round(ang*1.5,2), round(min(fr+0.2,0.7),2), 'Y' if c not in ('SNP',) else 'N', 6, 0.25,
                 'Pad only. Off in PvP Arena. Assist columns apply with STR_OPT_ASSIST'))
rows.append(('VEH_TURRET','Hauler turret',3.0,80,0.35,20,4.5,0.55,'N','','','Pad only'))
rows.append(('VEH_FLYER_GUN','Flyer bolts',3.5,90,0.35,25,5.25,0.55,'N','','','Pad only'))
wr('aim_assist.csv', ['class_id','name','autoaim_cone_deg','autoaim_range_m','friction_slowdown','magnetism_pull_deg_s','assist_cone_deg','assist_friction','ads_snap','ads_snap_max_deg','ads_snap_window_s','notes'], rows)

# ---------------------------------------------------------------- camera modes
CAM = [  # id, view, dist, pivot_right, pivot_up, fov_add, pitch_min, pitch_max, pos_lag, blend_in_s, notes
 ('CAM_EXPLORE','3P',3.6,0.45,1.55,0,-70,60,10,0.30,'Auto-recentre behind player after 2.5 s of movement without look input; option off'),
 ('CAM_COMBAT','3P',4.2,0.35,1.50,2,-60,55,12,0.40,'Enters when any enemy is aware within 25 m; leaves 4 s after combat ends'),
 ('CAM_LOCKON','3P',4.5,0.30,1.60,2,-35,40,14,0.20,'Framing rules in camera_rules.csv'),
 ('CAM_ADS_1P','1P',0,0,1.62,'per weapon',-85,85,0,'ads_ms','Eye socket; body visible (true first person), head mesh hidden, full-body shadow kept'),
 ('CAM_OTS_AIM','3P',1.6,0.60,1.60,'per weapon',-80,80,20,'ads_ms','Option "Aim Camera: Over Shoulder" for motion comfort; plan 5.4 fallback. Forced 1P in PvP Arena'),
 ('CAM_SPRINT','3P',4.0,0.40,1.50,6,-60,55,8,0.35,'FOV +6 at full sprint (scaled by shake slider)'),
 ('CAM_INTERIOR','3P',2.6,0.40,1.45,0,-60,50,12,0.60,'Auto inside volumes with ceiling under 3.5 m'),
 ('CAM_LADDER','3P',3.0,0.00,1.40,0,-80,70,10,0.30,''),
 ('CAM_SWIM','3P',3.8,0.30,0.60,0,-50,60,8,0.40,''),
 ('CAM_LOWGRAV','3P',4.4,0.40,1.55,4,-80,70,6,0.50,'Looser lag to sell float'),
 ('CAM_MOUNT','3P',5.5,0.00,2.40,3,-60,50,9,0.40,'Gallop FOV +5, glide distance 7.0 and FOV +8'),
 ('CAM_VEH_SKIMMER','3P',6.5,0.00,2.00,4,-30,45,7,0.35,'Speed FOV +10 at top speed; boost +6 more'),
 ('CAM_VEH_HAULER','3P',8.5,0.00,3.20,2,-30,45,6,0.40,''),
 ('CAM_VEH_GUNNER','1P',0,0,0,'turret',-20,60,0,0.25,'Turret sight; x2 zoom on LT'),
 ('CAM_VEH_PASSENGER','3P/1P',5.0,0.50,2.20,0,-60,60,8,0.30,'1P when aiming own firearm'),
 ('CAM_VEH_FLYER','3P',10.0,0.00,2.50,6,-80,80,5,0.40,''),
 ('CAM_DOWNED','3P',3.0,0.00,0.70,-4,-40,20,6,0.60,'Desaturate 40%'),
 ('CAM_SPECTATE','3P',4.5,0.30,1.60,0,-60,55,10,0.60,'Uses the spectated player\'s camera mode'),
 ('CAM_DEATH','3P',6.0,0.00,2.00,0,-60,20,2,1.20,'Slow pull-back and up over 2 s before the death screen'),
 ('CAM_FINISHER','3P',3.2,0.80,1.40,-6,-30,30,0,0.10,'Crit, riposte and backstab; option "Critical Cameras" Off keeps CAM_LOCKON'),
 ('CAM_BOSS_INTRO','cine',0,0,0,0,0,0,0,0.00,'Authored per boss; skippable after first view (IA_CINEMATIC_SKIP_CINE)'),
 ('CAM_BOSS_ARENA','3P','4.5 + 0.35 x (Height m - 2)',0.30,'1.6 + 0.25 x (Height m - 2)','+1 per 3 m of boss height above 2 m, max +8',-40,45,12,0.50,'Applied on lock-on to any actor over 3 m tall (bosses.csv / enemies.csv Height m)'),
 ('CAM_DIALOGUE','3P',1.8,0.55,1.65,-8,-15,15,0,0.50,'Over-shoulder on the NPC; Ostra lines keep gameplay camera'),
 ('CAM_LOCKPICK','fixed',0.6,0,0,-15,0,0,0,0.30,'Close-up on the lock'),
 ('CAM_MENU_INSPECT','fixed',3.2,0,1.10,-10,-20,30,0,0.30,'Character preview in inventory and wardrobe; RS rotates'),
 ('CAM_PHOTO','free',0,0,0,'STR_PHOTO_FOV 20-110',-89,89,0,0.20,'Tether 8 m, collision on, time frozen solo'),
 ('CAM_CINEMATIC','cine',0,0,0,0,0,0,0,0.00,'Letterbox 2.39:1 optional'),
 ('CAM_FORGE','free',0,0,0,0,-89,89,0,0.20,'No tether inside the editing volume'),
]
wr('camera_modes.csv', ['cam_id','view','distance_m','pivot_right_m','pivot_up_m','fov_add_deg','pitch_min_deg','pitch_max_deg','position_lag_per_s','blend_in_s','notes'], CAM)

# ---------------------------------------------------------------- per-weapon camera offsets
MC = {r['class_id'][-3:]: r for r in rd('items/melee_classes.csv')}
MELEE = [('STS','Straight Sword',2.2),('CRV','Curved Sword',2.1),('GRS','Greatsword',2.9),('AXE','Axe',2.1),('HMR','Hammer',2.3),
         ('POL','Polearm',3.2),('FST','Fist',1.2),('DGR','Dagger',1.5),('SHD','Shield',1.6),('TWB','Twinblade',2.4),
         ('GAX','Greataxe',3.0),('GHM','Greathammer',2.8)]
rows = []
for c, n, reach in MELEE:
    reach = float(MC[c]['reach_m']) if c in MC else reach
    d = round(0.15 * (reach - 2.0), 2)
    rows.append(('ITM_CLS_'+c, n, 'melee', round(3.6+d,2), round(4.2+d,2), round(4.5+d,2), round(0.35 - (0.05 if reach > 2.5 else 0),2),
                 round(1.50 + (0.05 if reach > 2.5 else 0),2), '', '', '', '', '', 'Distance grows 0.15 m per metre of reach over 2 m'))
VM = {'PST':(62,0.0),'ARF':(60,0.4),'SCT':(58,0.6),'SMG':(64,0.3),'SHG':(62,0.5),'SNP':(56,1.0),'LCH':(60,0.6),'LNC':(58,0.7)}
for f in FC:
    c = f['class_id'][-3:]; z = float(f['zoom']); vfov, sway = VM[c]
    rows.append((f['class_id'], f['name'], 'firearm', 3.6, 4.2, 4.5, 0.40, 1.55,
                 f"base / {z}", f['ads_ms'], vfov, sway, 'Y' if c in ('SNP','LNC','SCT') else 'N',
                 'ADS FOV = player FOV / zoom (firearm_classes zoom); transition = ads_ms; 3P carry pose unchanged'))
wr('camera_weapon_offsets.csv', ['class_id','name','kind','explore_dist_m','combat_dist_m','lockon_dist_m','pivot_right_m','pivot_up_m',
    'ads_fov','ads_ms','viewmodel_fov','scope_sway_deg','scope_overlay','notes'], rows)

# ---------------------------------------------------------------- camera rules
CR = [
 ('FOV_BASE','Base horizontal FOV',75,'deg','Range 70-110 on all platforms (STR_OPT_FOV_D); 3P and 1P use the same slider; console default 75, PC 80'),
 ('FOV_1P_SEPARATE','First-person FOV offset',0,'deg','Optional separate slider -10 to +10 for ADS hip view'),
 ('SWITCH_TO_1P','3P to 1P on aim',"ads_ms",'s','Camera slides forward along the aim ray into the eye socket; player mesh fades 0.1 s before arrival to avoid clipping'),
 ('SWITCH_TO_3P','1P to 3P on release',0.18,'s','Ease-out; aim direction kept so the 3P crosshair lands on the same point'),
 ('SWITCH_ROLL','Roll in ADS',1,'flag','Exits to 3P; re-enters after roll if aim still held'),
 ('SWITCH_HEAVY','Heavy pressed in ADS',1,'flag','Exits to 3P and performs the buffered heavy'),
 ('SWITCH_SPRINT','Sprint in ADS',1,'flag','Exits ADS'),
 ('SWITCH_HIT','Hit while in ADS',0,'flag','Stays in 1P; flinch kick only (feel_hit_types TAKEN_*)'),
 ('SWITCH_LOCKED','Aim while locked on',20,'deg','ADS snaps to target centre if within 20 deg; lock suspends; on release lock resumes if target alive, within 25 m and visible'),
 ('LOCK_ACQUIRE_RANGE','Lock-on acquire range',20,'m','Bosses 40 m'),
 ('LOCK_BREAK_RANGE','Lock-on break range',30,'m','Bosses 60 m'),
 ('LOCK_LOS_GRACE','Lock kept without line of sight',1.5,'s',''),
 ('LOCK_SCORE','Target choice score',"0.6 x (1 - angle/60) + 0.4 x (1 - dist/range)",'formula','Angle from camera centre; awake hostile only; prefers last-hit target on ties'),
 ('LOCK_FRAMING','Target screen height',0.42,'screen y','Camera pitches so target chest sits at 42% from top; player stays in lower third'),
 ('LOCK_PITCH_BIAS','Look-down on small targets',-8,'deg','Targets under 1.2 m'),
 ('LOCK_POINTS','Multi-point lock on big actors',"Height m > 3",'rule','Lock points from bosses.csv "Weak points / parts" plus head and core; RS flick cycles points on the same boss'),
 ('LOCK_AUTO','Auto lock-on option',0,'flag','STR_OPT_AUTO_LOCK: off by default; on = locks the nearest attacker when you attack'),
 ('LOCK_SWITCH_MODE','Switch method',"Flick",'enum','STR_OPT_LOCK_SWITCH_FLICK or _BUTTON (button = RS click cycles, hold = unlock)'),
 ('LOCK_SOFT','Soft lock when unlocked',0.35,'strength','Attacks rotate toward the nearest enemy within 60 deg and 4 m; option 0-1'),
 ('COLL_PROBE','Collision probe radius',0.25,'m','Sphere sweep from pivot to desired position'),
 ('COLL_PULL_IN','Pull-in speed',0,'s','Instant'),
 ('COLL_EASE_OUT','Ease back out',0.40,'s',''),
 ('COLL_IGNORE','Ignored by camera collision',"foliage, small props < 0.5 m, characters, VFX",'list','Characters between camera and player dither-fade to 25%'),
 ('COLL_NEAR_FADE','Player fade when camera close',0.6,'m','Player mesh fades to 30% opacity inside 0.6 m'),
 ('COLL_NEAR_CLIP','Near clip plane',0.05,'m','1P 0.03'),
 ('RECENTRE_DELAY','Auto recentre delay',2.5,'s','Explore only; never in combat'),
 ('RECENTRE_SPEED','Auto recentre speed',90,'deg/s',''),
 ('FALL_LOOK','Look-down when falling',-25,'deg','After 0.6 s of falling'),
 ('BOB_3P','3P camera bob',0,'m','None'),
 ('BOB_1P','1P head bob',0.012,'m','Walking only; slider 0-100% (A21)'),
 ('LEDGE_LOOK','Ledge peek',1,'flag','Pitch -10 deg when standing at a drop over 4 m'),
 ('ENEMY_BEHIND','Off-screen attacker hint',1,'flag','No camera turn; HUD UV-024 edge arcs only (pillar: readable fights)'),
 ('MOTION_BLUR','Motion blur',"camera off, per-object on",'enum','Toggle A22'),
 ('PVP_RULES','PvP Arena camera',"1P aim forced, FOV 70-110 allowed, OTS off",'rule','Parity'),
]
wr('camera_rules.csv', ['rule_id','name','value','unit','notes'], CR)

# ---------------------------------------------------------------- game feel: presets
SHAKE = [  # id, amp_deg, freq_hz, dur_s, falloff, shape
 ('SHK_NONE',0,0,0,'-','-'),('SHK_TICK',0.15,30,0.08,'linear','perlin'),('SHK_LIGHT',0.35,25,0.12,'linear','perlin'),
 ('SHK_MED',0.7,20,0.18,'ease-out','perlin'),('SHK_HEAVY',1.2,16,0.28,'ease-out','perlin'),('SHK_CRUSH',2.0,12,0.40,'ease-out','perlin'),
 ('SHK_BOOM',2.6,10,0.60,'distance 0-15 m','perlin'),('SHK_RUMBLE_LONG',0.5,8,1.50,'linear','sine'),('SHK_LAND',0.9,18,0.20,'ease-out','vertical only'),
]
wr('shake_presets.csv', ['shake_id','amplitude_deg','frequency_hz','duration_s','falloff','shape'], SHAKE)
RUM = [  # id, low, high, ms, envelope   (low = heavy motor, high = light motor)
 ('RUM_NONE',0,0,0,'-'),('RUM_TICK',0.0,0.25,40,'square'),('RUM_LIGHT',0.15,0.35,70,'decay'),('RUM_MED',0.35,0.45,110,'decay'),
 ('RUM_HEAVY',0.65,0.50,170,'decay'),('RUM_CRUSH',0.95,0.70,260,'decay'),('RUM_BOOM',1.0,0.6,450,'distance decay'),
 ('RUM_PULSE',0.25,0.0,120,'heartbeat 2 pulses'),('RUM_HUM',0.10,0.10,0,'loop while active'),('RUM_SHOT_LIGHT',0.05,0.40,35,'square'),
 ('RUM_SHOT_MED',0.25,0.50,60,'square'),('RUM_SHOT_HEAVY',0.70,0.60,140,'decay'),
]
wr('rumble_presets.csv', ['rumble_id','low_freq_motor','high_freq_motor','duration_ms','envelope'], RUM)
# DualSense adaptive trigger effects. Positions 0-9 along travel, strength 0-8 (Sony effect parameter ranges).
TRG = [
 ('TRG_OFF','Off','-','-','-','-'),
 ('TRG_AIM','Feedback',2,'-',3,'L2 aim: light resistance from 20% travel'),
 ('TRG_HEAVY_LIGHT','Weapon',3,6,3,'R2 heavy, weight under 5'),
 ('TRG_HEAVY_MED','Weapon',3,6,5,'R2 heavy, weight 5-10'),
 ('TRG_HEAVY_BIG','Weapon',2,6,7,'R2 heavy, weight over 10; charged heavy holds at position 6'),
 ('TRG_SEMI','Weapon',4,7,6,'Pistol, Scout: click break at 70%'),
 ('TRG_AUTO','Vibration',3,'rpm/60 Hz',4,'Auto Rifle, SMG while firing'),
 ('TRG_SHOTGUN','Weapon',3,7,8,'Shotgun'),
 ('TRG_SNIPER','Weapon',5,8,7,'Sniper: long pull, hard break'),
 ('TRG_LAUNCHER','Feedback',1,'-',8,'Launcher: heavy all the way'),
 ('TRG_LANCE','Vibration',2,'30 Hz rising to 60 Hz over charge',5,'Shard Lance charge'),
 ('TRG_EMPTY','Feedback',0,'-',0,'Dry fire: trigger goes slack'),
 ('TRG_OVERHEAT','Vibration',0,'12 Hz',6,'Turret overheat'),
 ('TRG_THROTTLE','Feedback',1,'-','2 + speed/10','Vehicle throttle (R2)'),
 ('TRG_BRAKE','Feedback',3,'-',5,'Vehicle brake (L2)'),
 ('TRG_BOW_STRING','Feedback',0,'-',2,'Mounted ADS'),
]
wr('trigger_effects.csv', ['trigger_id','mode','start_pos','end_pos_or_freq','strength','use'], TRG)

# ---------------------------------------------------------------- hit types
# id, group, hitstop_att_f, hitstop_vic_f, shake, kick_pitch, kick_yaw, kick_return_s, fov_punch, rumble, ds_haptic, time_scale, sfx, vfx, notes
H = [
 ('HIT_LIGHT','melee out',4,5,'SHK_LIGHT',0.4,0.3,0.10,0,'RUM_LIGHT','HPT_IMPACT_LIGHT',1,'Play_SFX_MeleeWeapons_{Class}_HitFlesh / HitArmor','VFX_HIT_{DMG}_S','Light 1-3'),
 ('HIT_HEAVY','melee out',7,8,'SHK_MED',0.8,0.4,0.14,0.5,'RUM_MED','HPT_IMPACT_MED',1,'Play_SFX_MeleeWeapons_{Class}_HitFlesh','VFX_HIT_{DMG}_M',''),
 ('HIT_CHARGED','melee out',10,11,'SHK_HEAVY',1.2,0.5,0.18,1.0,'RUM_HEAVY','HPT_IMPACT_HEAVY',1,'Play_SFX_MeleeWeapons_{Class}_HitFlesh','VFX_HIT_{DMG}_L',''),
 ('HIT_RUNNING','melee out',6,7,'SHK_MED',0.7,0.3,0.12,0.5,'RUM_MED','HPT_IMPACT_MED',1,'Play_SFX_MeleeWeapons_{Class}_HitFlesh','VFX_HIT_{DMG}_M',''),
 ('HIT_JUMP','melee out',8,9,'SHK_HEAVY',1.4,0,0.16,0.5,'RUM_HEAVY','HPT_IMPACT_HEAVY',1,'Play_SFX_MeleeWeapons_{Class}_HitFlesh','VFX_HIT_{DMG}_L','Plus SHK_LAND on landing'),
 ('HIT_GUARD_COUNTER','melee out',9,10,'SHK_HEAVY',1.0,0.6,0.16,1.0,'RUM_HEAVY','HPT_IMPACT_HEAVY',1,'Play_SFX_MeleeWeapons_{Class}_HitFlesh','VFX_HIT_{DMG}_L',''),
 ('HIT_WEAPON_ART','melee out',8,9,'SHK_HEAVY',1.0,0.5,0.16,1.0,'RUM_HEAVY','HPT_IMPACT_HEAVY',1,'SFX_ART_* (weapon_arts.csv)','VFX_ART_*','Per art override allowed'),
 ('HIT_RIPOSTE','melee crit',14,16,'SHK_CRUSH',1.6,0,0.30,-4,'RUM_CRUSH','HPT_CRIT',0.85,'Play_SFX_Ui_Interface_Crit + class HitFlesh','VFX_HIT_CRIT','Time scale 0.85 for 0.25 s (solo only)'),
 ('HIT_BACKSTAB','melee crit',14,16,'SHK_CRUSH',1.4,0,0.30,-4,'RUM_CRUSH','HPT_CRIT',0.85,'Play_SFX_Ui_Interface_Crit + class HitFlesh','VFX_HIT_CRIT','Solo only time scale'),
 ('HIT_STANCE_CRIT','melee crit',16,18,'SHK_CRUSH',1.8,0,0.32,-5,'RUM_CRUSH','HPT_CRIT',0.85,'Play_SFX_Ui_Interface_Crit + class HitFlesh','VFX_HIT_CRIT','Critical on a stance-broken enemy'),
 ('HIT_STANCE_BREAK','melee event',10,12,'SHK_HEAVY',1.0,0,0.20,1.5,'RUM_HEAVY','HPT_BREAK',1,'Play_SFX_Combat_StanceBreak','VFX_STANCE_BREAK','Moment the stance meter empties; enemy staggers 120 f (boss 150)'),
 ('HIT_WARD_BREAK','melee event',8,8,'SHK_MED',0.6,0,0.15,1.0,'RUM_MED','HPT_GLASS',1,'Play_SFX_Combat_WardShatter_{Element}','VFX_WARD_BREAK_{Element}','Enemy Ward hits 0; any source'),
 ('HIT_WARD','melee out',3,4,'SHK_TICK',0.3,0.2,0.08,0,'RUM_TICK','HPT_SHIELD',1,'Play_SFX_MeleeWeapons_{Class}_HitWard','VFX_HIT_WARD_{Element}','Hit absorbed by Ward'),
 ('HIT_ARMORED','melee out',5,3,'SHK_LIGHT',0.4,0.2,0.10,0,'RUM_LIGHT','HPT_METAL',1,'Play_SFX_MeleeWeapons_{Class}_HitArmor','VFX_HIT_SPARK','Resistance 0.4 or higher for the damage type'),
 ('HIT_KILL','melee event',3,0,'SHK_LIGHT',0.3,0,0.10,0,'RUM_LIGHT','HPT_IMPACT_MED',1,'class HitFlesh','VFX_HIT_{DMG}_M','Added on top of the killing hit; capped so total hitstop <= 16'),
 ('HIT_DEFLECT','melee out',6,0,'SHK_MED',0.8,1.0,0.18,0,'RUM_MED','HPT_METAL',1,'Play_SFX_MeleeWeapons_{Class}_Block','VFX_HIT_SPARK','Attack bounces off a wall or an enemy shield; recovery +12 f'),
 ('HIT_WHIFF','melee out',0,0,'SHK_NONE',0.1,0,0.08,0,'RUM_NONE','HPT_NONE',1,'Play_SFX_MeleeWeapons_{Class}_WhooshLight','-','No hitstop on miss'),
 ('DEF_BLOCK_LIGHT','defense',4,4,'SHK_LIGHT',0.4,0.3,0.10,0,'RUM_LIGHT','HPT_SHIELD',1,'Play_SFX_MeleeWeapons_{Class}_Block','VFX_BLOCK_SPARK',''),
 ('DEF_BLOCK_HEAVY','defense',7,7,'SHK_MED',0.9,0.4,0.15,0,'RUM_MED','HPT_SHIELD',1,'Play_SFX_MeleeWeapons_{Class}_Block','VFX_BLOCK_SPARK','Incoming damage mult >= 1.2'),
 ('DEF_GUARD_BREAK','defense',0,12,'SHK_HEAVY',1.4,0.8,0.25,0,'RUM_HEAVY','HPT_BREAK',1,'Play_SFX_MeleeWeapons_{Class}_GuardBreak','VFX_GUARD_BREAK','Player Breath hits 0 while blocking'),
 ('DEF_PARRY','defense',10,14,'SHK_MED',0.6,0,0.15,-3,'RUM_HEAVY','HPT_PARRY',0.9,'Play_SFX_MeleeWeapons_{Class}_Parry','VFX_PARRY_FLASH','Flash obeys Reduce Flashing'),
 ('DEF_PERFECT_DODGE','defense',0,0,'SHK_NONE',0,0,0,0,'RUM_TICK','HPT_WHOOSH',1,'Play_SFX_Player_Kindled_PerfectDodge','VFX_DODGE_TRAIL','Enemy active frame overlapped i-frames'),
 ('DEF_ROLL','defense',0,0,'SHK_NONE',0,0,0,0,'RUM_NONE','HPT_FOOTSTEP',1,'-','-','Haptic only: body roll thump'),
 ('TAKEN_LIGHT','incoming',0,4,'SHK_LIGHT',1.0,0.6,0.15,0,'RUM_MED','HPT_HURT_LIGHT',1,'Play_SFX_PlayerVocals_BodyType{AB}_HurtLight','VFX_SCREEN_HIT_EDGE','Damage mult < 1.2 (enemy_attacks / boss_moves)'),
 ('TAKEN_HEAVY','incoming',0,8,'SHK_HEAVY',2.0,1.0,0.25,0,'RUM_HEAVY','HPT_HURT_HEAVY',1,'Play_SFX_PlayerVocals_BodyType{AB}_HurtHeavy','VFX_SCREEN_HIT_EDGE','Damage mult >= 1.2'),
 ('TAKEN_GRAB','incoming',0,0,'SHK_RUMBLE_LONG',0.5,0.5,0.3,-3,'RUM_PULSE','HPT_GRAB',1,'Play_SFX_Player_Grabbed','-','boss_moves Damage type Grab; shake loops for the grab duration'),
 ('TAKEN_WARD','incoming',0,2,'SHK_TICK',0.5,0.3,0.10,0,'RUM_TICK','HPT_SHIELD',1,'Play_SFX_Player_WardHit','VFX_SCREEN_WARD_RIPPLE','Hit fully absorbed by player Ward'),
 ('TAKEN_WARD_BREAK','incoming',0,6,'SHK_MED',1.0,0,0.2,2,'RUM_MED','HPT_GLASS',1,'Play_SFX_Player_Kindled_WardBreak','VFX_SCREEN_WARD_SHATTER',''),
 ('TAKEN_KNOCKDOWN','incoming',0,10,'SHK_HEAVY',2.5,0,0.3,0,'RUM_HEAVY','HPT_HURT_HEAVY',1,'Play_SFX_Player_Knockdown','-','Stability: 3 staggers in 8 s'),
 ('TAKEN_STATUS','incoming',0,0,'SHK_TICK',0.2,0,0.1,0,'RUM_TICK','HPT_STATUS_{Status}',1,'Play_SFX_Status_{Status}_Proc','VFX_STATUS_{Status}_SCREEN','Status proc on player, per STS_*'),
 ('TAKEN_EXPLOSION','incoming',0,6,'SHK_BOOM',2.0,1.0,0.3,0,'RUM_BOOM','HPT_BOOM',1,'Play_SFX_Explosion_Near','-','Scaled by distance 0-15 m'),
 ('LOW_HEALTH','state',0,0,'SHK_NONE',0,0,0,0,'RUM_PULSE','HPT_HEARTBEAT',1,'Play_SFX_Player_Kindled_LowHealthHeartbeat','VFX_SCREEN_LOW_HEALTH','Under 25% Health; pulse every 1.0 s'),
 ('PLAYER_DEATH','state',0,0,'SHK_MED',0,0,0,0,'RUM_HEAVY','HPT_DEATH',0.6,'Play_SFX_Player_Kindled_Death','-','Time scale 0.6 for 0.5 s solo'),
 ('GUN_HIT_BODY','gun out',0,2,'SHK_NONE',0,0,0,0,'RUM_NONE','HPT_NONE',1,'Play_SFX_Ui_Interface_HitMarker','VFX_HIT_KIN','No hitstop on guns; victim flinch only'),
 ('GUN_HIT_HEAD','gun out',0,3,'SHK_NONE',0,0,0,0,'RUM_TICK','HPT_TICK',1,'Play_SFX_Ui_Interface_Headshot','VFX_HIT_HEAD','Only x2 after Ward is down'),
 ('GUN_HIT_WARD','gun out',0,1,'SHK_NONE',0,0,0,0,'RUM_NONE','HPT_NONE',1,'Play_SFX_Impacts_Ward_{Element}','VFX_HIT_WARD_{Element}',''),
 ('GUN_KILL','gun out',0,0,'SHK_NONE',0,0,0,0,'RUM_TICK','HPT_TICK',1,'Play_SFX_Ui_Interface_KillConfirm','VFX_KILL_DISSOLVE',''),
 ('ABL_CAST','ability',0,0,'SHK_LIGHT',0.3,0,0.1,0,'RUM_LIGHT','HPT_CAST_{Element}',1,'Play_SFX_Weave_{Element}_Cast','ABL VFX','Per ABL_* slot'),
 ('ABL_STRIKE','ability',6,7,'SHK_MED',0.8,0,0.15,0.5,'RUM_MED','HPT_CAST_{Element}',1,'Play_SFX_Weave_{Element}_Strike','ABL VFX',''),
 ('ABL_STEP','ability',0,0,'SHK_NONE',0,0,0,2,'RUM_LIGHT','HPT_WHOOSH',1,'Play_SFX_Weave_{Element}_Step','ABL VFX','FOV punch +2 for 0.2 s'),
 ('ABL_SURGE','ability',12,10,'SHK_CRUSH',1.5,0,0.4,4,'RUM_CRUSH','HPT_SURGE_{Element}',0.8,'Play_SFX_Weave_{Element}_Surge','ABL VFX','Activation; 0.8 time scale for 0.3 s solo'),
 ('RESONANCE','ability',0,0,'SHK_RUMBLE_LONG',0.8,0,0.3,3,'RUM_HEAVY','HPT_RESONANCE',1,'RES SFX','RES VFX','Per RES_* row'),
 ('LAND_SOFT','traversal',0,0,'SHK_NONE',0,0,0,0,'RUM_TICK','HPT_FOOTSTEP',1,'-','-','Fall under 3 m'),
 ('LAND_HARD','traversal',0,0,'SHK_LAND',1.2,0,0.2,0,'RUM_MED','HPT_LAND',1,'Play_SFX_Player_Kindled_FallDamage','VFX_LAND_DUST','Fall 3-8 m'),
 ('DOUBLE_JUMP','traversal',0,0,'SHK_NONE',0,0,0,1,'RUM_LIGHT','HPT_WHOOSH',1,'Strider double jump','-',''),
 ('GLIDE','traversal',0,0,'SHK_NONE',0,0,0,4,'RUM_HUM','HPT_WIND',1,'Strider glide loop','-','Loop while gliding'),
 ('MOUNT_GALLOP','traversal',0,0,'SHK_NONE',0,0,0,0,'RUM_TICK','HPT_HOOF',1,'-','-','Per footfall, alternating L/R haptic'),
 ('VEH_BOOST','vehicle',0,0,'SHK_RUMBLE_LONG',0,0,0,6,'RUM_HUM','HPT_ENGINE',1,'Skimmer boost','-','For 3 s'),
 ('VEH_COLLIDE','vehicle',0,4,'SHK_HEAVY',1.5,1.0,0.3,0,'RUM_HEAVY','HPT_CRASH',1,'Vehicle impact','-','Scaled by impact speed / 20 m/s'),
 ('VEH_PART_BREAK','vehicle',0,0,'SHK_MED',0.8,0,0.2,0,'RUM_MED','HPT_BREAK',1,'Vehicle part destroyed','-','Hull, engine, wheel, wing'),
 ('VEH_HIJACK','vehicle',6,6,'SHK_MED',0.8,0,0.2,-3,'RUM_HEAVY','HPT_IMPACT_HEAVY',1,'Hijack','-','STR_ACH_56'),
 ('BOSS_ROAR','boss',0,0,'SHK_RUMBLE_LONG',0.6,0,0.3,0,'RUM_PULSE','HPT_ROAR',1,'Boss roar','-','Enrage and phase change (boss_phases.csv)'),
 ('BOSS_SLAM_NEAR','boss',0,0,'SHK_BOOM',1.5,0,0.3,0,'RUM_BOOM','HPT_BOOM',1,'-','-','Boss_moves with AoE radius over 4 m, within 2x radius'),
 ('UI_LEVEL_UP','ui',0,0,'SHK_NONE',0,0,0,0,'RUM_LIGHT','HPT_CHIME',1,'Play_SFX_Ui_Interface_LevelUpStinger','-',''),
 ('UI_SHARDBORN_DROP','ui',0,0,'SHK_NONE',0,0,0,0,'RUM_MED','HPT_CHIME',1,'Shardborn drop','-',''),
 ('UI_ANCHOR_LIT','ui',0,0,'SHK_TICK',0,0,0,0,'RUM_LIGHT','HPT_CHIME',1,'Play_SFX_Player_Kindled_AnchorLight','-',''),
]
wr('feel_hit_types.csv', ['hit_id','group','hitstop_attacker_f','hitstop_victim_f','shake_id','cam_kick_pitch_deg','cam_kick_yaw_deg','kick_return_s',
   'fov_punch_deg','rumble_id','ds_haptic_id','time_scale','sfx_event','vfx_hook','notes'], H)

# ---------------------------------------------------------------- per weapon class modifiers
# melee: hitstop mult, shake mult, rumble mult, kick mult, heavy trigger, haptic texture
MCM = {'STS':(1.0,1.0,1.0,1.0,'TRG_HEAVY_LIGHT','HPT_TEX_BLADE'),'CRV':(0.85,0.9,0.9,0.9,'TRG_HEAVY_LIGHT','HPT_TEX_BLADE'),
       'GRS':(1.3,1.3,1.3,1.2,'TRG_HEAVY_BIG','HPT_TEX_BLADE_HEAVY'),'AXE':(1.15,1.1,1.1,1.1,'TRG_HEAVY_MED','HPT_TEX_CHOP'),
       'HMR':(1.4,1.4,1.4,1.3,'TRG_HEAVY_BIG','HPT_TEX_BLUNT'),'POL':(0.95,1.0,1.0,1.0,'TRG_HEAVY_MED','HPT_TEX_PIERCE'),
       'FST':(0.7,0.8,0.9,0.8,'TRG_HEAVY_LIGHT','HPT_TEX_BLUNT'),'DGR':(0.6,0.7,0.7,0.7,'TRG_HEAVY_LIGHT','HPT_TEX_PIERCE'),
       'SHD':(1.1,1.1,1.2,1.0,'TRG_HEAVY_MED','HPT_TEX_BLUNT'),'TWB':(0.75,0.8,0.8,0.8,'TRG_HEAVY_LIGHT','HPT_TEX_BLADE'),
       'GAX':(1.4,1.4,1.4,1.3,'TRG_HEAVY_BIG','HPT_TEX_CHOP'),'GHM':(1.5,1.5,1.5,1.4,'TRG_HEAVY_BIG','HPT_TEX_BLUNT')}
# firearms: recoil pitch/shot, yaw range, recovery s, fire shake, fire rumble, trigger, fov punch
FCM = {'PST':(0.9,0.3,0.12,'SHK_TICK','RUM_SHOT_LIGHT','TRG_SEMI',0),'ARF':(0.45,0.25,0.10,'SHK_TICK','RUM_SHOT_LIGHT','TRG_AUTO',0),
       'SCT':(1.3,0.2,0.18,'SHK_LIGHT','RUM_SHOT_MED','TRG_SEMI',0),'SMG':(0.35,0.35,0.08,'SHK_TICK','RUM_SHOT_LIGHT','TRG_AUTO',0),
       'SHG':(3.0,0.6,0.30,'SHK_MED','RUM_SHOT_HEAVY','TRG_SHOTGUN',1),'SNP':(4.0,0.4,0.45,'SHK_MED','RUM_SHOT_HEAVY','TRG_SNIPER',0),
       'LCH':(3.5,0.5,0.50,'SHK_HEAVY','RUM_SHOT_HEAVY','TRG_LAUNCHER',2),'LNC':(2.5,0.2,0.35,'SHK_MED','RUM_SHOT_HEAVY','TRG_LANCE',1)}
rows = []
for c, n, _ in MELEE:
    hm, sm, rm, km, trg, tex = MCM[c]
    rows.append(('ITM_CLS_'+c, n, 'melee', hm, sm, rm, km, trg, tex, '', '', '', '', '', 'TRG_AIM'))
for f in FC:
    c = f['class_id'][-3:]; p, y, rec, sh, ru, trg, fov = FCM[c]
    rows.append((f['class_id'], f['name'], 'firearm', '', '', '', '', trg, 'HPT_TEX_SHOT_'+c, p, y, rec, sh, ru, 'TRG_AIM'))
wr('feel_weapon_class.csv', ['class_id','name','kind','hitstop_mult','shake_mult','rumble_mult','kick_mult','r2_trigger','haptic_texture',
   'recoil_pitch_deg_per_shot','recoil_yaw_range_deg','recoil_recovery_s','fire_shake','fire_rumble','l2_trigger'], rows)

# ---------------------------------------------------------------- feel matrix (class x hit type), final values
SHK = {s[0]: s for s in SHAKE}
AUDN = {'Curved Sword':'CurvedBlade','Fist':'FistWeapon','Submachine Gun':'Smg'}
def an(n): return AUDN.get(n, n.replace(' ', ''))
MELEE_HITS = [h for h in H if h[1] in ('melee out','melee crit','melee event')] + [h for h in H if h[0].startswith('DEF_BLOCK') or h[0]=='DEF_PARRY']
rows = []
for c, n, _ in MELEE:
    hm, sm, rm, km, trg, tex = MCM[c]
    for h in MELEE_HITS:
        a = min(16, round(h[2]*hm)); v = min(18, round(h[3]*hm))
        amp = round(SHK[h[4]][1]*sm, 2)
        rows.append((f'FEEL_{c}_{h[0][h[0].index("_")+1:]}', 'ITM_CLS_'+c, h[0], a, v, h[4], amp, round(h[5]*km,2), round(h[6]*km,2), h[9], rm, tex,
                     h[12].replace('{Class}', an(n))))
for f in FC:
    c = f['class_id'][-3:]; n = f['name']; p, y, rec, sh, ru, trg, fov = FCM[c]
    rows.append((f'FEEL_{c}_FIRE', f['class_id'], 'GUN_FIRE', 0, 0, sh, SHK[sh][1], p, y, ru, 1.0, 'HPT_TEX_SHOT_'+c, f'Play_SFX_Firearms_{an(n)}_FireClose'))
    for h in H:
        if h[1] == 'gun out':
            rows.append((f'FEEL_{c}_{h[0][4:]}', f['class_id'], h[0], h[2], h[3], h[4], SHK[h[4]][1], h[5], h[6], h[9], 1.0, h[10], h[12]))
    rows.append((f'FEEL_{c}_RELOAD', f['class_id'], 'GUN_RELOAD', 0, 0, 'SHK_NONE', 0, 0, 0, 'RUM_TICK', 1.0, 'HPT_RELOAD', f'Play_SFX_Firearms_{an(n)}_MagIn'))
    rows.append((f'FEEL_{c}_EMPTY', f['class_id'], 'GUN_EMPTY', 0, 0, 'SHK_NONE', 0, 0, 0, 'RUM_TICK', 1.0, 'HPT_CLICK', f'Play_SFX_Firearms_{an(n)}_DryFire'))
wr('feel_matrix.csv', ['feel_id','class_id','hit_id','hitstop_attacker_f','hitstop_victim_f','shake_id','shake_amp_deg','kick_pitch_deg','kick_yaw_deg',
   'rumble_id','rumble_mult','haptic','sfx_event'], rows)
FEEL_IDS = {r[0] for r in rows}

# ---------------------------------------------------------------- map every data attack to a feel row
ATKMAP = {'Light 1':'LIGHT','Light 2':'LIGHT','Light 3':'LIGHT','Heavy':'HEAVY','Charged Heavy':'CHARGED','Running Attack':'RUNNING',
          'Jump Attack':'JUMP','Guard Counter':'GUARD_COUNTER'}
rows = []; missing = []
for r in rd('items/melee_frame_data.csv'):
    c = r['attack_id'].split('_')[2]; fid = f'FEEL_{c}_{ATKMAP[r["attack"]]}'
    if fid not in FEEL_IDS: missing.append(fid)
    rows.append((r['attack_id'], 'player melee', fid, 'Play_SFX_MeleeWeapons_'+an(r['weapon_class'])+'_WhooshLight / WhooshHeavy'))
for r in rd('items/weapon_arts.csv'):
    rows.append((r['item_id'], 'weapon art', 'HIT_WEAPON_ART x class of wielder', r['sfx']))
for r in rd('actors/weave_abilities.csv'):
    slot = r['Slot'].upper()
    rows.append((r['ABL_ID'], 'ability', 'ABL_'+slot, f"Play_SFX_Weave_{r['Element']}_{r['Slot']}"))
for r in rd('actors/resonances.csv'):
    rows.append((r['RES_ID'], 'resonance', 'RESONANCE', ''))
def incoming(dt, mult):
    if dt == 'Grab': return 'TAKEN_GRAB'
    if dt in ('Buff','Heal','Summon','None'): return 'none (no hit)'
    try: m = float(mult)
    except ValueError: m = 1
    return 'TAKEN_HEAVY' if m >= 1.2 else 'TAKEN_LIGHT'
for r in rd('actors/enemy_attacks.csv'):
    rows.append((r['ATK_ID'], 'enemy attack on player', incoming(r['Damage type'], r['Damage mult']), ''))
for r in rd('actors/boss_moves.csv'):
    f = incoming(r['Damage type'], r['Damage mult'])
    try:
        if float(r['AoE radius m']) > 4: f += ' + BOSS_SLAM_NEAR'
    except ValueError: pass
    rows.append((r['MOV_ID'], 'boss move on player', f, ''))
for r in rd('items/arena_power_weapons.csv'):
    rows.append((r['item_id'], 'arena power weapon', 'class of '+r['base_class']+' x1.2 rumble, PvP normalized', ''))
wr('attack_feel_map.csv', ['source_id','kind','feel','swing_sfx'], rows)
if missing: print('MISSING FEEL ROWS', sorted(set(missing)))

# ---------------------------------------------------------------- feel rules
FR = [
 ('Hitstop is simulation','Hitstop frames are part of the attack timeline on both sides and run on the fixed sim clock, so co-op host and guests agree. Attacker recovery and victim hitstun start after hitstop.'),
 ('Multi-target','Hitting several targets in one swing uses the largest single hitstop plus 1 frame per extra target, max +2.'),
 ('Caps','Attacker hitstop max 16 frames, victim max 18. HIT_KILL adds to the killing hit but stays under the cap.'),
 ('Multi-hit moves','Twinblade, Fist and Dagger multi-hit strings use 50% hitstop on all hits except the last.'),
 ('Firearms','No hitstop for firearms on either side; feel comes from recoil kick, haptics, hit markers and victim flinch.'),
 ('PvP','PvP Arena: victim hitstop fixed at 3 frames, time scale effects off, finisher cameras off.'),
 ('Online time scale','time_scale below 1 only applies solo and offline. Online it becomes a 0.1 s camera slow-zoom only.'),
 ('Shake stacking','Shakes add, then clamp at 3.0 deg. The newest shake of a higher tier replaces lower tiers already playing.'),
 ('Rumble stacking','Rumble takes the max of each motor across active events, not the sum.'),
 ('Distance','Shake and rumble from events not caused by or hitting the local player fall off linearly to 0 at 15 m (SHK_BOOM, RUM_BOOM).'),
 ('Co-op allies','Allies hitting enemies give the local player nothing; allies being hit give nothing.'),
 ('Settings: shake','STR_OPT_CAMERA_SHAKE 0-100% scales shake amplitude, cam kick and FOV punch. Default 100%.'),
 ('Settings: vibration','STR_OPT_VIBRATION 0-100% scales both motors and DualSense haptic gain. Default 100%.'),
 ('Settings: triggers','STR_OPT_TRIGGERS Off / Light (strength x0.5) / Full. Default Full.'),
 ('Settings: flashing','Reduce Flashing (A21) removes parry flash, Ward-break flash and screen-edge pulses; keeps hitstop.'),
 ('Reduce Motion preset','Shake 30%, FOV punch 0, head bob 0, camera motion blur off, finisher cameras off (A21, A22).'),
 ('DualSense haptics','HPT_* ids are audio-driven haptic clips authored with the SFX; texture clips (HPT_TEX_*) layer on top of impact clips per weapon class.'),
 ('Impulse triggers','Xbox impulse triggers use the trigger_effects rows as: Weapon/Feedback -> 60 ms pulse at strength/8, Vibration -> loop at amplitude/8.'),
 ('KBM','No haptics on KBM. Shake and kick still apply.'),
 ('Hit reactions','Every hit type also drives an enemy hit reaction (flinch, stagger, knockback) owned by the animation set; feel rows do not replace reactions.'),
 ('Telegraph sync','Boss telegraph SFX (boss_moves "Telegraph cue") never get rumble, so pad players read the same cue as others.'),
]
wr('feel_rules.csv', ['rule_id','rule','detail'], [(f'FEEL_R{i:02d}', a, b) for i, (a, b) in enumerate(FR, 1)])

# ---------------------------------------------------------------- settings
S = [
 ('STR_OPT_SENS_X','Controls','1-10','5','LOOK_YAW_PAD'),('STR_OPT_SENS_Y','Controls','1-10','5','LOOK_PITCH_PAD'),
 ('STR_OPT_SENS_AIM','Controls','0.5-2.0','1.0','ADS_SENS'),('STR_OPT_INVERT_Y','Controls','Off/On','Off',''),('STR_OPT_INVERT_X','Controls','Off/On','Off',''),
 ('STR_OPT_DEADZONE_L','Controls','0-30%','12%','DZ_LS_INNER'),('STR_OPT_DEADZONE_R','Controls','0-30%','10%','DZ_RS_INNER'),
 ('STR_OPT_VIBRATION','Controls','0-100%','100%','FEEL_R13'),('STR_OPT_TRIGGERS','Controls','Off/Light/Full','Full','FEEL_R14'),
 ('STR_OPT_AIM_ASSIST','Controls','0-100%','100%','aim_assist.csv'),('STR_OPT_TOGGLE_SPRINT','Controls','Hold/Toggle','Hold','RMP_08'),
 ('STR_OPT_TOGGLE_AIM','Controls','Hold/Toggle','Hold','RMP_08'),('STR_OPT_TOGGLE_BLOCK','Controls','Hold/Toggle','Hold','RMP_08'),
 ('STR_OPT_TOGGLE_CROUCH','Controls','Hold/Toggle','Toggle','RMP_08'),('STR_OPT_CAMERA_DIST','Gameplay','80-130%','100%','camera_modes distance'),
 ('STR_OPT_CAMERA_SHAKE','Gameplay','0-100%','100%','FEEL_R12'),('STR_OPT_FOV','Gameplay','70-110','75 console / 80 PC','FOV_BASE'),
 ('STR_OPT_LOCK_SWITCH','Gameplay','Flick/Button','Flick','LOCK_SWITCH_MODE'),('STR_OPT_AUTO_LOCK','Gameplay','Off/On','Off','LOCK_AUTO'),
 ('NEW: STR_OPT_AIM_CAMERA','Gameplay','First Person/Over Shoulder','First Person','CAM_OTS_AIM'),
 ('NEW: STR_OPT_CRIT_CAMERA','Gameplay','Off/On','On','CAM_FINISHER'),('NEW: STR_OPT_AUTO_RECENTRE','Gameplay','Off/On','On','RECENTRE_DELAY'),
 ('NEW: STR_OPT_SOFT_LOCK','Gameplay','0-100%','35%','LOCK_SOFT'),('NEW: STR_OPT_LOOK_CURVE','Controls','Linear/Default/Precise','Default','LOOK_CURVE'),
 ('NEW: STR_OPT_HOLD_TIME','Accessibility','0.4-1.6 s','0.8 s','TIM_HOLD_RING'),('NEW: STR_OPT_HOLD_TO_TAP','Accessibility','Off/On','Off','RMP_09'),
 ('NEW: STR_OPT_ABILITY_INPUT','Controls','Chord/Direct','Chord','PRE_DIRECT'),('NEW: STR_OPT_PRESET','Controls','input_presets.csv','Shardfall Default','input_presets.csv'),
 ('NEW: STR_OPT_GYRO','Controls','Off/On','Off','RMP_13'),('NEW: STR_OPT_HEAD_BOB','Accessibility','0-100%','100%','BOB_1P'),
 ('NEW: STR_OPT_REDUCE_FLASH','Accessibility','Off/On','Off','FEEL_R15'),('NEW: STR_OPT_REDUCE_MOTION','Accessibility','Off/On','Off','FEEL_R16'),
 ('NEW: STR_OPT_CONFIRM_SWAP','Controls','Cross confirm/Circle confirm','Cross','IA_MENU_CONFIRM'),
 ('NEW: STR_OPT_FOV_1P','Gameplay','-10 to +10','0','FOV_1P_SEPARATE'),
]
wr('settings.csv', ['string_id','tab','range','default','drives'], S)
print('BTN tokens:', len(tokens_used))

# ---------------------------------------------------------------- data requests
import re
AUD = os.path.join(OUT, '..', 'audio', 'event_map.csv')
events = {r['wwise_event'] for r in csv.DictReader(open(AUD))} if os.path.exists(AUD) else set()
need_sfx, need_vfx, need_hpt = set(), set(), set()
for fn in ('feel_hit_types.csv', 'feel_matrix.csv'):
    for r in csv.DictReader(open(os.path.join(OUT, fn))):
        for e in re.findall(r'Play_SFX_[A-Za-z0-9_{}]+', r.get('sfx_event', '')):
            if '{' not in e and e not in events: need_sfx.add(e)
        v = r.get('vfx_hook', '')
        if v.startswith('VFX_') and '*' not in v: need_vfx.add(v)
        for k in ('ds_haptic_id', 'haptic'):
            h = r.get(k, '')
            if h.startswith('HPT_') and h != 'HPT_NONE': need_hpt.add(h)
for r in csv.DictReader(open(os.path.join(OUT, 'feel_weapon_class.csv'))):
    need_hpt.add(r['haptic_texture'])
DR = []
def dr(req, table, value, reason): DR.append((f'CTL-{len(DR)+1:03d}', req, table, value, reason))
dr('add table', 'new data/input/ (or ui/)', 'input_actions.csv, input_contexts.csv, input_timing.csv, input_presets.csv, aim_assist.csv',
   'Input map as DataTables (USfInputSubsystem, Enhanced Input IMC_*); tech datatable_map.csv should list them')
dr('add table', 'new data/feel/', 'feel_hit_types.csv, feel_weapon_class.csv, feel_matrix.csv, shake_presets.csv, rumble_presets.csv, trigger_effects.csv, attack_feel_map.csv',
   'FEEL_* ids; attack_feel_map ties every ITM_ATK_, ATK_, MOV_, ABL_, RES_, ITM_ART_, ITM_PWR_ row to a feel row')
dr('add table', 'new data/camera/', 'camera_modes.csv, camera_weapon_offsets.csv, camera_rules.csv', 'CAM_* ids for USfCameraComponent modes')
dr('add column', 'items/melee_frame_data.csv', 'feel_id (FEEL_<class>_<type>)', 'Lets link.py validate the attack -> feel link')
dr('add rows', 'items/melee_classes.csv', 'ITM_CLS_GAX Greataxe, ITM_CLS_GHM Greathammer',
   'Plan 4.1 says 12 melee classes; melee_frame_data and weapons_melee already use GAX and GHM but melee_classes has only 10. Plan wins')
dr('add value', 'actors/player_base_stats.csv', 'STAT_PARRY_FRAMES 6, STAT_PARRY_ASSIST +4, STAT_RIPOSTE_WINDOW 60, STAT_GUARD_COUNTER_WINDOW 20, STAT_COMMIT_FRAME 6',
   'Timing values used by input_timing.csv; confirm they live in one owner table')
dr('add value', 'new vehicles table', 'VEH_SKIMMER, VEH_HAULER, VEH_FLYER with seats, speeds, boost 3 s / 6 s, turret overheat 4 s, part health (plan Part 1b)',
   'No vehicle table exists in data/; controls and camera reference vehicles by name only')
dr('add value', 'actors/bosses.csv', 'lock_points column (head, core, plus Weak points / parts)', 'LOCK_POINTS rule in camera_rules.csv')
dr('add strings', 'ui/strings.csv', 'STR_OPT_AIM_CAMERA, CRIT_CAMERA, AUTO_RECENTRE, SOFT_LOCK, LOOK_CURVE, HOLD_TIME, HOLD_TO_TAP, ABILITY_INPUT, PRESET, GYRO, HEAD_BOB, REDUCE_FLASH, REDUCE_MOTION, CONFIRM_SWAP, FOV_1P (+ _D descriptions)',
   'New options in settings.csv')
dr('add strings', 'ui/strings.csv', 'STR_PRESET_<id> names for the 8 rows of input_presets.csv; STR_ACTION_<action_id> display names for the remap screen (157 actions)',
   'Remap screen lists every action by name')
dr('add tokens', 'ui/README.md token list', ', '.join(sorted({r["btn_token"] for r in csv.DictReader(open(os.path.join(OUT, "input_actions.csv")))})),
   'Every BTN_ token the input map defines; all 26 tokens used in strings today are covered')
dr('add assets', 'shardfall-assets.xlsx glyphs UV-079', 'Glyphs for every binding in input_actions.csv on Xbox, PS5, KBM, Steam Deck including chords (LB+X) and hold variants',
   '180 glyphs budgeted; chord glyphs may push past that')
dr('add hooks', 'assets/asset_hooks.csv (VFX)', ', '.join(sorted(need_vfx)), 'VFX hooks named by feel_hit_types.csv')
dr('add hooks', 'assets/asset_hooks.csv (haptics, new HPT_ prefix)', ', '.join(sorted(need_hpt)), 'DualSense haptic clips, authored with SFX by audio')
dr('add events', 'design/audio/event_map.csv', ', '.join(sorted(need_sfx)), 'Events named by feel tables that the audio map does not have yet; {Class}/{Element} patterns excluded')
dr('conflict', 'design/tech/01-code-architecture.md', 'Camera mode "over-shoulder aim" -> first person ADS (CAM_ADS_1P) by default; over-shoulder only as option CAM_OTS_AIM',
   'Plan 3.0 and 3.4: aim switches to first person; over-shoulder is the plan 5.4 fallback')
dr('conflict', 'design/production/accessibility_checklist.csv A20', 'Difficulty sliders -> Assist Mode only (aim help, +4 parry frames)',
   'Plan 3.4: no difficulty menu; strings STR_OPT_DIFF_NOTE agree with the plan')
dr('conflict', 'design/production/accessibility_checklist.csv A22', 'FOV slider PC only -> all platforms 70-110', 'STR_OPT_FOV_D already says 70 to 110 with no platform limit')
dr('choice', 'world design', 'Swimming: surface only, no diving, no drowning (CTX_SWIM)', 'Plan does not mention water traversal; world thread may override')
with open(os.path.join(OUT, 'data-requests.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'request', 'target_table', 'value', 'reason']); w.writerows(DR)
print('data-requests.csv:', len(DR), 'rows;', len(need_sfx), 'sfx,', len(need_vfx), 'vfx,', len(need_hpt), 'haptics')
