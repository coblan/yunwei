from django.shortcuts import render
from django.conf import settings
import os
import json
import csv

# Create your views here.

def watch(request):
    media_root=settings.MEDIA_ROOT
    nodes_path=os.path.join(media_root,'nodes')
    nodes=os.listdir(nodes_path)
    
    ctx={
        'nodes':json.dumps( nodes )
    }
    
    node=request.GET.get('node',None)
    if node:
        node_path=os.path.join(nodes_path,node)
        files=os.listdir(node_path)
        ctx['files']=json.dumps(files)
        
        fl=request.GET.get('fl',None)
        if fl:
            file_path=os.path.join(node_path,fl)
            ctx['data']=json.dumps(parse_csv(file_path))
        
    return render(request,'watch/index.html',context=ctx)
    

def parse_csv(path):
    with open(path,'rb') as f:
        reader = csv.DictReader(f)
        dc={}
        for key in reader.fieldnames:
            dc[key]=[]
        for row in reader:
            for key in reader.fieldnames:
                dc[key].append(row[key])
    return dc