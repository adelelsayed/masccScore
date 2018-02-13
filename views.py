# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from masccIndex.handy import *

# Create your views here.

chronicObstructivePulmonaryCodes = {'13645005':'chronic obstructive pulmonary disorder',
                                    '313299006':'Severe chronic obstructive pulmonary disease',
                                    '313296004':'Mild chronic obstructive pulmonary disease',
                                    '87433001':'Pulmonary emphysema',
                                    '40100001':'Obliterative bronchiolitis',
                                    '313297008':'Moderate chronic obstructive pulmonary disease',
                                    '135836000':'End stage chronic obstructive airways disease',
                                    '196001008':'Chronic obstructive pulmonary disease with acute lower respiratory infection',
                                    '195951007':'Acute exacerbation of chronic obstructive airways disease',
                                    '106001000119101':'Chronic obstructive lung disease co-occurrent with acute bronchitis'}

dehydrationCodes = {'34095006':'Dehydration','427784006':'Hypernatremic dehydration',
                    '1601000119105':'Moderate dehydration ', '212971003':'Deprivation of water',
                    '450316000':'Severe dehydration', '190894003':'Isonatremic dehydration',
                    '162685008':'On examination - dehydrated', '1611000119108':'Mild dehydration',
                    '78812008':'Neonatal dehydration', '112421000119102':'Dehydration due to radiation',
                    '735909008':'Dehydration following exertion'}

solidTumorCodes = {'55342001':'Neoplastic disease','399956005':'Melanocytic neoplasm', '255050003':'Tumor of unknown origin or ill-defined site',
                   '302862001':'Fibro-osteoma', '118616009':'Neoplastic disease of uncertain behavior',
                   '302861008':'Chondromatosis', '254289008':'Post-transplant neoplasia',
                   '55352002':'Familial neoplastic disease', '255046005':'Neuroendocrine tumor',
                   '399343007':'Chromaffinoma', '402874001':'Neoplasm of nerve sheath origin',
                    '393564001':'Glioma', '443790001':'Giant cell tumor',
                   '402877008':'Rhabdomyomatous neoplasm', '126736007':'Neoplasm of blood vessel',
                   '402878003':'Germ cell tumor', '127331007':'Neoplasm by body site ', '302835009':'Pheochromocytoma',
                   '416402001':'Gestational trophoblastic disease', '254827004':'Lipomatous tumor', '371004008':'Rupture of neoplasm',
                   '402123007':'Human papillomavirus associated intraepithelial neoplasia', '363346000':'Malignant neoplastic disease',
                   '414825006':'Neoplasm of hematopoietic cell type', '28386007':'Pericarditis co-occurrent and due to neoplasia',
                   '20376005':'Benign neoplastic disease', '99741000119100':'Adenocarcinoma in situ in villous adenoma',
                   '255127006':'Local tumor spread','109355002':'Carcinoma in situ', '404042005':'Pigmented neuroectodermal tumor of infancy',
                   '444231005':'Thymoma'}

hematologyCodes = {'414823004':'Neoplasm affecting hematopoietic structure','445738007':'Myelodysplastic/myeloproliferative disease',
                   '93720005':'Primary malignant neoplasm of bone marrow', '93143009':'Leukemia, disease', '397009000':'Mast cell malignancy',
                   '109993000':'Chronic myeloproliferative disorde', '109995007':'Myelodysplastic syndrome', '94217008':'Secondary malignant neoplasm of bone marrow',
                   '443495005':'Neoplasm of lymphoid system structure', '118612006':'Malignant histiocytosis'}

