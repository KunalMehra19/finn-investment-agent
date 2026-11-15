"""Use the existing Git credential helper; never print or persist its credential."""
import argparse,json,os,subprocess
import httpx
parser=argparse.ArgumentParser();parser.add_argument('--create',action='store_true');args=parser.parse_args()
env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GCM_INTERACTIVE':'Never'}
result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\nusername=KunalMehra19\n\n',text=True,capture_output=True,env=env)
if result.returncode:raise SystemExit('GitHub credential unavailable; complete GitHub connection.')
credential=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
token=credential.get('password');headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
with httpx.Client(base_url='https://api.github.com',headers=headers,timeout=20) as client:
    r=client.get('/user');r.raise_for_status();login=r.json()['login'];print(json.dumps({'authenticated_as':login}))
    if args.create:
        name='finn-investment-agent';path=f'/repos/{login}/{name}';existing=client.get(path)
        if existing.status_code==200:
            # Never overwrite an unrelated repository.
            marker=client.get(path+'/contents/.openai/hosting.json')
            import base64
            if marker.status_code!=200 or json.loads(base64.b64decode(marker.json()['content'])).get('project_id')!='appgprj_6af9d0431d088191bdc589b2e47bb089':
                name='finn-enam-2026';path=f'/repos/{login}/{name}';existing=client.get(path)
                if existing.status_code==200:raise SystemExit('Both candidate repository names are already in use; preserved existing repositories.')
        site='https://finn-research-desk.delicateloon4.chatgpt.site'
        values={'description':'FINN: evidence-backed Indian equity research, NSE filing reels and guidance accountability. Public demo: '+site,'homepage':site,'has_wiki':False}
        if existing.status_code==404:
            response=client.post('/user/repos',json={**values,'name':name,'private':False,'auto_init':False})
        else:response=client.patch(path,json=values)
        response.raise_for_status();repo=response.json()
        print(json.dumps({'repository':repo['html_url'],'clone_url':repo['clone_url'],'homepage':repo['homepage'],'private':repo['private']}))
