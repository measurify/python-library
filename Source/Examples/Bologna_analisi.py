import measurify
#from timeit import default_timer as timer


api=measurify.Create()

response=api.deleteDataset(filename="centraline-qualita-aria")
#print(response)
#start = timer()  
response=api.postDataset(file=".\\centraline-qualita-aria.txt",description=".\\AllegatoBologna.txt",force=True,verbose=True)

#end = timer()  
print(response)
#print("time="+str((end-start))+" seconds")
filename="centraline-qualita-aria"

dict=api.createFilter(feature="PM10")

dataset=api.getDataset(filter=dict,filename=filename,format=api.Format.DATAFRAME)#PDDATAFRAME
#print(dataset)