fungalInfectionCodes={'3218000':'Mycosis','240775001':'Disseminated hyalohyphomycosis', '110276005':'Deep mycosis', '86348002':'Mycotic endocarditis',
                      '471379007':'Necrotizing mycotic dermatitis', '444064003':'Infection caused by Scedosporium boydii', '721277003':'Fetus or newborn infection caused by fungus',
                      '59277005':'Zygomycosis', '29530003':'Fungal granuloma',
                      '111908007':'Branchiomycosis', '26053008':'Infection caused by Ascomycetes', '372935001':'Infection caused by Penicillium',
                      '721794002':'Infection caused by Malassezia', '312146001':'Fungal infection by site', '59258008':'Infection caused by Deuteromycetes',
                      '714113003':'Linear gingival erythema caused by fungus', '42386007':'Cryptococcosis',
                      '399314004':'Systemic mycosis', '252402000':'Mossy foot disease', '410038006':'Eumycotic mycetoma', '240773008':'Hyalohyphomycosis', '78999002':'Opportunistic mycosis'}

class TheView (viewsets.ViewSet):

    def view(self,request,patient):

        self.patient = int(self.kwargs['patient'])
        self.score= 0
        '''neutropenia'''
        
        self.anc = getNumOneValList(handleIntResJs(goGetLtst('Observation','751-8,753-4',self.patient,1,{'count':1})))
        
        
        '''assuming that temp unit is 'c '''
        '''taking temp as sole indicator of FN sympotms severity'''
        self.temp= getNumOneValList(handleIntResJs(goGetLtst('Observation','415945006,415882003',self.patient,1,{'count':1})))
        if self.anc and self.temp:
            if self.anc <= 0.5 and self.temp > 37: self.score += 5
            elif self.anc <= 0.5 and self.temp > 39: self.score += 3

        '''SBP'''
        self.sbp = getNumOneValList(handleIntResJs(goGetLtst('Observation','85354-9',self.patient,1,{'count':1})))
        if self.sbp:
            if self.sbp > 90: self.score += 5

        '''age'''
        self.demosObj = re.get('https://fhirtest.uhn.ca/baseDstu3/Patient?_id={}'.format(self.patient))
        self.demosJson = json.loads(self.demosObj.text)
        self.dob = dat.datetime.strptime(self.demosJson['entry'][0]['resource']['birthDate'],'%Y-%m-%d')
        self.ageYrs =  (dat.datetime.today()).year - self.dob.year

        if self.ageYrs:
            if self.ageYrs < 60: self.score +=2

        '''visit'''

        self.curVisit = re.get('''http://hapi.fhir.org/baseDstu3/Encounter?patient={}&_status='arrived,triaged,in-progress'&_type:text='outpatient'&_format=json&_pretty=true'''.format(self.patient))
        if self.curVisit:
            self.score +=3



        self.problemList = goGetConProfile(self.patient)
        self.activeProblemList = checkCon(self.problemList)


        '''deydration requiring parenteral intervention assuming it is documented on those codes'''
        self.dehydrationInd = dict(set((condDicter(self.activeProblemList)).items()).intersection(set(dehydrationCodes.items())))
        if not self.dehydrationInd:
            self.score +=3

        '''chronic obstructive pulmonary disorder assuming it is documented using those codes'''
        self.pulmonaryInd = dict(set((condDicter(self.activeProblemList)).items()).intersection(set(chronicObstructivePulmonaryCodes.items())))
        if not self.pulmonaryInd:
            self.score +=4

        '''solid tumor assuming it is documented using those codes'''
        self.solidTumorInd = dict(set((condDicter(self.activeProblemList)).items()).intersection(set(solidTumorCodes.items())))

        '''hematology disease assuming it is documented using those codes'''
        self.hematologyInd = dict(set((condDicter(self.activeProblemList)).items()).intersection(set(hematologyCodes.items())))

        '''past fungal infection assuming it is documented using those codes'''
        self.fungalInfectionInd = dict(set((condDicter(self.problemList)).items()).intersection(set(fungalInfectionCodes.items())))

        if self.solidTumorInd or self.hematologyInd:
            if not self.fungalInfectionInd:
                self.score += 4
        





        return HttpResponse('Score is {}'.format(self.score))


