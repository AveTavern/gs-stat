import gspread 
gs = gspread.service_account(filename='/var/www/system-admin/credits.json')  
sh = gs.open_by_key('GS_key') 

import xml.etree.ElementTree as ET 
import requests 

from datetime import datetime 
current_date = datetime.now()

worksheet = sh.worksheet("Stat")
tunnel_names = worksheet.col_values(1) 

res = requests.request('get', 'https://quiet-vpn.ru:1500/ispmgr?authinfo=LOGIN:PASS&func=wireguard.user&out=xml')
root = ET.fromstringlist(res)
for elem in root.findall('elem'):
    sentsize = elem.find('sentsize').text
    sentsize = sentsize.strip(' GB') 
    sentsize = sentsize.replace(".", ",") 
    name = elem.find('name').text 
    i = 0 
    for word in tunnel_names: 
        a = i+1
        b = current_date.day+1
        if name == tunnel_names[i]:
            worksheet = sh.worksheet("Stat")
            worksheet = worksheet.update_cell(a, b, sentsize); 
        i += 1
        
worksheet = sh.sheet1  
tunnel_names = worksheet.col_values(4) 
tunnel_names.remove('Tunnel names')
license_expirational_dates = worksheet.col_values(3) 
license_expirational_dates.remove('End date')

i = 0 
import subprocess 
for word in tunnel_names:
    date_for_comparison = license_expirational_dates[i]
    date_for_comparison = datetime.strptime(date_for_comparison, "%d.%m.%Y")
    if date_for_comparison.year > current_date.year:
        print('year success', tunnel_names[i], date_for_comparison.year, current_date.year)
    else:
        if date_for_comparison.month > current_date.month: 
            print('month success', tunnel_names[i], date_for_comparison.month, current_date.month)
        else:
            if date_for_comparison.month == current_date.month:
                print('month equal', tunnel_names[i], date_for_comparison.month, current_date.month)
                if date_for_comparison.day >= current_date.day:
                    print('day success', tunnel_names[i], date_for_comparison.day, current_date.day)
                else:
                    print('day fail', tunnel_names[i], date_for_comparison.day, current_date.day)
                    elid = 'elid='+tunnel_names[i]
                    url = '/usr/local/mgr5/sbin/mgrctl'+' -m'+' ispmgr'+' wireguard.user.suspend '+elid+' sok=ok'
                    subprocess.run([url], shell=True)
            else:
                print('month fail', tunnel_names[i], date_for_comparison.month, current_date.month)
                elid = 'elid='+tunnel_names[i]
                url = '/usr/local/mgr5/sbin/mgrctl'+' -m'+' ispmgr'+' wireguard.user.suspend '+elid+' sok=ok'
                subprocess.run([url], shell=True)
    i +=1
print('Cycle end')
