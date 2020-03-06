import pandas as pd
import os
#INPUTS REQUIRED FOR CODE
path='D:\sai kumar\Project\Main'
is_input_is_time=True
os.chdir(path)
A=pd.read_excel(io='Input.xls',sheet_name='Canal_IP',index_col ="Canal_ID")
B=pd.read_excel(io='Input.xls',sheet_name='Canal_end_nodes',index_col ="Canal_ID")
d=pd.read_excel(io='Input.xls',sheet_name='Volume_IP')

#function used to get volume of junction based on diverted canals from that junction
def LO(lt):
    sm=0
    for i in lt:
        x=C[C.Outlet_ID==i].index.tolist()[0]
        if C['Volume(m3)'][x]==0:
            t=0
            v=0
        elif is_input_is_time == True:
            t=A['Desided_run_time(sec)'][i]
            v=(C['Volume(m3)'][x])+(t*(A['Q_losses(m3/sec)'][i]))
        else:
            t=(C['Volume(m3)'][x])/((A['Desided_discharge(m3/sec)'][i])-(A['Q_losses(m3/sec)'][i]))
            v=(t*(A['Desided_discharge(m3/sec)'][i]))
        sm=sm+v
    return sm        

# function used to find the Q,V,T at start of a canal when CId and V given at canal end 
def jtoc(j,v):
    if v==0:
        t=0
        vo=0
        q=0
    elif is_input_is_time == True:
        t=A['Desided_run_time(sec)'][j]
        vo=v+(t*(A['Q_losses(m3/sec)'][j]))
        q=vo/t
    else:
        q=A['Desided_discharge(m3/sec)'][j]
        t=v/((A['Desided_discharge(m3/sec)'][j])-(A['Q_losses(m3/sec)'][j]))
        vo=q*t
    return [vo,q,t] 
# function is used to find wether the given list is avalible in C or not
def chek(lst):
    sm=0
    for i in lst:
        sm=sm+sum(C.Outlet_ID==i) 
    if sm==len(lst):
        return True
    else:
        return False          

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

# Main Algorithem    j=4
for j in range(len(A)-1):
    Pr_N=B.Prev_Node[C.Outlet_ID[j]]
    Po_N=B[B.Prev_Node==Pr_N].index.tolist()
    if sum(C.Outlet_ID==Pr_N)==0 and chek(Po_N):
        if sum(d.Junction_ID==Pr_N)==0:
            vol=LO(Po_N)
        else:
            vol=LO(Po_N)+d['Req_Volume(m3)'][d[d.Junction_ID==Pr_N].index.tolist()[0]]
        C=C.append({'Outlet_ID' : Pr_N,'Volume(m3)' : vol} , ignore_index=True)
C=C.astype({'Outlet_ID':int})
# Converting C to canal data
caid,v,q,t=[],[],[],[]
for k in range(len(C)):
    cid=C.Outlet_ID[k]
    ve=C['Volume(m3)'][k]
    caid.append(cid)
    v.append(jtoc(cid,ve)[0])
    q.append(jtoc(cid,ve)[1])
    t.append(jtoc(cid,ve)[2])
if is_input_is_time == True:
    se={'Canal_ID': caid,'Volume(m3)': v,'given t(sec)': t,'Q(m3/sec)': q}
    ofn='Output_for_given_T'
else:
    se={'Canal_ID': caid,'Volume(m3)': v,'given Q(m3/sec)': q,'Run time(sec)': t}
    ofn='Output_for_given_Q'
Canal=pd.DataFrame(se)
Canal.set_index('Canal_ID',inplace=True)
Canal=Canal.sort_index()
#Converting C to Junction data
Junction=C
Junction=Junction.append({'Outlet_ID' : B.Prev_Node[C.Outlet_ID[len(A)-1]] , 'Volume(m3)' : LO([C.Outlet_ID[len(A)-1]])},ignore_index=True)
Junction=Junction.rename(columns={'Outlet_ID': 'Junction_ID'})
Junction.set_index('Junction_ID',inplace=True)
Junction=Junction.sort_index()

with pd.ExcelWriter(f"{ofn}.xls") as writer:
    Canal.to_excel(writer, sheet_name='Canal_OP')
    Junction.to_excel(writer, sheet_name='Junction_OP')