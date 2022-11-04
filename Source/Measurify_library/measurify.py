import string
import requests
import json
from . import Measurify_Dictionary as md 
import urllib3
import pandas as pd
import numpy as np
from timeit import default_timer as timer
from enum import Enum
from typing import Literal
import time
import os
path = os.path.dirname(__file__)
path = str(path)

import sys
sys.path.append(path)


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)#disable warning certificate


class Create:
    def __init__(self,config_Directory:str=path + "\measurifyConfig.json",username:str="",password:str="",options:str=None,verbose:bool=False):
        self.auth_token=0
        self.tknExpTime=0
        self.data=json.load(open(config_Directory))        
        if options is not None:
            options=json.loads(options)
            for key in options:
                if key in self.data:                    
                    self.data[key]=options[key]  
        self.verbose=verbose
        self.filter=None        
        self.login(username=username,password=password)
    
    
    class Format(Enum):
        JSON = 'Json'
        DATAFRAME ='Dataframe'
        CSV = 'CSV'  
        CSVPLUS = 'CSV+' 


    def login(self, username:str="",password:str="",verbose:bool=None):#username=data["username"],password=self.data["password"]):
            if verbose is None:
                verbose=self.verbose
            if username=="":
                verboseprint(md.dictionary["fromjson"],verbose)
                username=self.data["username"]
            if password=="":
                password=self.data["password"]
            
            payload={"username" : username,"password" : password}
            response = requests.post(self.data["url"]+self.data["login_route"], data=payload,verify=False)#verify = false perchè non c'è il certificato
            verboseprint("Status Code: "+ str(response.status_code),verbose)
            if response.ok:
                verboseprint(md.dictionary["log"],verbose)
                self.auth_token=response.json()['token']
                self.setExpToken(response.json()['token_expiration_time'])                
                verboseprint(self.auth_token,verbose)
            else:
                verboseprint(md.dictionary["error"],verbose) 
                verboseprint(response.content,verbose)
            verboseprint("-------",verbose)


    def setExpToken(self,tokenExp:string):
        currentTime=time.time()
        expTimeSeconds=0
        if (tokenExp.endswith('h')):            
            slice_object = slice(0, -1) 
            expTimeSeconds=int(tokenExp[slice_object])*60*60
        elif (tokenExp.endswith('m')):
            slice_object = slice(0, -1) 
            expTimeSeconds=int(tokenExp[slice_object])*60
        elif (tokenExp.endswith('s')):
            slice_object = slice(0, -1) 
            expTimeSeconds=int(tokenExp[slice_object])
        else:
            slice_object = slice(0, -1) 
            expTimeSeconds=int(tokenExp[slice_object])        
        self.tknExpTime=currentTime+expTimeSeconds


    def updateTkn(self, verbose:bool=None):#username=data["username"],password=self.data["password"]):
            if verbose is None:
                verbose=self.verbose            
            headers={'Authorization':self.auth_token}            
            response = requests.put(self.data["url"]+self.data["login_route"], headers=headers,verify=False)#verify = false perchè non c'è il certificato
            verboseprint("Status Code: "+ str(response.status_code),verbose)
            if response.ok:
                verboseprint(md.dictionary["log"],verbose)
                #print(response.json())
                self.auth_token=response.json()['token']
                self.setExpToken(response.json()['token_expiration_time'])                
                verboseprint(self.auth_token,verbose)
                return True
            else:
                verboseprint(md.dictionary["tknError"],verbose) 
                verboseprint(response.content,verbose)
                return False
            
    
    def setVerbose(self,verbose:bool):
        self.verbose=verbose

    
    def setFilter(self,filter:dict):
        self.filter=filter

   
    def createFilter(self,thing:str=None,feature:str=None,device:str=None): 
        if(thing==None and feature==None and device==None):
            print(md.dictionary["noFilterParameters"])
            return None
        else:
            dict={}
            if (thing!=None):
                dict["thing"]=thing
            if (feature!=None):
                dict["feature"]=feature
            if (device!=None):
                dict["device"]=device
        return dict  

    
    def getDataset(self,filename:string=None,filter:dict=None,verbose:bool=None,format:Format=Format.JSON,downloadPath:string=None,limit:int=None,page:int=None):#name is csv name when uploaded on server
        if verbose is None:
            verbose=self.verbose
        if filter is None:
            filter=self.filter
        if filename is not None:
            filename=self.clearFilename(filename) 
        if(format==self.Format.JSON):
            if filter is None:
                filter={}            
            if(filename is not None):
                filter['tags']=filename
            routeFilter="?filter="+json.dumps(filter)#dumps permits dict to str
            if (limit is not None):
                routeFilter+="&limit="+str(limit)
            if (page is not None):
                routeFilter+="&page="+str(page)
            route=self.data["measurements_route"]+routeFilter
            verboseprint(route,verbose)
        else:#not json
            routeFilter=""
            if filter is not None:#self.Filter contains something
                routeFilter="filter="+json.dumps(filter)#dumps permits dict to str
            if (limit is not None):
                routeFilter+="&limit="+str(limit)
            if (page is not None):
                routeFilter+="&page="+str(page)
            if(filename is not None):
                route=self.data["dataset_route"]+"/"+filename+"?"+routeFilter
                verboseprint(route,verbose)
            else:
                route=self.data["dataset_route"]+"?"+routeFilter
                verboseprint(route,verbose)
           
        formatRequest=None
        if(format==self.Format.JSON):
            formatRequest=None            
        if(format==self.Format.CSV):
            formatRequest="text/csv"
        if(format==self.Format.CSVPLUS):
            formatRequest="text/csv+"
        if(format==self.Format.DATAFRAME):
            formatRequest="text/dataframe"
        dataJson=self.getGeneric(route,verbose,formatRequest=formatRequest)

        if downloadPath is not None:            
            with open(downloadPath, 'w') as f:
                f.write(dataJson)
        return dataJson


    def getDatasetInfo(self,filename:string,verbose:bool=None):
        if verbose is None:
            verbose=self.verbose 
        filename=self.clearFilename(filename)     
        dataJson=self.getGeneric(self.data["dataset_route"]+"/"+filename+self.data["dataset_info"],formatRequest="info",verbose=verbose)
        return dataJson


    def getGeneric(self,route:str,verbose:bool=None,formatRequest:dict=None):
        if verbose is None:
            verbose=self.verbose
        if(self.tknExpTime-time.time()<=60):            
            result=self.updateTkn()
            if(result==False):
                print(md.dictionary["tknError"])
                return None
        headers={'Authorization':self.auth_token}        
        if formatRequest is not None and formatRequest != "text/dataframe"and formatRequest != "info":
            headers={'Authorization':self.auth_token,'Accept':formatRequest}        

        #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response=requests.get(self.data["url"]+route,headers=headers,verify=False)
        
        verboseprint("Status Code: "+ str(response.status_code),verbose)
        if response.ok:
            verboseprint(md.dictionary["accepted"],verbose)
            verboseprint(response.content,verbose)

            if(formatRequest==None or formatRequest=="text/json"):                
                data=response.json()
                #verboseprint(data,verbose)
                data=data["docs"]
                #print(type(data))
                #verboseprint(data,verbose)       

            if(formatRequest=="text/csv"):    
                #print(response.content)                
                data=response.content               
                data=str(data)                
                data=data.replace("\\r\\n","\n")
                data=data.replace('""','')         
            if(formatRequest=="text/csv+"):    
                #print(response.content)                
                data=response.content
                data=str(data)    
                data=data.replace("\\n","\n")                 
            if(formatRequest=="text/dataframe"):
                data=response.content
                data=json.loads(data)     
                #print(data)                     
                #data=data[0]                
                data=pd.DataFrame.from_dict(data)
            if(formatRequest=="info"):
                data=response.content
                data=str(data)
                data=data.replace("\\","")
            return data
        else:
            verboseprint(md.dictionary["error"],verbose)
            print(response.content)


    def clearFilename(self,filename:string):
        if (filename.endswith('.txt')):            
            filename = slice(0, -4)
        if (filename.endswith('.csv')):            
            filename = slice(0, -4)
        if (filename.endswith('.json')):            
            filename = slice(0, -5)
        return filename
    

    def deleteDataset(self,filename:string,verbose:bool=None):
        if verbose is None:
            verbose=self.verbose
        filename=self.clearFilename(filename)   
        if(self.tknExpTime-time.time()<=60):            
            result=self.updateTkn()
            if(result==False):
                print(md.dictionary["tknError"])
                return None
        headers={'Authorization':self.auth_token}           
       
        response=requests.delete(self.data["url"]+self.data["dataset_route"]+"/"+filename,headers=headers,verify=False)
        verboseprint("Status Code: "+ str(response.status_code),verbose)
        if response.ok:
            verboseprint(md.dictionary["accepted"],verbose)
            verboseprint(str(response.content).replace('\\\\',''),verbose)
        else:
            verboseprint(md.dictionary["error"],verbose)
            print(response.content)


    def postDataset(self,file:string=None,description:string=None,force:bool=False,verbose:bool=None):
        if verbose is None:
            verbose=self.verbose 
        if(self.tknExpTime-time.time()<=60):            
            result=self.updateTkn()
            if(result==False):
                print(md.dictionary["tknError"])
                return None 
        if file is None:
            file=self.data["file"]
        if description is None:
            description=self.data["description"]  
        headers={'Authorization':self.auth_token}          
        if(force==True):
            response=requests.post(self.data["url"]+self.data["dataset_route"]+"?force=true",headers=headers,verify=False,files={'file':open(file, 'rb'),'description':open(description, 'rb')})
        else: 
            response=requests.post(self.data["url"]+self.data["dataset_route"],headers=headers,verify=False,files={'file':open(file, 'rb'),'description':open(description, 'rb')})   

        verboseprint("Status Code: "+ str(response.status_code),verbose)
        if response.ok:
            verboseprint(md.dictionary["accepted"],verbose)
            #verboseprint(str(response.content).replace('\\\\',''),verbose)
            return response.content
        else:
            verboseprint(md.dictionary["error"],verbose)
            print(response.content)

def verboseprint(arg:str,verbose:bool):
    if verbose:
        print(arg)