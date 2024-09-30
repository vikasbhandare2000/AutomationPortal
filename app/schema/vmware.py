from .utils import db
from app.utils import encode, decode
from pyVmomi import vim
from time import strftime, localtime
import time
import logging
import ssl, json
from pyVim import connect

class vcenter(db.Model):
    __tablename__ = 'vcenter_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String) 
    description = db.Column(db.String) 
    url = db.Column(db.String)
    site = db.Column(db.String)
    credentials = db.Column(db.String)
    status = db.Column(db.Boolean, default=True)


    def get_creds(self):
        return decode(self.credentials)

    def set_creds(self,creds):
        self.credentials = encode(creds)
        
    def connect(self) -> None:
        username = (json.loads(decode(self.credentials).replace('\'','\"')))['username']
        password = (json.loads(decode(self.credentials).replace('\'','\"')))['password']
        logger = logging.getLogger("vmware")
        logger.info("Authenticating to vCenter "+ self.name+" with username "+username)
        ssl._create_default_https_context = ssl._create_unverified_context
        self.content = connect.SmartConnect(host=self.url,
                                            user=username,
                                            pwd=password,
                                            port=int(443)).RetrieveContent()
        if self.content:
            logger.info("Connected successfully to vCenter "+ self.url+" with username "+username)
        else:
            logger.info("Connection failed to vCenter "+ self.url+" with username "+username)
            
    def disconnect(self) -> None:
        self.content.sessionManager.Logout()
        
    def get_virtual_machines(self) -> None:       
        self.connect()
        logger = logging.getLogger("vmware")
        logger.info("Fecthing VirtualMachines details from vCenter "+self.url)            
        objview = self.content.viewManager.CreateContainerView(self.content.rootFolder,
                                                          [vim.VirtualMachine],
                                                          True)
        virtulmachines = objview.view

        for vm in virtulmachines:
            instance = {
                "name"  : vm.name,
                "mobid" : vm._GetMoId()
            }
            print(instance)

            v = VirtualMachine.query.filter_by(mobid=vm._GetMoId()).filter_by(vcenterid=self.id).first()

            if not v:
                v = VirtualMachine(self.id)
            v.put(vm)
        
    def get_object(self,vimtype,name):

        obj = None
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vimtype], True)

        for containerObject in container.view:
            
            if (containerObject.name).lower() == (name).lower():
                obj = containerObject

        return obj  

      
class Datacenter():
    
    @staticmethod
    def get_datacenter(dc):
        if isinstance(dc, vim.Datacenter):
            return dc.name            
        else:
            return Datacenter.get_datacenter(dc.parent) 
          
class VirtualMachine(db.Model):
    __tablename__ = 'virtualmachine'   

    #basic details
    vcenterid = db.Column(db.Integer, db.ForeignKey("vcenter_items.id"))

    #vm object details 
    name = db.Column(db.String)
    type = db.Column(db.String)
    mobid = db.Column(db.String)
    cpu = db.Column(db.BigInteger)
    memory = db.Column(db.BigInteger)
    hostname = db.Column(db.String)
    numnic = db.Column(db.BigInteger)
    ipaddress = db.Column(db.String)
    guestos = db.Column(db.String)
    host = db.Column(db.String)
    datacenter = db.Column(db.String)
    istemplate = db.Column(db.Boolean)
    toolsstatus = db.Column(db.String)
    guestversion = db.Column(db.String)
    powerstate = db.Column(db.String)
    connectionstate = db.Column(db.String)
    isactive =db.Column(db.Boolean,server_default='t')
    #parent linking
    parentname = db.Column(db.String)
    parentmobid = db.Column(db.String)
    #resource details
    datastore = db.Column(db.String)
    network = db.Column(db.String)
    last_updated = db.Column(db.TIMESTAMP, server_default=db.func.now(),
                             onupdate=db.func.current_timestamp())
    __table_args__ = (
        db.PrimaryKeyConstraint('mobid', 'vcenterid'),
        {},)
    #extra inventory parameters
    disk_space_mb = db.Column(db.String)
    host_type = db.Column(db.String)
    vm_catagory = db.Column(db.String)
    last_patched = db.Column(db.TIMESTAMP)
    patch_windows = db.Column(db.String)
    installed_antivirus = db.Column(db.String)
    uptime = db.Column(db.String)
    domain = db.Column(db.String)
    pool_name = db.Column(db.String)

    
    def __init__(self, vc) -> None:
            self.vcenterid = vc
            self.type = 'VirtualMachine'
            self.description = 'Virtual Machine Object'

    def put(self,vm):
        update = False
        try:
            if isinstance(vm,vim.VirtualMachine):
                if self.vcenterid:
                    update = True
                self.mobid = vm._GetMoId()
                #vm object details
                self.name            = vm.name
                self.hostname        = vm.summary.guest.hostName
                self.cpu             = int(vm.summary.config.numCpu)
                self.memory          = int(vm.summary.config.memorySizeMB)
                self.numnic          = int(vm.summary.config.numEthernetCards)
                self.ipaddress       = vm.summary.guest.ipAddress
                self.guestos         = vm.summary.config.guestFullName
                self.istemplate      = vm.summary.config.template
                if vm.summary.config.template:
                    self.type = 'VirtualMachine Template'
                self.toolsstatus     = vm.summary.guest.toolsStatus
                self.guestversion    = vm.config.version
                self.powerstate      = vm.summary.runtime.powerState
                self.connectionstate = vm.summary.runtime.connectionState
                self.isactive        = True
                self.parentname      = vm.parent.name
                self.parentmobid     = vm.parent._GetMoId()
                self.host            = vm.summary.runtime.host.name
                self.datacenter      = Datacenter.get_datacenter(vm.parent)
                tdatastore = [] 
                tnetwork = [] 
                for d in vm.datastore: tdatastore.append(d.name)
                for d in vm.network: tnetwork.append(d.name)
                self.datastore       = str(tdatastore)
                self.network         = str(tnetwork)
                self.installed_antivirus = vm.summary.config.annotation
                if update:
                    db.session.merge(self)
                    print("updated")
                else:
                    db.session.add(self)
                    print("added")
                db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return e

    def get_snapshot_details(self):
        parent = vcenter.query.filter_by(id=self.vcenterid).first()        
        parent.connect()
        vm = parent.get_object(vim.VirtualMachine,self.name)
        if vm.snapshot:
            snaps = VirtualMachine.trace_snapshot(vm.snapshot.rootSnapshotList)              
            for snap in snaps:
                snap['uuid'] = self.mobid
            return snaps
        else:
            return []
        
    def create_snapshot(self, snap_details):
        try:
            vc = vcenter.query.filter_by(id=self.vcenterid).first()
            vc.connect()
            vm = vc.get_object(vim.VirtualMachine,self.name)
            snaps = self.get_snapshot_details()                
            if len(snaps) <= 2:
                description = snap_details['comment']
                dumpMemory = False
                quiesce = True                    
                task = vm.CreateSnapshot(snap_details['name'], description, dumpMemory, quiesce)
                if VirtualMachine.wait_for_task(task) == 'success':
                    print('Snapshot Created sucessfully')
                    return True
                else:
                    return False
            else:
                print("maximum limit exceeded...")
                return False
        except Exception as e:
            print(e)
        

    def delete_snapshot(self,snap_details):
        try:
            vc = vcenter.query.filter_by(id=self.vcenterid).first()
            vc.connect()
            vm = vc.get_object(vim.VirtualMachine,self.name)               
            snapshot_tree = vm.snapshot.rootSnapshotList
            
            for child in snapshot_tree:                    
                if child.name == snap_details['snap_name']:
                    task = child.snapshot.RemoveSnapshot_Task(removeChildren=False)
                    self.wait_for_task(task)
                    return True
            return False
        except Exception as e:
            print(e)

    
    @staticmethod
    def trace_snapshot(snapshots):
        snapshot_data = []

        for snapshot in snapshots:
            snap = {"name" : snapshot.name, "createdAt" : str(snapshot.createTime)[:19], "Description" : snapshot.description}
            snapshot_data.append(snap)
            snapshot_data = snapshot_data + VirtualMachine.trace_snapshot(
                                            snapshot.childSnapshotList)
        return snapshot_data

    @staticmethod
    def wait_for_task(task):
    # wait for a vCenter task to finish 

        task_done = False
        while not task_done:
            if task.info.state == 'success':
                return task.info.state

            if task.info.state == 'error':
                task_done = True
                return 'error'
