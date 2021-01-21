import shapefile as shp
import os
import pandas
file=shp.Reader("canal.shp")
# functions
def q_losses(ip):
    for _ in range(len(attributes)):
        globals()[attributes[_]]=ip[_]
    Area=(Top_wid+Bottom_wid)*Depth/2
    wetted_perimeter=2*(((((Top_wid-Bottom_wid)/2)**2)+Depth**2)**0.5)+Bottom_wid
    hydraulic_radius=Area/wetted_perimeter
    Q=(1/n)*(hydraulic_radius**(2/3))*((1/Bed_slope)**0.5)*Area     # Discharge capacity from manning's formula
    q_ul= (1.905*wetted_perimeter*(Q**0.0625))*(((100-Lined_perc)/100)*Length)/1000000  # losses in unlined canal from punjab emparical formula
    q_ll= (0.467*wetted_perimeter*(Q**0.056))*((Lined_perc/100)*Length)/1000000 # losses in lined canal from punjab emparical formula
    q_el=1.15741e-07*Top_wid*Length
    q_l=q_ul+q_ll+q_el
    return canal_id,q_l

def find_junction(ip):
    jun_id,cordinates=ip[0],ip[1]
    junction=[]
    if cordinates in start_cordinates:
        indexs=[_ for _  in range(len(start_cordinates)) if start_cordinates[_] == cordinates]
        for index in indexs:
            junction.append([canal_ID[index],end_cordinates[index]])
    if cordinates in end_cordinates:
        indexs=[_ for _  in range(len(end_cordinates)) if end_cordinates[_] == cordinates]
        for index in indexs:
            junction.append([canal_ID[index],start_cordinates[index]])
    if jun_id in [_[0] for _ in junction]:
        del junction[[_[0] for _ in junction].index(jun_id)]
    return junction

decimal_equalizer= lambda ip : (float(format(ip[0],f".{7}f")),float(format(ip[1],f".{7}f")))

# reading inputs
values=[list(f.record) for f in file]
attributes=[a[0] for a in file.fields[1:]]
out=[q_losses(_) for _ in values]
canal_ID=[_[0] for _ in out]
Q_losses=[_[1] for _ in out]
start_cordinates=[decimal_equalizer(s.points[0]) for s in file.shapes()]
end_cordinates=[decimal_equalizer(s.points[-1]) for s in file.shapes()]
# Taking inputs
Main_canal_id=int((input("Enter Main canal ID [default:1] : ") or "1"))
index=canal_ID.index(Main_canal_id)
# finding Main resarvior cordinates
Main_canal_cordinates=start_cordinates[index] if start_cordinates[index] not in end_cordinates else end_cordinates[index]
junction_ID,junction_cordinates,no_canals,prev_junction,canal,n=[0],[Main_canal_cordinates],[],[],[],0
# Main algorithem
while n < len(junction_ID):
    op=find_junction([junction_ID[n],junction_cordinates[n]])
    junction_ID=junction_ID+[_[0] for _ in op]
    junction_cordinates=junction_cordinates+[_[1] for _ in op]
    canal=canal+[_[0] for _ in op]
    prev_junction=prev_junction+[junction_ID[n] for _ in op]
    no_canals.append(len(op))
    n=n+1
# outputs
losses={'Canal_ID':canal_ID,'Prev_junction':[prev_junction[canal.index(_)] for _ in canal_ID],'Post_junction':canal_ID,'Nu_off_taking_canals':[no_canals[junction_ID.index(_)] for _ in canal_ID],'Losses(m3/sec)':Q_losses}
Losses=pandas.DataFrame(losses)
Losses.set_index('Canal_ID',inplace=True)
Losses=Losses.sort_index()
outlets=[_ for _ in junction_ID if no_canals[junction_ID.index(_)]==0]
outlet_cordinates=[junction_cordinates[_] for _ in range(len(junction_ID)) if no_canals[_]==0]
Outlets={'Outlet_ID':outlets,'Volume(m3)':[0 for _ in outlets]}
Outlets=pandas.DataFrame(Outlets)
Outlets.set_index('Outlet_ID',inplace=True)
Outlets=Outlets.sort_index()
input_volume=pandas.DataFrame({'Junction_ID':[0],'Volume(m3)':[0]})
input_volume.set_index('Junction_ID',inplace=True)
#  creating Junction Shapafiles
JS = shp.Writer('Junction')
JS.field('Junction_ID','N')
[JS.point(_[0],_[1]) for _ in junction_cordinates]
[JS.record(_) for _ in junction_ID]
JS.close()
#  creating outlet Shapafiles
#OS = shp.Writer('Outlets')
#OS.field('Outlet_ID','N')
#[OS.point(_[0],_[1]) for _ in outlet_cordinates]
#[OS.record(_) for _ in outlets]
#OS.close()
with pandas.ExcelWriter('Input.xls') as writer:
    Losses.to_excel(writer, sheet_name='Canal_losses')
    input_volume.to_excel(writer, sheet_name='Volume_input')
    Outlets.to_excel(writer, sheet_name='outlets')
print('Enter the required volume of water in "Volume_input" sheet of input.xls')