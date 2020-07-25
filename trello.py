import requests
from datetime import date
import re
from decouple import config

"""
AUTOMAT ZGŁOSZEŃ BŁĘDÓW
Gdy będzie błąd w jakimś serwisie, ma przesłać do Trello
"""
API_key = config("API_key")
API_token = config("API_token")
login = config("login")

class Trello_Job:
    def __init__(self, job_name, description, table_name="Automat", list_name="Inbox", checklist_name="Zadania", todo_names=["Wykonać"]):
        self.job_name = job_name
        self.description = description
        self.table_name = table_name
        self.list_name = list_name
        self.checklist_name = checklist_name
        self.todo_names = todo_names
        self.get_table_id()
        self.get_list_id()
        self.add_card()
        self.get_id_checklist()
        self.add_todo()

    def get_table_id(self):
        url = f"https://api.trello.com/1/members/{login}/boards"
        querystring = {"filter":"all","fields":"all","lists":"none","memberships":"none","organization":"false","organization_fields":"name,displayName","key":API_key,"token":API_token}
        response = requests.request("GET", url, params=querystring)
        response = response.json()
        for resp in response:
            if resp['name'] == self.table_name:
                self.id_tablicy = resp['id']
                break

    def get_list_id(self):
        url = f'https://api.trello.com/1/boards/{self.id_tablicy}/lists'
        querystring = {"cards":"none","card_fields":"all","filter":"open","fields":"all","key":API_key,"token":API_token}
        response = requests.request("GET", url, params=querystring).json()
        for resp in response:
            if resp['name'] == self.list_name:
                self.list_id = resp['id']
                break

    def add_card(self):

        url = "https://api.trello.com/1/cards"
        querystring = {"name":self.job_name, "desc":self.description,"idList":self.list_id,"keepFromSource":"all","key":API_key,"token":API_token}
        response = requests.request("POST", url, params=querystring).json()
        self.id_card = response['id']

    def get_id_checklist(self):

        url = f"https://api.trello.com/1/cards/{self.id_card}/checklists"
        querystring = {"name":self.checklist_name,"key":API_key,"token":API_token}
        response = requests.request("POST", url, params=querystring).json()
        self.id_checklist = response['id']

    def add_todo(self):

        url = f"https://api.trello.com/1/checklists/{self.id_checklist}/checkItems"
        for todo_name in self.todo_names:
            querystring = {"name": todo_name,"pos":"bottom","checked":"false","key":API_key,"token":API_token}
            response = requests.request("POST", url, params=querystring)
    
    def get_date_now(self):
        self.date_now = date.today()
        print(self.date_now)

    def get_id_for_delete(self):
        self.get_date_now()
        url = f"https://api.trello.com/1/lists/{self.list_id}/cards"
        querystring = {"key":API_key,"token":API_token}
        response = requests.request("GET", url, params=querystring).json()
        self.id_karty_del = []
        for resp in response:
            data = (rf'.*{self.date_now}*')
            dataapi = resp['dateLastActivity']
            if re.match(data, dataapi):
                self.id_karty_del.append(resp['id'])

    def delete(self):
        for id_karty in self.id_karty_del:
            url = f"https://api.trello.com/1/cards/{id_karty}"
            response = requests.request("DELETE", url, params={"key":API_key,"token":API_token})

if __name__ == "__main__":
    t = Trello_Job("Testowe zadanie", "Opis zadania", list_name="test")
    #t.get_id_for_delete()
    #t.delete()

