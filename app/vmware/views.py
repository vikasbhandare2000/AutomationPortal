from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from ..main.utils import roles_required
from ..schema.vmware import vcenter, VirtualMachine
from ..schema.tracking import Request
from ..schema.utils import db
from ..utils import Page
import logging
import json
from app.utils import resp


vmware = Blueprint('vmware', __name__,
                 template_folder='templates')

@vmware.app_context_processor
def utility_processor():
    def get_vcname(id):
        try:
            return vcenter.query.filter_by(id=id).first().name
        except:
            return 'NULL'
    return dict(get_vcname=get_vcname)

@vmware.app_context_processor
def utility_processor():
    def human_time(seconds):
        if seconds:
            hours = str((seconds//3600)%24)
            min = str((seconds%3600)//60)
            sec = str((seconds%3600)%60)
            days = str(int((seconds//3600)/24))
            return "{} days {} hours {} mins {} sec".format(days,hours, min, sec)
        else:
            return "0"
    return dict(human_time=human_time)

@vmware.app_context_processor
def utility_processor():
    def prity_time(tm):
        return tm
        return tm.strftime("%Y-%m-%d %H:%M:%S")
    
    
    return dict(prity_time=prity_time)


@vmware.route('/')
def vmware_dashboard():
    page = Page("vmware","VMWare Dashabord")
    return render_template('vmware.html',page=page)

#Route to List vcenters 
@vmware.route('/vcenters',methods=['GET','POST'])
@login_required
@roles_required(['VMWARE'])
def get_vcenters():
    logger = logging.getLogger('vmware')
    if request.method == 'GET':
        vc = vcenter.query.all()
        logger.info('Listing all the vcenters')
        return render_template('vcenters.html',data=vc)
    elif request.method == 'POST':
        data = json.loads(request.data)
        for key in list(data.keys()):
            if data[key] == "":
                return resp(400,"Bad Request, Missing required parameters")
            else:
                continue
        try:
            if vcenter.query.filter_by(site=data["site"]).filter_by(name=data["name"]).first():
                vc = vcenter.query.filter_by(site=data["site"]).filter_by(name=data["name"]).first()
                vc.site = data["site"]
                vc.description = data["description"]
                vc.url = data["url"]
                vc.set_creds(str(data["credentials"]))
                db.session.merge(vc)
                db.session.commit()
                return resp(201,"Vcenter Already Exists, Hence updated the data.")
            
            vc = vcenter()
            vc.name = data["name"]
            vc.site = data["site"]
            vc.description = data["description"]
            vc.url = data["url"]
            vc.set_creds(str(data["credentials"]))
            db.session.add(vc)
            db.session.commit()

            return resp(200,"vCenter Details has been added succefully.")
        except Exception as e:
            print(e)
            return resp(500,"Internal Error, Something Went Wrong.")
    
@vmware.route('/v1/api/vcenter/<vcenter_id>',methods=['GET','POST','DELETE'])
@login_required
@roles_required(['VMWARE'])
def vcenter_details(vcenter_id=0):
    if request.method == 'GET':
        if vcenter_id != 0:
            vc = vcenter.query.filter_by(id=vcenter_id).first()            
           
            return jsonify(
                {
                  "name": vc.name, 
                  "id" : vc.id, 
                  "site": vc.site,
                  "url" : vc.url,
                  "description" : vc.description,
                  "username" : json.loads((vc.get_creds()).replace("'",'"'))['username']
                  
                 })    
    elif request.method == 'DELETE':
        if vcenter_id != 0:
            vc = vcenter.query.filter_by(id=vcenter_id).first() 
            if vc: 
                try:          
                    db.session.delete(vc)
                    db.session.commit()
                    return resp('200', 'vCenter '+vc.name+' deleted successfully.')
                except Exception as e:
                    return resp('500','Internal Error') 

@vmware.route('/ui/snapshot', methods=['GET'])
@login_required
def snapshot():    
    vc = vcenter.query.all()
    return render_template('snapshot.html',vcenters=vc)

@vmware.route('/v1/api/snapshot', methods=['POST','PUT','DELETE'])
@login_required
def api_snapshot():    
    if request.method == 'POST':
        data = json.loads(request.data)
        host = VirtualMachine.query.filter_by(name=data['hostname']).first()
        if host:
            snap = host.get_snapshot_details()
            return jsonify(snap)
        else:
            return resp(404, "Server "+data['hostname']+" Not Found")
    elif request.method == 'PUT':
        # For Create Snapshot
        #from .utils import SnapshotMail
        data = json.loads(request.data)
        host = VirtualMachine.query.filter_by(name=data['hostname']).first()
        
        #sm = SnapshotMail()
        
        reqData = {
            "hostname"      : data['hostname'],
            "vcenter"       : vcenter.query.filter_by(id=host.vcenterid).first().name,
            "snapshot_name" : data['name'],
            "comment"     : data['comment']
        }
        
        req = Request()
        request_id = req.CreateSnapshotRequest(reqData)  
        request_obj = Request.query.filter_by(request_id=request_id).first()
        
        if host.create_snapshot(data): 
            #send Snapshot creation mail 
            data['status'] = 'success'
            #sm.create_snapshot(host,data)
            request_obj.add_note(f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} :: Snapshot Created Successfully")
            Request.CloseRequest(request_id)
            return resp(200,"Snapshot Created Successfully")
        else:
            data['status'] = 'unsuccessful'
            # sm.create_snapshot(host,data)
            # request_obj.add_note(f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} :: Snapshot Creation failed with Error")
            # Request.CloseRequest(request_id)
            return resp(500,"Snapshot Creation failed with Error")
    else:
        # from .utils import SnapshotMail
        data = json.loads(request.data)
        host = VirtualMachine.query.filter_by(vcenterid=data['vcenter']).filter_by(name=data['hostname']).first()
        # sm = SnapshotMail()
        
        print(data)
        
        reqData = {
            "hostname"      : data['hostname'],
            "vcenter"       : vcenter.query.filter_by(id=host.vcenterid).first().name,
            "snapshot_name" : data['snap_name'],
            "comment"     : data['comment']
        }
        
        # req = Request()
        # request_id = req.DeleteSnapshotRequest(reqData)  
        # request_obj = Request.query.filter_by(request_id=request_id).first()
        
        
        if host.delete_snapshot(data): 
            data['status'] = 'success'
            # sm.delete_snapshot(host,data)
            # request_obj.add_note(f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} :: Snapshot Deleted Successfully")
            # Request.CloseRequest(request_id)
            return resp(200,"Snapshot Deleted Successfully")
        else:
            data['status'] = 'unsuccessful'
            # sm.delete_snapshot(host,data)
            # request_obj.add_note(f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} :: Snapshot Deletion failed with Error")
            # Request.CloseRequest(request_id)
            return resp(500,"Snapshot Deletion failed with Error")
    
@vmware.route('/inventory/scan')
@login_required
@roles_required(['VMWARE'])
def inventory_scan():
    from .utils import vmware_scrape_job
    
    vmware_scrape_job()
    
    return "done"

@vmware.route('/inventory')
@login_required
@roles_required(['VMWARE'])
def inventory():

    vms = VirtualMachine.query.all()
    return render_template('inventory.html',data=vms)


@vmware.route('/<vc_name>/autocomplete')
@vmware.route('/autocomplete')
@login_required
def get_hostnames(vc_name=None):
    if vc_name:        
        js = []
        vc = vcenter.query.filter_by(name=vc_name).first()
        term =request.args.get('term')
        if not vc: 
            return resp(404,"vCenter Not Found")
        vms = VirtualMachine.query.filter_by(vcenterid = vc.id).filter(VirtualMachine.name.ilike(f'%{term}%')).all()
        for v in vms:
            js.append(v.name)
        return jsonify(js)
    else:
        js = []
        term =request.args.get('term')
        vms = VirtualMachine.query.filter(VirtualMachine.name.ilike('%' + term + '%')).all()
        for v in vms:
            js.append({"name": v.name,"vc": vcenter.query.filter_by(id=v.vcenterid).first().name})
        return jsonify(js)