import json
import datetime as dat
import operator as op
import requests as re




bundle = '''{
  "resourceType":"Bundle" ,
  "type":"transaction",
  "entry": [{"request": {
                        "method":"POST",
                        "url": "Observation"},
						
						"resource":{
						"resourceType":"Observation",
						"status":"final",
						"valueCodeableConcept":{
						"code": {
						"coding": {
                "system": "gcharts" ,
                "code":  %d ,
                "display": "%s"}}},
				"subject":{
          "reference": "Patient/%d"
        },"valueString":"%s" }}]}'''

headers = {"content-type":"application/fhir+json;charset=utf-8"}




def goGetLtst(cat,code,pat,validWx,*kwargs):

    dtt = (dat.datetime.now()- dat.timedelta(days=7*validWx)).date()
    if kwargs:
        Obj = re.get('https://fhirtest.uhn.ca/baseDstu3/{}?code={}&patient={}&date=ge{}&status=final&_sort=date&_count={}&_format=json&_pretty=true'.format(cat,code,pat,dtt.strftime('%Y-%m-%d'),kwargs[0]['count']))
    else:
        Obj = re.get('https://fhirtest.uhn.ca/baseDstu3/{}?code={}&patient={}&date=ge{}&status=final&_sort=date&_format=json&_pretty=true'.format(cat,code,pat,dtt.strftime('%Y-%m-%d')))
    ObjJson  = json.loads(Obj.text)
    
    return ObjJson

def handleIntResJs (js):
    res=[]
    if 'entry' in js.keys():
        for i in js['entry']:
            res.append({i['resource']['code']['coding'][0]['code']:{i['resource']['valueQuantity']['value']:i['resource']['valueQuantity']['unit']}})
    return res

def getNumOneValList(lst):
    num=0
    if lst:
        num = lst[0].values()[0].values()[0]
    return num
        

def goGetConProfile(pat):

    Obj = re.get('https://fhirtest.uhn.ca/baseDstu3/Condition?_patient={}&_verificationStatus=confirmed&_code:coding:system="http://snomed.info/sct"&_format=json&_pretty=true'.format(pat))
    ObjJson  = json.loads(Obj.text)
    return ObjJson

def checkCon(js):
    if 'entry' in js.keys():

            for x in js['entry'][:]:
                if x['resource']['clinicalStatus'] not in ['active','recurrence'] or x['resource']['verificationStatus']!='confirmed':
                    js['entry'].remove(x)
            if js['entry']:
                return js
            else:
                return None
def condDicter(js):
    net={}
    if 'entry' in js.keys():
        for x in js['entry']:
               
            net.update({x['resource']['code']['coding'][0]['code']:x['resource']['code']['coding'][0]['display']})
    
    return net
