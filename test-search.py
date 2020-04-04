import requests
from bs4 import BeautifulSoup

output = requests.get("http://localhost:8050/render.html?url=https%3A%2F%2Fduckduckgo.com%2F%3Fq%3Darctic%20policy%20national%26kl%3Dwt-wt%26ks%3Dl%26k1%3D-1%26kp%3D-2%26ka%3Da%26kaq%3D-1%26k18%3D-1%26kax%3D-1%26kaj%3Du%26kac%3D-1%26kn%3D1%26kt%3Da%26kao%3D-1%26kap%3D-1%26kak%3D-1%26kk%3D-1%26ko%3Ds%26kv%3D-1%26kav%3D1%26t%3Dhk%26ia%3Dnews&wait=5").content

soup = BeautifulSoup(output, 'html.parser')
results = soup.findAll("a", {"class": "result__a"})
result_size = len(results)

print ("Size: "+ str(result_size))

for element in results:
    new_url = element['href']
    # TODO: Filter URLs if required
    print(new_url)
