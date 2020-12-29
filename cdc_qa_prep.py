import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json

url = 'https://www.cdc.gov/coronavirus/2019-ncov/faq.html'
response = requests.get(url)
print(response)
# make sure we got a valid response
if(response.ok):
  # get the full data from the response
  data = response.text
  print(data)

soup = BeautifulSoup(data, 'lxml')
TAGS = ['span']

text_q = [element.get_text() for element in soup.find_all('span') if soup.find(id='accordion-15') and soup.find(role='heading')]
questions = ' '.join(text_q)

text_a = [element.get_text() for element in soup.find_all('p') if soup.find(id='accordion-15') and soup.find(id='accordion-15-card-1')]
answers = ' '.join(text_a)

for element in soup.find_all('div', class_='card-body'):
  print(element)

soup.find('div', id='accordion-15').find_all('span', role='heading')

questions = []
for i in range(14,27):
  q_s = soup.find('div', id=f'accordion-{i}').find_all('span', role='heading')
  for element in q_s:
    text_q = element.get_text()
    questions.append(text_q)

answers = []
for i in range(14,27):
  a_s = soup.find('div', id=f'accordion-{i}').select('div[class*=card-body]')
  for element in a_s:
    text_a = element.get_text()
    answers.append(text_a)

print(len(questions))
print(len(answers))

with open('answers.json', 'w') as f:
  json.dump(answers, f)
with open('questions.json', 'w') as f:
  json.dump(questions, f)

answers = pd.read_json('/content/drive/My Drive/Colab Datasets/COVID Chat Bot/answers.json')
questions = pd.read_json('/content/drive/My Drive/Colab Datasets/COVID Chat Bot/questions.json')
print(len(questions))
print(len(answers))

with open("test.json", 'w') as f:
  json.dump(q_and_a, f)

with open("test.json", 'r') as f:
  new_data = json.load(f)
with open('answers.json', 'w') as f:
  json.dump(answers, f)
with open('questions.json', 'w') as f:
  json.dump(questions, f)

q_and_a

df = pd.DataFrame(q_and_a)

df.to_csv('cdc_qa.csv', index=False)
