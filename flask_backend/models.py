from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Circular(db.Model):
    __tablename__ = 'circular'
    __bind_key__ = 'db1'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    sender = db.Column(db.UnicodeText, nullable=False)
    received = db.Column(db.DateTime, nullable=False)
    subject = db.Column(db.UnicodeText, nullable=False)
    oid = db.Column(db.Integer, db.ForeignKey('observatory.id'))
    evtid = db.Column(db.Integer, db.ForeignKey('event.id'))
    cid = db.Column(db.Integer, db.ForeignKey('circular_body.id'))


    def __init__(self, id, sender, received, subject, oid, evtid, cid):
        self.id = id
        self.sender = sender
        self.received = received
        self.subject = subject
        self.oid = oid
        self.evtid = evtid
        self.cid = cid

    def __repr__(self):
    	return "<Circular '%s', '%s', '%s', '%s', '%s'>" %(self.id, self.sender, self.subject, self.oid, self.evtid)

class Circular_body(db.Model):
    __tablename__ = 'circular_body'
    __bind_key__ = 'db9'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    body = db.Column(db.UnicodeText, nullable=False)
    circular = db.relationship('Circular', backref="cid_circular")
    
    def __init__(self, id, body):
        self.id = id
        self.body = body
        
    def __repr__(self):
        return "<Circular_body '%s', '%s'>" %(self.id, self.cid)



class Event(db.Model):
    __tablename__ = 'event'
    __bind_key__ = 'db2'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    event = db.Column(db.UnicodeText, nullable=False, primary_key=True)
    evtType = db.Column(db.UnicodeText, nullable=False)
    trigger = db.Column(db.DateTime, nullable=True)
    ra = db.Column(db.Float, nullable=True)
    dec = db.Column(db.Float, nullable=True)
    ra_hms = db.Column(db.UnicodeText, nullable=True)
    dec_dms = db.Column(db.UnicodeText, nullable=True)
    error = db.Column(db.Float, nullable=True)
    circulars = db.relationship('Circular', backref="evtid_circular")
    notices = db.relationship('EventNotice', backref="evtid_notice")
    
    def __init__(self, id, event, evtType, trigger, ra, dec, ra_hms, dec_dms, error):
        self.id = id
        self.event = event
        self.evtType = evtType
        self.trigger = trigger
        self.ra = ra
        self.dec = dec
        self.raHMS = ra_hms
        self.decDMS = dec_dms
        self.error = error

    def __repr__(self):
        return "<Event ('%s', '%s', '%s', '%s', '%s')>" %(self.id, self.event, self.trigger, self.ra, self.dec)


class Observatory(db.Model):
    __tablename__ = 'observatory'
    __bind_key__ = 'db3'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    telescope = db.Column(db.UnicodeText, nullable=True)
    detector = db.Column(db.UnicodeText, nullable=True)
    fullName = db.Column(db.UnicodeText, nullable=True)
    mwid = db.Column(db.Integer, db.ForeignKey('mmmw.id'))
    circulars = db.relationship('Circular', backref="oid_circular")
    
    def __init__(self, id, tel, dtr, name, mwid):
        self.id = id
        self.mwid = mwid
        self.telescope = tel
        self.detector = dtr
        self.fullName = name
        
        
    def __repr__(self):
        return "<Observatory ('%s', '%s', '%s', '%s', '%s')>" %(self.id, self.telescope, self.detector, self.fullName, self.mwid)


class MMMW(db.Model):
    __tablename__ = 'mmmw'
    __bind_key__ = 'db8'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    wavelength = db.Column(db.UnicodeText, nullable=True)
    messenger = db.Column(db.UnicodeText, nullable=True)
    events = db.relationship('Observatory', backref="oid_event")
    
    def __init__(self, id, mw, mm):
        self.id = id
        self.wavelength = mw
        self.messenger = mm
        
    def __repr__(self):
        return "<MMMW ('%s', '%s', '%s')>" %(self.id, self.wavelength, self.messenger)


class Mission(db.Model):
    __tablename__ = 'mission'
    __bind_key__ = 'db4'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)
    basedir = db.Column(db.UnicodeText, nullable=True)
    notices = db.relationship("Notice", backref="mid_notice")
    events = db.relationship("EventNotice", backref="mid_event")
    
    def __init__(self, id, name, description, basedir):
        self.id = id
        self.name = name
        self.description = description
        self.basedir = basedir

    def __repr__(self):
        return "<Mission ('%s', '%s', '%s', '%s')>" %(self.id, self.name, self.description, self.basedir)


class Notice(db.Model):
    __tablename__ = 'notice'
    __bind_key__ = 'db5'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    mid = db.Column(db.Integer, db.ForeignKey('mission.id'))
    file = db.Column(db.UnicodeText, nullable=True)
    details = db.relationship('Detail', backref="full_notice")
    
    def __init__(self, id, mid, file):
        self.id = id
        self.mid = mid
        self.file = file
        
    def __repr__(self):
        return "<Notice ('%s', '%s', '%s')>" %(self.id, self.mid, self.file)


class Detail(db.Model):
    __tablename__ = 'detail'
    __bind_key__ = 'db6'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    nid = db.Column(db.Integer, db.ForeignKey('notice.id'))
    line = db.Column(db.Integer, nullable=False)
    key = db.Column(db.UnicodeText, nullable=True)
    textval = db.Column(db.UnicodeText, nullable=True)
    realval = db.Column(db.Float, nullable=True)
    arrval = db.Column(db.UnicodeText, nullable=True)
    
    def __init__(self, id, nid, line, key, textval, realval, arrval):
        self.id = id
        self.nid = nid
        self.line = line
        self.key = key
        self.textval = textval
        self.realval = realval
        self.arrval = arrval
        
    def __repr__(self):
        return "<Detail ('%s', '%s', '%s', '%s', '%s', '%s', '%s')>" %(self.id, self.nid, self.line, self.key, self.textval, self.realval, self.arrval)

class EventNotice(db.Model):
    __tablename__ = 'eventNotice'
    __bind_key__ = 'db7'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    mid = db.Column(db.Integer, db.ForeignKey('mission.id'))
    nid = db.Column(db.Integer, db.ForeignKey('notice.id'))
    tid = db.Column(db.Integer, nullable=False)
    evtid = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.Column(db.UnicodeText, nullable=True)
    trigger = db.Column(db.DateTime, nullable=True)
    ra = db.Column(db.Float, nullable=True)
    dec = db.Column(db.Float, nullable=True)
    ra_hms = db.Column(db.UnicodeText, nullable=True)
    dec_dms = db.Column(db.UnicodeText, nullable=True)
    error = db.Column(db.Float, nullable=True)
    
    def __init__(self, id, mid, nid, tid, evtid, event, trigger, ra, dec, ra_hms, dec_dms, error):
        self.id = id
        self.mid = mid
        self.nid = nid
        self.tid = tid
        self.evtid = evtid
        self.event = event
        self.trigger = trigger
        self.ra = ra
        self.dec = dec
        self.raHMS = ra_hms
        self.decDMS = dec_dms
        self.error = error
        
    def __repr__(self):
        return "<EventNotice (id: '%s', mid: '%s', tid: '%s', nid: '%s', evtid: '%s', event: '%s')>" %(self.id, self.mid, self.tid, self.nid, self.evtid, self.event)