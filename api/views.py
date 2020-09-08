from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from decimal import Decimal, ROUND_DOWN
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
		cpf		= request.data.get('cpf')		
		finance = request.data.get('finance')

		if not all([cpf, finance]):
			return Response({'success': False, 'detail':f'Parâmetros insuficientes {cpf} {finance}'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			int(cpf)
			finance = float(finance)
		except:
			return Response({'success': False, 'detail':'Parâmetros incorretos'}, status=status.HTTP_400_BAD_REQUEST)

		finance = Decimal(finance).quantize(Decimal('.01'), rounding=ROUND_DOWN)

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
			credit.save()
		except Exception as e:
			raise Exception(e)

		return analysis_serasa


class AnalysisNubank(APIView):
	def post(self, request):
		client = request.POST.get('id')
		password = request.POST.get('bank_password')
		qrcode = request.POST.get('qrcode')


class GroupAPI(APIView):
	def post(self, request, id=None):
		list_group	= request.data.get('group', [])
		group = list_group.split(',')

		if not all([group]):
			return Response({'success': False, 'detail':'Parâmetros insuficientes'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			person = Person.objects.get(pk=id)
		except:
			return Response({'success': False, 'detail':'Id do cliente não encontrado'}, status=status.HTTP_404_NOT_FOUND)

		group.append(person.cpf)

		scores = []
		total_finances = 0
		contacts = []

		for g in group:
			try:
				contact = CreditAnalysis.objects.get(person__cpf=g)
				scores.append(int(contact.score_serasa))
				total_finances += contact.person.finance
			except Exception as e:
				continue

			insert_contact = ContactPerson.objects.create(person=person, contact=contact.person)
			insert_contact.save()

			contacts.append(contact.person.nickname)
		
		analysis_group = AnalysisGroup(scores)
		
		obj = CreditAnalysis.objects.get(person=person)
		
		obj.analysis_group=analysis_group
		obj.finance_group=total_finances
		obj.save()
		
		calculators = CalcLoanPayment(total_finances)
		calculators.update({'names': contacts, 'finances': total_finances, 'score_serasa': analysis_group})

		response = {'success': True, 'calculators_group': calculators}

		return Response(response, status=status.HTTP_201_CREATED)