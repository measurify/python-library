import os
path = os.path.dirname(__file__)

from Source.Measurify_library.measurify import Create
#from timeit import default_timer as timer

def Bologna_analisi():

    api=Create()

    response=api.deleteDataset(filename="centraline-qualita-aria")
    print(response)
    #start = timer()  
    response=api.postDataset(file=path+"\\centraline-qualita-aria.txt",description=path+"\\AllegatoBologna.txt",force=True,verbose=True)

    #end = timer()  
    print(response)
    #print("time="+str((end-start))+" seconds")
    filename="centraline-qualita-aria"

    dict=api.createFilter(feature="PM10")

    dataset=api.getDataset(filter=dict,filename=filename,format=api.Format.CSV)
    print(dataset)

