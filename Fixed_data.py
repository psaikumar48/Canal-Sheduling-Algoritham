import shapefile as shp
import os
import pandas as pd
#INPUT REQUIRED FOR CODE
path='D:\sai kumar\Project\Main'
Cananal_id=1 # canal diverted from resarvior
shppath=path+'\shapefile'
os.chdir(shppath)
sf=shp.Reader("canal.shp")
shapes =sf.shapes()
# converting canal dimensions in to a dataframe 
v1,v2,v3,v4,v5,v6,v7,v8=[],[],[],[],[],[],[],[]
for h in range(len(sf)):
    data=sf.record(h)
    v1.append(data[0]),v2.append(data[1]),v3.append(data[2]),v4.append(data[3])
    v5.append(data[4]),v6.append(data[5]),v7.append(data[6]),v8.append(data[7])
cd=pd.DataFrame({f'{sf.fields[1][0]}':v1,f'{sf.fields[2][0]}':v2,f'{sf.fields[3][0]}':v3,f'{sf.fields[4][0]}':v4,
                f'{sf.fields[5][0]}':v5,f'{sf.fields[6][0]}':v6,f'{sf.fields[7][0]}':v7,f'{sf.fields[8][0]}':v8})
cd['index']=cd.canal_id
cd.set_index('index',inplace=True) 
# gettin cordinates of canal
scord,ecord,cid=[],[],[]
for i in range(len(sf)):
    lcord=shapes[i].points
    scord.append(lcord[0])
    ecord.append(lcord[len(lcord)-1])
    cid.append(sf.record(i)[0])
Canal=pd.DataFrame({'Canal_ID': cid,'Start_cord': scord,'End_cord': ecord})
Canal.set_index('Canal_ID',inplace=True)
Canal.End_cord[29]=(3612437.2112000063, 3170581.363900002)
Canal.Start_cord[1012]=(3662436.132400006, 3184459.4406999946)
Canal.Start_cord[167]=(3628850.0515000075, 3179112.1341999993)
# method related to a junction
def cop(cid,crd1):
    if Canal.Start_cord[cid]==crd1:
        crd2=Canal.End_cord[cid]
    else:
        crd2=Canal.Start_cord[cid]
    idlst=Canal[Canal.Start_cord==crd2].index.tolist()
    [idlst.append(k) for k in Canal[Canal.End_cord==crd2].index.tolist()]
    idlst.remove(cid)
    return crd2,idlst
# method will give disigned discharge and losses
def ca(cid):
    a=((cd.Top_wid[cid]+cd.Bottom_wid[cid])/2)*cd.Depth[cid]
    wp=(2*(((((cd.Top_wid[cid]-cd.Bottom_wid[cid])/2)**2)+cd.Depth[cid]**2)**0.5))+cd.Bottom_wid[cid]
    r=a/wp
    q=(1/cd.n[cid])*((r)**(2/3))*((1/cd.Bed_slope[cid])**0.5)*a
    qul=((1.905*wp*(q**0.0625))*(1-(cd.Lined_perc[cid]/100))*cd.Length[cid])/1000000
    qll=((wp*(q**0.056)*0.467)*(cd.Lined_perc[cid]/100)*cd.Length[cid])/1000000
    qel=1.157407407407407e-07*(cd.Top_wid[cid])*(cd.Length[cid])
    ql=qul+qll+qel
    return q,ql 
# findin resarvior cordinates   
x,y=cop(Cananal_id,Canal.End_cord[Cananal_id])
if len(y)==0:
    cv=Canal.Start_cord[Cananal_id]
else:
    cv=Canal.End_cord[Cananal_id]
#gettin cordinates of junction
Junction=pd.DataFrame({'Junction_ID': [Cananal_id],'sai':[cv],'Cordinates': [(0,0)],'kumar':[0],'Nop':0})
for j in range(len(sf)):
        cordn,jid=cop(Junction.Junction_ID[j],Junction.sai[j])
        Junction.Cordinates[j]=cordn
        Junction.Nop[j]=len(jid)
        for k in jid:
            Junction=Junction.append({'Junction_ID':k,'sai':cordn,'Cordinates':(0,0),'kumar':Junction.Junction_ID[j],'Nop':0},ignore_index=True)
# gettin start and end node of each canal section
CEN=pd.DataFrame({'Canal_ID':Junction.Junction_ID,'Prev_Node':Junction.kumar,'Post_Node':Junction.Junction_ID})
CEN.set_index('Canal_ID',inplace=True)
CEN=CEN.sort_index()
Junction=Junction.drop(columns=['sai','kumar'])
Junction=Junction.append({'Junction_ID':0,'Cordinates':cv,'Nop':1},ignore_index=True)
Junction['Index']=Junction.Junction_ID
Junction.set_index('Index',inplace=True)
Junction=Junction.sort_index()
# creating junction shapefile 
j = shp.Writer('junction')
j.field('Junction_ID', 'N')
j.field('Nop','N')
for k in range(len(Junction)):
    j.point(Junction.Cordinates[k][0],Junction.Cordinates[k][1]) 
    j.record(Junction.Junction_ID[k],Junction.Nop[k])
j.close()
# creating outlet shapefile 
o = shp.Writer('Outlets')
o.field('Outlet_ID', 'N')
for l in Junction[Junction.Nop==0].index.tolist():
    o.point(Junction.Cordinates[l][0],Junction.Cordinates[l][1]) 
    o.record(Junction.Junction_ID[l])
o.close()
# finding input1 and input3
ip3=pd.DataFrame({'Junction_ID':[0],'Req_Volume(m3)':[0]})
ip3.set_index('Junction_ID',inplace=True)
ip2=pd.DataFrame({'Outlet_ID':Junction[Junction.Nop==0].index.tolist()})
caid,qd,ql=[],[],[]
for m in cd.canal_id:
    caid.append(m)
    x,y=ca(m)
    qd.append(x)
    ql.append(y)
ip1=pd.DataFrame({'Canal_ID':caid,'Design_discharge(m3/sec)':qd,'Q_losses(m3/sec)':ql,
                  'Desided_discharge(m3/sec)':[0]*len(caid),'Desided_run_time(sec)':[0]*len(caid)}) 
ip1.set_index('Canal_ID',inplace=True)
os.chdir(path)
with pd.ExcelWriter('Input.xls') as writer:
    ip1.to_excel(writer, sheet_name='Canal_IP')
    ip3.to_excel(writer, sheet_name='Volume_IP')
    ip2.to_excel(writer, sheet_name='Outlets')
    CEN.to_excel(writer, sheet_name='Canal_end_nodes')
