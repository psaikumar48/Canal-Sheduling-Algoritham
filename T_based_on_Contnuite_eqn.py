import pandas as pd
import os
#INPUTS REQUIRED FOR CODE
ip=[1,250]    #ip=[canal id,desided Discharge(m3/sec)]
path='D:\sai kumar\Project\Main'
os.chdir(path)
A=pd.read_excel(io='Input.xls',sheet_name='Canal_IP',index_col ="Canal_ID")
B=pd.read_excel(io='Input.xls',sheet_name='Canal_end_nodes',index_col ="Canal_ID")
d=pd.read_excel(io='Input.xls',sheet_name='Volume_IP')

#function used to get volume of junction based on diverted canals from that junction LO([10,6,8])
def LO(lt):
    sm=0
    for i in lt:
        x=C[C.Outlet_ID==i].index.tolist()[0]
        sm=sm+C['Volume(m3)'][x]
    return sm                  

# finding outlets
ol,vl=[],[]
for z in range(1,len(A)+1):
    if sum(B.Prev_Node==z)==0:
        ol.append(z)
        if sum(d.Junction_ID==z)==0:
            vl.append(0)
        else:
            vl.append(d['Req_Volume(m3)'][d[d.Junction_ID==z].index.tolist()[0]])
odf={'Outlet_ID':ol,'Volume(m3)':vl}
C=pd.DataFrame(odf)

# Volume finding at each junction based on  given volume input(Ql=0)   
for j in range(len(A)-1):
    if sum(C.Outlet_ID==(B.Prev_Node[C.Outlet_ID[j]]))==0:
        lst=B[B.Prev_Node==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()
        lst.remove(C.Outlet_ID[j])
        if len(C[C.Outlet_ID==lst[0]].index.tolist()) > 0 and len(lst)==1:
            lst=B[B.Prev_Node==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()
            if sum(d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]])==0:
                vol=LO(lst)
            else:
                vol=LO(lst)+d['Req_Volume(m3)'][d[d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()[0]]
            C=C.append({'Outlet_ID' : B.Prev_Node[C.Outlet_ID[j]] ,'Volume(m3)' : vol} , ignore_index=True)
        elif len(lst)==2 and len(C[C.Outlet_ID==lst[0]].index.tolist()) > 0 and len(C[C.Outlet_ID==lst[1]].index.tolist()) > 0:
            lst=B[B.Prev_Node==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()
            if sum(d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]])==0:
                vol=LO(lst)
            else:
                vol=LO(lst)+d['Req_Volume(m3)'][d[d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()[0]]
            C=C.append({'Outlet_ID' : B.Prev_Node[C.Outlet_ID[j]] , 'Volume(m3)' : vol} , ignore_index=True)
C=C.astype({'Outlet_ID':int})
C.set_index('Outlet_ID',inplace=True)
CEV=C
# making Qlosses zero for unused canals 
for k in range(1,len(A)):
    if C['Volume(m3)'][k]==0:
        A['Q_losses(m3/sec)'][k]=0
# finding qumalative Qlosses at each end of a canal
jid,ql=[],[]
for l in range(1,len(A)):
    jid.append(l)
    ql.append(A['Q_losses(m3/sec)'][l])
qldf={'Junction_ID':jid,'Req_Volume(m3)':ql}   
d=pd.DataFrame(qldf)   
# repeating operation
# finding outlets
ol,vl=[],[]
for z in range(1,len(A)+1):
    if sum(B.Prev_Node==z)==0:
        ol.append(z)
        if sum(d.Junction_ID==z)==0:
            vl.append(0)
        else:
            vl.append(d['Req_Volume(m3)'][d[d.Junction_ID==z].index.tolist()[0]])
odf={'Outlet_ID':ol,'Volume(m3)':vl}
C=pd.DataFrame(odf)

# Volume finding at each junction based on  given volume input(Ql=0)   
for j in range(len(A)-1):
    if sum(C.Outlet_ID==(B.Prev_Node[C.Outlet_ID[j]]))==0:
        lst=B[B.Prev_Node==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()
        lst.remove(C.Outlet_ID[j])
        if len(C[C.Outlet_ID==lst[0]].index.tolist()) > 0 and len(lst)==1:
            lst=B[B.Prev_Node==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()
            if sum(d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]])==0:
                vol=LO(lst)
            else:
                vol=LO(lst)+d['Req_Volume(m3)'][d[d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()[0]]
            C=C.append({'Outlet_ID' : B.Prev_Node[C.Outlet_ID[j]] ,'Volume(m3)' : vol} , ignore_index=True)
        elif len(lst)==2 and len(C[C.Outlet_ID==lst[0]].index.tolist()) > 0 and len(C[C.Outlet_ID==lst[1]].index.tolist()) > 0:
            lst=B[B.Prev_Node==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()
            if sum(d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]])==0:
                vol=LO(lst)
            else:
                vol=LO(lst)+d['Req_Volume(m3)'][d[d.Junction_ID==B.Prev_Node[C.Outlet_ID[j]]].index.tolist()[0]]
            C=C.append({'Outlet_ID' : B.Prev_Node[C.Outlet_ID[j]] , 'Volume(m3)' : vol} , ignore_index=True)
C=C.astype({'Outlet_ID':int})
C.set_index('Outlet_ID',inplace=True)
print(CEV['Volume(m3)'][ip[0]]/(ip[1]-C['Volume(m3)'][ip[0]]))
