# S6989 Part J12: checks the assay rules. Powers only on beings; gear scale only on weapon/armor/vehicle; reports assay beings with no verified source link. No AI.
# python3 -I assay_rules_check.py   (reads /mnt/project-files/plans)
import csv,collections
P='/mnt/project-files/plans/'; rd=lambda f:csv.DictReader(open(P+f),delimiter='\t')
master={r['id']:r for r in rd('PANSCRIPTUM_MASTER.tsv')}
bad_pow=sum(1 for r in rd('powers/BEING_POWERS.tsv') if r['key'] not in master)
bad_gear=collections.Counter(r['kind'] for r in rd('powers/GEAR_SCALE.tsv') if r['kind'] not in ('weapon','armor','vehicle'))
unlinked=collections.Counter(r['relink_status'] for r in master.values() if not r['source_wiki'] and r['relink_status']!='original')
print('powers on non-beings:',bad_pow); print('gear rows not weapon/armor/vehicle:',dict(bad_gear))
print('assay beings with no verified source link:',sum(unlinked.values()),dict(unlinked))
print('originated beings (no wiki page by design):',sum(1 for r in master.values() if r['relink_status']=='original'))
