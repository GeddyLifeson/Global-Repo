// Mirrors the engine state KubeJS needs (current Age, story flags) and keeps it across restarts.
const AGES = { age: 'TELLING', flags: {} }
const AGES_MIRROR = 'kubejs/data/ages_mirror.json'

try {
  let saved = JsonIO.read(AGES_MIRROR)
  if (saved) {
    AGES.age = String(saved.age || AGES.age)
    AGES.flags = saved.flags || {}
  }
} catch (e) {
  console.warn('[ages] mirror unreadable: ' + e)
}

function agesSaveMirror() {
  try { JsonIO.write(AGES_MIRROR, { age: AGES.age, flags: AGES.flags }) }
  catch (e) { console.warn('[ages] mirror not saved: ' + e) }
}

const agesIsAge = id => AGES.age === id
const agesFlag = name => AGES.flags[name] === true

NativeEvents.onEvent(Java.loadClass('net.diaithir.ages.mc.StoryEvent'), e => {
  let kind = String(e.kind), key = String(e.key), value = String(e.value)
  if (kind === 'flag') { AGES.flags[key] = value === 'true'; agesSaveMirror() }
  else if (kind === 'age') {
    AGES.age = value
    agesSaveMirror()
    Utils.server.scheduleInTicks(1, () => Utils.server.runCommandSilent('reload')) // tech_gate.js rebuilds recipes for the new Age
  }
  console.info('[agesevt] ' + kind + ' ' + key + '=' + value)
})
