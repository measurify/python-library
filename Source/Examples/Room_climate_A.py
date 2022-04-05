import measurify
#from timeit import default_timer as timer


api=measurify.Create()

response=api.deleteDataset(filename="room_climate-location_A-measurement01")
#print(response)
#start = timer()  
response=api.postDataset(file=".\\room_climate-location_A-measurement01.txt",description=".\\AllegatoRoomClimate.txt",force=True,verbose=True)

#end = timer()  
print(response)
#print("time="+str((end-start))+" seconds")
filename="room_climate-location_A-measurement01"

dict=api.createFilter(feature="Room_Status")

dataset=api.getDataset(filter=dict,filename=filename,format=api.Format.CSVPLUS,limit=10)
#print(dataset)