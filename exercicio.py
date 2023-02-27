import requests

# Etapas cumpridas:
# 1. obter_dados

def obter_dados():
	# Efetuar requisição da API.
	response = requests.get('https://randomuser.me/api/')
	if response.status_code != 200:
		print('API retornou status', response.status_code)
		return None

	# Verificar se algum erro foi retornado.
	dados = response.json()
	if 'error' in dados:
		print('API retornou erro:', dados['error'])
		return None

	return dados

def main():
	# Obter dados da API.
	dados = obter_dados()
	if not dados:
		return

	print(dados)

if __name__ == '__main__':
	main()
