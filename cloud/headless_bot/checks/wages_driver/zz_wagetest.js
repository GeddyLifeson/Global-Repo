// TEST-ONLY driver (lives in the lane, never in the repo): /wt <step> drives the real wage functions with real villagers.
const WT_CULT = 'celtic'
function wtSay(s) { console.info('[wt] ' + s) }
function wtNear(server, type) { let out = []; server.overworld().getEntities().forEach(e => { if (String(e.type) === type && e.isAlive()) out.push(e) }); return out }
function wtState() {
  let w = wageState(ECON), o = []
  Object.keys(w.workers).forEach(id => { let r = w.workers[id]; o.push(r.job + ':' + wageKey(r.employer) + ' owe=' + r.owe + ' stage=' + r.stage + (r.gone ? ' gone' : '')) })
  Object.keys(w.accounts).forEach(k => o.push('acct ' + k + ' funds=' + w.accounts[k].funds + ' unrest=' + w.accounts[k].unrest))
  return o.join(' | ')
}
function wtWeek(server) { ECON.week++; let ev = []; wageWeek(ECON, c => 1, c => (global.WT_AGE || 'IV'), wageAutomated).forEach(e => { ev.push(e.t); wageApply(e) }); wtSay('week ' + ECON.week + ' events=' + ev.join(',')); wtSay(wtState()) }
ServerEvents.commandRegistry(event => {
  let { commands: Commands, arguments: Arguments } = event
  event.register(Commands.literal('wt').then(Commands.argument('step', Arguments.STRING.create(event)).executes(cx => {
    let step = String(Arguments.STRING.getResult(cx, 'step')), server = cx.source.server
    try {
      if (step === 'village_setup') { // step 1: treasury 0, account funds 0, hire the villagers to a town
        econCur(ECON, WT_CULT).treasury = 0
        let emp = { type: 'town', id: 'wt_town', culture: WT_CULT }
        wtNear(server, 'minecraft:villager').forEach(v => wageHire(ECON, String(v.uuid), 'laborer', emp, WT_CULT, ECON.week))
        wageAccount(ECON, emp).funds = 0
        wtSay('setup treasury=' + econCur(ECON, WT_CULT).treasury + ' ' + wtState())
      } else if (step === 'week') wtWeek(server)
      else if (step === 'keepers') wtSay('keepers on strike: ' + wtNear(server, 'minecraft:villager').map(v => wageOnStrike(v)).join(','))
      else if (step === 'rebels') wtSay('rebels=' + server.overworld().getEntities().stream().filter(e => e.getTags().contains('wage_rebel')).count() + ' villagers_left=' + wtNear(server, 'minecraft:villager').length)
      else if (step === 'company_setup') { // company step 1: hired crane operator, unpaid
        companyFound(ECON, 'acme', 'Acme Rail', WT_CULT)
        let v = wtNear(server, 'minecraft:villager')[0]
        wtSay('villager=' + (v ? v.type : 'none')); let m; try { m = econMarketOf(v); wtSay('market=' + JSON.stringify(m)) } catch (x) { wtSay('econMarketOf ERR ' + x) }; try { v.persistentData.putString('wage_company', 'acme'); wtSay('emp=' + JSON.stringify(wageEmployerOf(v, m || {}))) } catch (x) { wtSay('employer ERR ' + x) }
        let r = global.WAGE_HIRE(v, 'crane_operator', 'acme')
        wtSay('hired=' + (r ? JSON.stringify(r) : 'null') + ' money=' + ECON.company.acme.money)
      } else if (step === 'company_state') wtSay('striking=' + ECON.company.acme.striking + ' ' + wtState())
      else if (step === 'company_pay') { ECON.company.acme.money = 100000; wtSay('paid company') }
      else if (step === 'types') { let o = []; server.overworld().getEntities().forEach(e => { o.push(String(e.type) + '/' + String(e.getType()) + '/' + e.getType().toString()) }); wtSay('types ' + o.slice(0, 8).join(' ; ')) }
      else if (step === 'probe') { let v = wtNear(server, 'minecraft:villager')[0]; let id = String(v.uuid); let n; try { n = wageEntity(id) } catch (x) { wtSay('wageEntity ERR ' + x) }; wtSay('ECON_SERVER=' + (ECON_SERVER ? 'set' : 'null'));
      try { let U = Java.loadClass('java.util.UUID'); wtSay('A load UUID ok ' + U) } catch (x) { wtSay('A load UUID ERR ' + x) }
      try { let U = Java.loadClass('java.util.UUID'); let e1 = server.overworld().getEntity(U.fromString(id)); wtSay('B getEntity(uuid)=' + (e1 ? e1.type : e1)) } catch (x) { wtSay('B ERR ' + x) }
      try { let e2 = server.getEntityByUUID ? server.getEntityByUUID(id) : 'nofn'; wtSay('C server.getEntityByUUID=' + (e2 && e2.type ? e2.type : e2)) } catch (x) { wtSay('C ERR ' + x) }
      try { let e3 = null; server.overworld().getEntities().forEach(e => { if (String(e.uuid) === id) e3 = e }); wtSay('D scan=' + (e3 ? e3.type : e3)) } catch (x) { wtSay('D ERR ' + x) }
      try { wtSay('E nbt getString=' + v.persistentData.getString('wage_company').orElse('') + ' getBoolean=' + v.persistentData.getBoolean('wage_strike').orElse(false)) } catch (x) { wtSay('E ERR ' + x) }
      wtSay('wageEntity(' + id + ')=' + (n ? n.type : n)); try { wtSay('getString=' + v.persistentData.getString('wage_company') + ' getBoolean=' + v.persistentData.getBoolean('wage_strike') + ' strikeFn=' + wageOnStrike(v)) } catch (x) { wtSay('nbt ERR ' + x) } }
      else if (step === 'age7') { global.WT_AGE = 'VII'; wtSay('age VII') }
    } catch (e) { wtSay('ERR ' + step + ' ' + e) }
    return 1
  })))
})
