from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.base_user import AbstractBaseUser

class User(AbstractBaseUser):
    USERNAME_FIELD  = 'username'

    username        = models.CharField(max_length=10, unique=True)
    key             = models.CharField(max_length=20)
    is_active       = models.BooleanField(default=True)
    creation_date   = models.DateTimeField(auto_now_add=True)
    password        = None
    class Meta:
        db_table = 'user_project'
    

class Person(models.Model):
    name            = models.CharField(max_length=50, null=True)
    nickname        = models.CharField(max_length=50, null=True)
    cpf             = models.CharField(max_length=20, validators=[MinLengthValidator(11)])
    number_rg       = models.CharField(max_length=20, null=True)
    phone           = models.CharField(max_length=20, null=True)
    date_of_birth   = models.DateField(null=True)
    finance         = models.DecimalField(max_digits=10, decimal_places=2)
    informal_worker = models.CharField(max_length=20)
    receives_payment = models.CharField(max_length=200, null=True)
    card_companies  = models.CharField(max_length=200, null=True)
    token_myid      = models.CharField(max_length=100, null=True)
    token_company   = models.CharField(max_length=100, null=True)
    bank_used       = models.CharField(max_length=50, null=True)
    loan_reason     = models.TextField(null=True)
    date_register   = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'persons'


class ContactPerson(models.Model):
    person  = models.ForeignKey(Person, related_name='persons', on_delete=models.CASCADE)
    contact = models.ForeignKey(Person, related_name='contacts', on_delete=models.CASCADE)
    class Meta:
        db_table = 'contacts_persons'


class CreditAnalysis(models.Model):
    person          = models.ForeignKey(Person, on_delete=models.CASCADE)
    score_serasa    = models.CharField(max_length=20)
    analysis_bank   = models.CharField(max_length=20)
    analysis_machine = models.CharField(max_length=20)
    analysis_group  = models.CharField(max_length=20)
    finance_group   = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    class Meta:
        db_table = 'credits_analysis'