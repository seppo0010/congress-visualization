import os
import json
import re
import sys

prefix = sys.argv[1] if len(sys.argv) > 1 else ''

congressmember = {}
for i in range(101, 114):
    congressmember[i] = {}
    for root, dirs, files in os.walk(os.path.join(str(i), 'votes')):
        for f in files:
            if f == 'data.json':
                if not os.path.basename(root).startswith(prefix):
                    continue
                # sys.stderr.write('{}/{}\n'.format(root, f))
                # print (os.path.join(root, f))
                with open(os.path.join(root, f)) as fp:
                    vote_data = json.loads(fp.read())
                if 'bill' not in vote_data:
                    continue
                if 'bill' in vote_data:
                    # 101/amendments/samdt/samdt225/data.json
                    t = vote_data['bill']['type']
                    number = str(vote_data['bill']['number'])
                    with open(os.path.join(str(i), 'bills', t, t + number,
                                'data.json')) as fp:
                        bill_data = json.loads(fp.read())

                if 'Yea' not in vote_data['votes'] and 'Aye' in vote_data['votes']:
                    vote_data['votes']['Yea'] = vote_data['votes'].pop('Aye')
                if 'Nay' not in vote_data['votes'] and 'No' in vote_data['votes']:
                    vote_data['votes']['Nay'] = vote_data['votes'].pop('No')
                yea_d = len(tuple(1 for v in vote_data['votes']['Yea']
                            if isinstance(v, dict) and v['party'] == 'D'))
                yea_r = len(tuple(1 for v in vote_data['votes']['Yea']
                            if isinstance(v, dict) and v['party'] == 'R'))
                nay_d = len(tuple(1 for v in vote_data['votes']['Nay']
                            if isinstance(v, dict) and v['party'] == 'D'))
                nay_r = len(tuple(1 for v in vote_data['votes']['Nay']
                            if isinstance(v, dict) and v['party'] == 'R'))

                d, r = None, None
                if yea_d > nay_d:
                    d = 'Yea'
                elif yea_d < nay_d:
                    d = 'Nay'

                if yea_r > nay_r:
                    r = 'Yea'
                elif yea_r < nay_r:
                    r = 'Nay'

                for vote, voters in vote_data['votes'].items():
                    if vote not in ('Yea', 'Nay'):
                        continue
                    for voter in voters:
                        if isinstance(voter, basestring):
                            continue
                        if voter['party'] not in ('R', 'D'):
                            continue

                        if voter['display_name'] not in congressmember[i]:
                            congressmember[i][voter['display_name']] = {
                                'total': 0,
                                'majority': 0,
                                'name': voter['display_name'],
                                'party': voter['party'],
                            }

                        congressmember[i][voter['display_name']]['total'] += 1
                        if ((voter['party'] == 'R' and vote == r) or
                                (voter['party'] == 'D' and vote == d)):
                            congressmember[i][voter['display_name']]['majority'] += 1
    for member in congressmember[i].values():
        member['ratio'] = float(member.pop('majority', 0)) / member.pop('total', 1)

    congressmember[i] = sorted(congressmember[i].values(), lambda m1, m2:
            cmp(m1['ratio'] * (1 if m1['party'] == 'R' else -1),
                m2['ratio'] * (1 if m2['party'] == 'R' else -1)))

    j = - len(tuple(m for m in congressmember[i] if m['party'] == 'D'))

    for member in congressmember[i]:
        if member.pop('party') == 'R':
            member['color'] = 'rgba(238, 27, 36, .5)'
        else:
            member['color'] = 'rgba(0, 128, 195, .6)'
        member['data'] = [[j, member.pop('ratio') * 100]]
        j += 1
        if j == 0:
            j += 1

print json.dumps(congressmember, indent=2)
