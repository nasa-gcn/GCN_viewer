from flask import current_app, Blueprint, abort, jsonify, render_template, request
from flask_backend.models import Circular, Event, Observatory, Mission, Notice, Detail, EventNotice, Circular_body
from flask_sqlalchemy import SQLAlchemy
from astropy.time import Time
import numpy as np

public = Blueprint('public', __name__, url_prefix='/')

def convertDateTime(datetime):
	if datetime!=None:
		return datetime.isoformat()
	else:
		return datetime

@public.route('/', methods=['GET'])
def gcn_viewer():
	#return "hello world"
	return render_template("index.html", token="test")

@public.route('/circular/', methods=['GET'])
def get_circular():
	circulars = Circular.query.all()
	savedGCN = [{'id': gcn.id, 'sender': gcn.sender, 'received': convertDateTime(gcn.received),
	'subject': gcn.subject, 'telescope': gcn.oid_circular.telescope, 'detector': gcn.oid_circular.detector,
	'obsid': gcn.oid, 'evtid': gcn.evtid, 'mwid': gcn.oid_circular.oid_event.id, 'wavelength': gcn.oid_circular.oid_event.wavelength, 'messenger': gcn.oid_circular.oid_event.messenger,
	} for gcn in circulars]
			
	return jsonify({'data': savedGCN})

@public.route('/circular/<id>', methods=['GET', 'POST'])
def update_circular(id):
	if request.method == 'POST':
		updatedCircular = Circular.query.filter_by(id=request.json['id']).first()
		updatedCircular.evtid = request.json['evtid']
		updatedCircular.oid = request.json['obsid']
		db.session.commit()
		return "Success"

	elif request.method == 'GET':
		gcn = Circular.query.filter_by(id=id).first()
		savedGCN = [{'id': gcn.id, 'sender': gcn.sender, 'received': convertDateTime(gcn.received),
				'subject': gcn.subject, 'telescope': gcn.oid_circular.telescope, 'detector': gcn.oid_circular.detector,
				'obsid': gcn.oid, 'evtid': gcn.evtid, 'mwid': gcn.oid_circular.oid_event.id, 'wavelength': gcn.oid_circular.oid_event.wavelength, 'messenger': gcn.oid_circular.oid_event.messenger,
				}]
		return jsonify({'data': savedGCN})

@public.route('/cbody/<id>', methods=['GET'])
def get_circular_body(id):
	gcn = Circular_body.query.filter_by(id=id).first()
	body = [{'id': gcn.id, 'body': gcn.body}]
	return jsonify({'data': body})

@public.route('/event/', methods=['GET'])
def get_event():
	events = Event.query.all()
	savedEvt = [{'id': evt.id, 'event': evt.event, 'eventType': evt.evtType, 'trigger': convertDateTime(evt.trigger), 
	'ra': evt.ra, 'raHMS': evt.ra_hms, 'dec': evt.dec, 'decDMS': evt.dec_dms, 'error': evt.error} for evt in events if evt.id != 99999]
	
	return jsonify({'data': savedEvt})

@public.route('/event/<id>', methods=['GET', 'POST'])
def update_event(id):

	if request.method == 'POST':
		removedEvt = Event.query.filter_by(id=request.json['id']).first()
		db.session.delete(removedEvt)
		db.session.commit()
		return "Success"

	elif request.method == 'GET':
		evt = Event.query.filter_by(id=id).first()
		savedEvt = [{'id': evt.id, 'event': evt.event, 'eventType': evt.evtType, 'trigger': convertDateTime(evt.trigger), 
		'ra': evt.ra, 'raHMS': evt.ra_hms, 'dec': evt.dec, 'decDMS': evt.dec_dms, 'error': evt.error}]
		return jsonify({'data': savedObs})

	return jsonify({'data': savedEvt})

@public.route('/observatory/', methods=['GET'])
def get_obs():
	allObs = Observatory.query.all()
	savedObs = [{'id': obs.id, 'telescope':obs.telescope, 'detector':obs.detector, 'full_name':obs.fullName, 
	'mwid': obs.mwid, 'wavelength': obs.oid_event.wavelength, 'messenger': obs.oid_event.messenger} for obs in allObs if obs.id < 1000]

	return jsonify({'data': savedObs})

@public.route('/observatory/<id>', methods=['GET', 'POST'])
def update_obs(id):
	if request.method == 'POST':
		if request.json['mode'] == 1:
			print(request.json['detector'])
			obsLine = Observatory(request.json['id'], request.json['telescope'], request.json['detector'], request.json['fullName'], request.json['mwid'] )
			db.session.add(obsLine)
		elif request.json['mode'] == 0:
			updatedObs = Observatory.query.filter_by(id=request.json['id']).first()
			updatedObs.telescope = request.json['telescope']
			updatedObs.detector = request.json['detector']
			updatedObs.fullName = request.json['fullName']
			updatedObs.mwid = request.json['mwid']
		elif request.json['mode'] == -1:
			removedObs = Observatory.query.filter_by(id=request.json['id']).first()
			db.session.delete(removedObs)
		db.session.commit()
		return "Success"

	elif request.method == 'GET':
		obs = Observatory.query.filter_by(id=id).first()
		savedObs = [{'id': obs.id, 'telescope':obs.telescope, 'detector':obs.detector, 'full_name':obs.fullName, 
		'mwid': obs.mwid, 'wavelength': obs.oid_event.wavelength, 'messenger': obs.oid_event.messenger}]
		return jsonify({'data': savedObs})


@public.route('/notice/', methods=['GET'])
def get_notice():
	allNotice = Notice.query.all()
	savedNotice = [{'id': notice.id, 'mission': notice.mid_notice.name.capitalize()} for notice in allNotice]

	return jsonify({'data': savedNotice})

@public.route('/notice/<id>', methods=['GET'])
def get_detail(id):
	notice = Notice.query.filter_by(id=id).first()
	detail = Detail.query.filter_by(nid=id)
	savedNotice = [{'id': notice.id, 'id': notice.mid, 'mission': notice.mid_notice.name.capitalize(), 
	'title': detail.filter_by(key="TITLE").first().textval,
	'date': Time(detail.filter_by(key="NOTICE_DATE").first().realval, format='mjd').isot, 'type': detail.filter_by(key="NOTICE_TYPE").first().textval }]

	return jsonify({'data': savedNotice})