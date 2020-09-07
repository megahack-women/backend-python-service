from api.models import *

from django.db import transaction

from decouple import config, Csv
import os, requests, json, random

from pynubank import Nubank

def AnalysisNubank(cpf, password, uuid):
    nu = Nubank()

    nu.authenticate_with_qr_code(cpf, password, uuid)

    bills = nu.get_bills()
    transactions = nu.get_account_statements()

    return True

def AnalysisSerasa(cpf):
    url = f"{config('URL_PROCOB')}{cpf}"
    header = {'X-Api-Key': f"{config('KEY_PROCOB')}"}

    try:
        r = requests.get(url, headers=header)
        response = r.json()
    except:
        return False
    
    content = response.get('content', {})

    #Se acabar os créditos da API...
    if response.get('code', '999') in ['002','999']:
        content = {
            'advertencias': {
                'p': random.choice(list({0,1}))
            },
            'score_serasa': {
                'conteudo': {
                    'score': random.randint(300, 1000) 
                }
            }
        }
    elif response.get('code') != '000':
        return False

    score = content.get('score_serasa', {}).get('conteudo', {}).get('score', 0)
    
    score = int(score)

    return score

def AnalysisGroup(scores=list):
    divider = 0
    
    for s in scores:
        if s >= 700:
            percentage = (((s-1000)/1000)*-3)

            divider += percentage

    dividend = sum(scores)

    total = dividend/divider

    return total

def CalcLoanPayment(value):
    payment_max = float(value)*0.5
    payment_min = float(value)*0.20
    
    loan_max = payment_max*24
    loan_min = payment_min*10


    response = {
        'loan_max': loan_max,
        'loan_min': loan_min,
        'payment_max': payment_max,
        'payment_min': payment_min
    }

    return response