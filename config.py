from detect_table import detect_table
import connect
dt = detect_table('test2.jpg')
text2D, t_name = dt.get_val()
for i in range(len(text2D)):  
    connect.insert(text2D[i])
connect.get()
print(text2D)
print('Table name : ', t_name)