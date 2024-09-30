from .utils import db
from sqlalchemy.dialects.postgresql import JSON
import datetime
from flask_login import current_user as user

requests_requestnotes = db.Table(
    'requestsnoterelationship',
    db.Column('request_id', db.Integer(), db.ForeignKey('requests.request_id')),
    db.Column('note_id', db.Integer(), db.ForeignKey('requestnotes.note_id'))
)

class RequestNotes(db.Model):
    """ Notes colume for requests """
    __tablename__ = "requestnotes"
    note_id = db.Column(db.Integer, primary_key=True)
    note    = db.Column(db.String)

    def __str__(self):
        return self.note
    
class Request(db.Model):
    """Requests Model."""
    __tablename__        = 'requests'
    request_id           = db.Column(db.Integer, primary_key=True)
    summary              = db.Column(db.String)
    catagory             = db.Column(db.String)
    operation            = db.Column(db.String)
    requestor_first_name = db.Column(db.String)
    requestor_last_name  = db.Column(db.String)
    requestor_email      = db.Column(db.String)
    requestor_team       = db.Column(db.String)
    submited_date        = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed_date       = db.Column(db.DateTime)
    status               = db.Column(db.String, default='Assigned')
    username             = db.Column(db.String)
    data                 = db.Column(JSON)
    notes                = db.relationship('RequestNotes', secondary=requests_requestnotes,
                                        backref=db.backref('requests', lazy='dynamic'), cascade='delete') 
    

    def add_note(self,comment):
        """Adding notes to requests"""
        try:
            note = RequestNotes()
            note.note = comment
            db.session.add(note)
            db.session.commit()
            self.notes.append(note)
            return True
        except Exception as e:
            print(e)
            raise
    
    
    def CreateSnapshotRequest(self,reqData):
        self.summary              = "Create Snapshot for "+reqData['hostname']
        self.requestor_first_name = user.first_name
        self.requestor_last_name  = user.last_name
        self.requestor_email      = user.email
        self.requestor_username   = user.username
        self.status               = "InProgress"        
        self.catagory             = "VirtualMachineSnapshot"
        self.operation            = "create"
        self.data                 = reqData
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self.request_id
    
    def DeleteSnapshotRequest(self,reqData):
        self.summary              = "Delete Snapshot for "+reqData['hostname']
        self.requestor_first_name = user.name
        self.requestor_last_name  = user.surname
        self.requestor_email      = user.email
        self.requestor_username   = user.username
        self.status               = "InProgress"        
        self.catagory             = "VirtualMachineSnapshot"
        self.operation            = "delete"
        self.data                 = reqData
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self.request_id
    
    @staticmethod
    def CloseRequest(request_id):      
        req = Request.query.filter_by(request_id=request_id).first()
        req.status = "Completed"
        db.session.merge(req)
        db.session.commit()