from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import os
import json
import csv
import fl_tar
import io
import shutil
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
media_root=settings.MEDIA_ROOT
nodes_path=os.path.join(media_root,'nodes')

def watch(request):
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



try:
    general_upload= os.path.join(settings.MEDIA_ROOT,'general_upload')
    os.makedirs(general_upload)
except os.error:
    pass

@csrf_exempt
def upload(request):
    node=request.GET.get('node')
    node_path=os.path.join(nodes_path,node)
    file_dict = request.FILES
    file_dir= os.path.join(general_upload,node)
    try:
        os.makedirs(file_dir)
    except os.error:
        pass

    for name, fl in file_dict.items():
        catch = io.BytesIO()    
        for chunk in fl.chunks():
            catch.write(chunk) 
            
        catch.flush()
     
        file_path=os.path.join(file_dir,fl.name)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path,'wb') as general_file:
            general_file.write(catch.getvalue())
            
    un_tgz_all(file_dir) 
    merge_all(file_dir,node_path)
    dc={
        'status':'success'
    }
    return HttpResponse(json.dumps(dc),content_type="application/json")

def un_tgz_all(path):
    os.chdir(path)

    for item in os.listdir(path):
        if item.endswith('.tar.gz'):
            fl_tar.un_tgz(item)
            os.remove(item)
    os.chdir('data')
    for item in os.listdir('.'):
        shutil.move(item,'../'+item)
    os.chdir('..')
    shutil.rmtree('data')

def merge_all(src,dst):
    for root, dirs, files in os.walk(src):
        rel_root=os.path.relpath(src,root)
        dst_root=os.path.join(dst,rel_root)
        try:
            os.makedirs(dst_root)
        except os.error:
            pass
        
        for fl in files:
            merge_file(os.path.join(root,fl),os.path.join(dst_root,fl))
 
def merge_file(src,dst):
    if src.endswith('.csv'):
        merg_csv(src, dst)
    else:
        shutil.copy(src, dst)

def merg_csv(src,dst):
    if os.path.exists(dst):
        with open(src,'rb') as f:
            with open(dst,'a+b') as dst_file:
                dst_file.writelines(f.readlines()[1:])
    else:
        shutil.copy(src,dst)
