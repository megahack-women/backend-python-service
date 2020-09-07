from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import requests
import json

from api.models import *
from api.utils import *
from lib.analysis import *
from backend.settings import *
import local

class HelloWord(APIView):
	def get(self, request):
		return Response(True, status=status.HTTP_200_OK)


class PersonAPI(APIView):
	def post(self, request):
		return Response(request.data)
		cpf		= request.POST.get('cpf')		
		finance = request.POST.get('finance')

		if not all([cpf, finance]):
			return Response({'success': False, 'detail':f'Parâmetros insuficientes {cpf} {finance}'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			int(cpf)
			finance = float(finance)
		except:
			return Response({'success': False, 'detail':'Parâmetros incorretos'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			person = Person.objects.get(cpf=cpf)
		except: 
			person = None

		if person != None:
			return Response({'success': False, 'detail':'Cliente já cadastrado'}, status=status.HTTP_400_BAD_REQUEST)
		
		
		serializer = PersonModelSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()

			response = {'success': True, 'client': serializer.data}

			analysis_serasa = self.serasa(cpf)

			calculators = CalcLoanPayment(finance)
			calculators.update({'score_serasa': analysis_serasa, 'finance': finance})

			response['client'].update({'calculators': calculators, 'calculators_group': {}})

			return Response(response, status=status.HTTP_201_CREATED)
		
		return Response({'success': False, 'detail':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request, id=None):
		if id == None:
			return Response({'success': False, 'detail':'Parâmetros insuficientes'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			person = Person.objects.get(id=id)
		except:
			return Response({'success': False, 'detail':'Id do cliente não encontrado'}, status=status.HTTP_404_NOT_FOUND)

		serializer = PersonModelSerializer(person)

		credit = CreditAnalysis.objects.get(person=person)

		calculators = CalcLoanPayment(person.finance)
		calculators.update({'score_serasa': credit.score_serasa, 'finance': person.finance})

		# relationships = ContactPerson.objects.filter(person=person)
		
		response = {'success': True, 'client': serializer.data}
		response['client'].update({'calculators': calculators})

		return Response(response)

	def serasa(self, cpf):
		analysis_serasa = AnalysisSerasa(cpf)

		try:
			person = Person.objects.get(cpf=cpf)

			credit = CreditAnalysis.objects.create(person=person, score_serasa=analysis_serasa)
		except Exception as e:
			raise Exception(e)

		return analysis_serasa


class AnalysisNubank(APIView):
	def post(self, request):
		client = request.POST.get('id')
		password = request.POST.get('bank_password')
		qrcode = request.POST.get('qrcode')


class GroupAPI(APIView):
	def post(self, request):
		person	= request.POST.get('id')
		group	= request.POST.getlist('group', [])

		if not all([person, person]):
			return Response({'success': False, 'detail':'Parâmetros insuficientes'}, status=status.HTTP_400_BAD_REQUEST)

		scores = []
		total_finances = 0
		contacts = []

		for g in group:
			try:
				contact = CreditAnalysis.objects.get(person__cpf=g)
				scores.insert(contact.score_serasa)
				total_finances += contact.person.finance
			except:
				continue

			insert_contact = ContactPerson.objects.create(person=person, contact=contact.person)
			insert_contact.save()

			contacts.insert(contact.person)
		raise Exception(scores)
		analysis_group = AnalysisGroup(scores)
		
		obj = CreditAnalysis.objects.get(person__pk=person)
		obj.update(analysis_group=analysis_group, finance_group=total_finances)
		
		calculators = CalcLoanPayment(total_finances)
		calculators.update({'group': contacts})

		response = {'success': True, 'calculators_group': calculators}

		return Response(response, status=status.HTTP_201_CREATED)