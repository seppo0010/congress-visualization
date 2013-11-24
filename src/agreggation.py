import os
import json
import re
import sys

prefix = sys.argv[1] if len(sys.argv) > 1 else ''

class Congress(object):
    def __init__(self, congress):
        self.congress = congress
        self.cache_sponsor = {}
        self.cache_voters = {}

    def get_sponsor_data(self, sponsor):
        if sponsor is None:
            return None
        cache_key = sponsor['title'], sponsor['name'], sponsor['state']
        if cache_key in self.cache_sponsor:
            return self.cache_sponsor[cache_key]
        congress_str = str(self.congress)
        for y in (1787, 1788):
            year_str = str(self.congress * 2 + y)
            directory = 'h' if sponsor['title'] == 'Rep' else 's'
            p = os.path.join(congress_str, 'votes', year_str)
            for root, dirs, files in os.walk(p):
                for d in dirs:
                    path = os.path.join(p, d, 'data.json')
                    if path in self.cache_voters:
                        data = self.cache_voters[path]
                    else:
                        with open(path) as fp:
                            data = json.loads(fp.read())
                        self.cache_voters[path] = data
                    for voters in data['votes'].values():
                        for voter in voters:
                            if not isinstance(voter, dict):
                                continue
                            display_name = re.sub(r'\(.*\)', '',
                                    voter['display_name']).strip()
                            if (sponsor['name'].startswith(display_name) and
                               sponsor['state'] == voter['state']):
                                self.cache_sponsor[cache_key] = voter
                                return voter
        # sys.stderr.write('Unable to find sponsor {}\n'.format(sponsor))
        self.cache_sponsor[cache_key] = None
        return None

votes = {}
for i in range(101, 114):
    congress = Congress(i)
    votes[i] = []
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
                # if 'amendment' in vote_data:
                #     # 101/amendments/samdt/samdt225/data.json
                #     amdt = vote_data['amendment']['type'] + 'amdt'
                #     number = str(vote_data['amendment']['number'])
                #     with open(os.path.join(str(i), 'amendments', amdt,
                #                 amdt + number, 'data.json')) as fp:
                #         amendment_data = json.loads(fp.read())
                if 'bill' in vote_data:
                    # 101/amendments/samdt/samdt225/data.json
                    t = vote_data['bill']['type']
                    number = str(vote_data['bill']['number'])
                    with open(os.path.join(str(i), 'bills', t, t + number,
                                'data.json')) as fp:
                        bill_data = json.loads(fp.read())
                    # print json.dumps(bill_data, indent=2)
                # print json.dumps(vote_data, indent=2)
                sponsors = [congress.get_sponsor_data(bill_data['sponsor'])]
                for cosponsor in bill_data['cosponsors']:
                    sponsors.append(congress.get_sponsor_data(cosponsor))
                if 'Yea' not in vote_data['votes'] and 'Aye' in vote_data['votes']:
                    vote_data['votes']['Yea'] = vote_data['votes']['Aye']
                if 'Nay' not in vote_data['votes'] and 'No' in vote_data['votes']:
                    vote_data['votes']['Nay'] = vote_data['votes']['No']
                yea_d = len(tuple(1 for v in vote_data['votes']['Yea']
                            if isinstance(v, dict) and v['party'] == 'D'))
                yea_r = len(tuple(1 for v in vote_data['votes']['Yea']
                            if isinstance(v, dict) and v['party'] == 'R'))
                nay_d = len(tuple(1 for v in vote_data['votes']['Nay']
                            if isinstance(v, dict) and v['party'] == 'D'))
                nay_r = len(tuple(1 for v in vote_data['votes']['Nay']
                            if isinstance(v, dict) and v['party'] == 'R'))

                subject = bill_data['subjects_top_term']
                d, r = None, None
                if yea_d > nay_d:
                    d = 'yea'
                elif yea_d < nay_d:
                    d = 'nay'

                if yea_r > nay_r:
                    r = 'yea'
                elif yea_r < nay_r:
                    r = 'nay'
                votes[i].append((subject, d, r, sponsors))

print json.dumps(votes, indent=2)
sys.exit(0)
