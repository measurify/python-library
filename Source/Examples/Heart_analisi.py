import measurify
#from timeit import default_timer as timer


api=measurify.Create()

response=api.deleteDataset(filename="heart")
#print(response)
#start = timer()  
response=api.postDataset(file=".\\heart.txt",description=".\\AllegatoHeart.txt",force=True)

#end = timer()  
print(response)
#print("time="+str((end-start))+" seconds")
filename="heart"

filter=api.createFilter(feature="heartValues")

dataset=api.getDataset(filter=filter,filename=filename,format=api.Format.CSV)
#print(dataset)