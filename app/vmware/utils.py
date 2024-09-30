from ..schema.vmware import vcenter, VirtualMachine

def vmware_scrape_job():
    try:
        vcs = vcenter.query.all()
        
        for obj in vcs:
            obj.get_virtual_machines()
        return None
    except Exception as e:
        print(e)