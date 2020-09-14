import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import re


scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_client.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Aux_emergencial').sheet1

pp = pprint.PrettyPrinter()

dados = sheet.get_all_records()

busca = "ALVES DO NASCIMENTO"
cont = 0
for dic in dados:
        if busca in dic['NOME']:
            print(dic['N'], '-', dic['CPF'], '-', dic['NOME'], '-', dic['OBSERVACAO'])
            cont += 1
            if cont >= 100:
                break

'''result = sheet.row_values(30000)
print(result)
#pp.pprint(result)

print(sheet.row_count, "registros encontradoa ")
busca = sheet.findall("02001541414")
print(busca)

nome = re.compile('DIOGO')
busca2 = sheet.findall(nome).cell.row
pp.pprint(busca2)'''
#for valor in busca2:


