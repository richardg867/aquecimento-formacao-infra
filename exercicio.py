import pandas, requests

# Etapas cumpridas:
# 1. obter_dados
# 2. obter_converter_dados

def obter_dados(n):
	# Efetuar requisição da API.
	response = requests.get('https://randomuser.me/api/?results={0}'.format(n))
	if response.status_code != 200:
		print('API retornou status', response.status_code)
		return None

	# Verificar se algum erro foi retornado.
	dados = response.json()
	if 'error' in dados:
		print('API retornou erro:', dados['error'])
		return None

	return dados

def obter_converter_dados(n):
	# Obter dados da API.
	dados = obter_dados(n)
	if not dados or 'results' not in dados:
		return None

	# Normalizar dados para torná-los planos.
	normalizado = pandas.json_normalize(dados['results'])

	# Converter dados em DataFrame.
	frame = pandas.DataFrame(normalizado)

	# Salvar dados em CSV.
	frame.to_csv('dados.csv')

	return frame


def main():
	# Obter e converter dados da API para 1000 usuários.
	frame = obter_converter_dados(1000)
	if frame is None:
		return

	print(frame)

if __name__ == '__main__':
	main()
