import pandas
import copy
#INPUTS REQUIRED FOR CODE
file_name='Input.xls'
Losses=pandas.read_excel(io='Input.xls',sheet_name='Canal_losses')
input_volume=pandas.read_excel(io='Input.xls',sheet_name='Volume_input')

prev_junction,q_losses=list(Losses['Prev_junction']),list(Losses['Losses(m3/sec)'])
input_ids,volume=list(input_volume['Junction_ID']),list(input_volume['Volume(m3)'])
outlets=list(pandas.read_excel(io='Input.xls',sheet_name='outlets')['Outlet_ID'])
outlets_volume=[volume[input_ids.index(_)] if _ in input_ids else 0 for _ in outlets]
juns=[_ for _ in input_ids if _ not in outlets]
juns_volume=[volume[input_ids.index(_)] for _ in juns]
junctions=copy.copy(outlets)
junctions_volume=copy.copy(outlets_volume)

# finding the active canals (some canals are not carrying any water)
n=0
while n<len(prev_junction):
    junction=prev_junction[outlets[n]-1]
    if junction not in outlets:
        post_junction=[_ for _ in range(1,len(prev_junction)+1) if prev_junction[_-1]==junction]
        if sum([1 for _ in post_junction if _ in outlets])==len(post_junction):
            sm=juns_volume[juns.index(junction)] if junction in juns else 0
            for _ in post_junction:
                sm=sm+outlets_volume[outlets.index(_)]
            outlets.append(junction)
            outlets_volume.append(sm)
    n=n+1
# making q_losses zero for unactive canals
for _ in outlets:
    if outlets_volume[outlets.index(_)] ==0:
        q_losses[_-1]=0
        
# Taking inputs
q_main=int(input("Discharge of the Main canal in m3/sec [default:200(m3/sec)] : ") or "200")
ip=(input("Do you know the volume of water available at the Reservoir? (yes/no) [default:no] : ") or "no")
time=sum(volume)/(q_main-sum(q_losses))
if ip[0]=='y' or ip[0]=='Y':
    v_main=int(input("volume of water available at the Reservoir in m3 [default: 0(m3)] : ") or "0")
    t_main=v_main/q_main
    if t_main<time:
        print('Volume of water available in the reservoir is less than the requirement')
        print('Running scenario 2.......................')
        t=t_main
        v_losses=[_*t for _ in q_losses]
        v_provide,v_required=v_main-sum(v_losses),sum(volume)
        reduce_percentage=v_provide*100/v_required
        junctions_volume=[_*(reduce_percentage/100) for _ in junctions_volume]
        juns_volume=[_*(reduce_percentage/100) for _ in juns_volume]
        print(f'with the volume of water available at the reservoir, we can supply only {reduce_percentage}% of the requirement')
    else:
        t=time
        v_losses=[_*t for _ in q_losses]
        print('Volume of water available in the reservoir is more than the requirement')
        print('Running scenario 1.......................')
else:
    print('Assuming that the volume of water available in the reservoir is more than the requirement')
    print('Running scenario 1.......................')
    t=time
    v_losses=[_*t for _ in q_losses]

# finding junction volume
n=0
while n<len(prev_junction):
    junction=prev_junction[junctions[n]-1]
    if junction not in junctions:
        post_junction=[_ for _ in range(1,len(prev_junction)+1) if prev_junction[_-1]==junction]
        if sum([1 for _ in post_junction if _ in junctions])==len(post_junction):
            sm=juns_volume[juns.index(junction)] if junction in juns else 0
            for m in post_junction:
                sm=sm+junctions_volume[junctions.index(m)]+v_losses[m-1]
            junctions.append(junction)
            junctions_volume.append(sm)
    n=n+1
# finding volume and discharge of the canal
v_canal=[junctions_volume[junctions.index(_)]+v_losses[_-1]  for _ in range(1,len(prev_junction)+1)]
q_canal=[_/t for _ in v_canal]

# outputs
canal={'Canal_ID':[_ for _ in range(1,len(prev_junction)+1) ],'Q_losses(m3/sec)':q_losses,'V_losses(m3)':v_losses,'Q_shedule(m3/sec)':q_canal,'Volume(m3)':v_canal}
canal=pandas.DataFrame(canal)
canal.set_index('Canal_ID',inplace=True)
canal=canal.sort_index()
junction={'Junction_ID':junctions,'Volume(m3)':junctions_volume}
junction=pandas.DataFrame(junction)
junction.set_index('Junction_ID',inplace=True)
junction=junction.sort_index()
with pandas.ExcelWriter('Output.xls') as writer:
    canal.to_excel(writer, sheet_name='Canal')
    junction.to_excel(writer, sheet_name='Junction')

print('Output.xls was created....add to Shape file to view the sheduling ')
print('Volume of water required at Resarvior : ',junctions_volume[-1],'(m3)')
print('Losses in the canal : ',sum(v_losses),'(m3)')
print('Canal Run time : ',t/60,'(min)')
