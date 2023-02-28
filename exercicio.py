import getopt, matplotlib.pyplot, os, pandas, re, requests, sys

# Etapas cumpridas:
# 1. obter_dados
# 2. obter_converter_dados
# 3. converter_telefone
# 4. gerar_relatorio_grafico
# 5. agrupar
# 6. particionar_dados
# 7. main

def obter_dados(n):
	print('Obtendo dados...')

	# Efetuar requisição da API.
	response = requests.get(f'https://randomuser.me/api/?results={n}')
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

	print('Convertendo dados...')

	# Normalizar dados para torná-los planos.
	normalizado = pandas.json_normalize(dados['results'])

	# Converter dados em DataFrame.
	frame = pandas.DataFrame(normalizado)

	# Salvar dados em CSV.
	frame.to_csv('dados.csv')

	return frame

def converter_telefone(frame_in):
	print('Convertendo telefones...')

	# Copiar DataFrame de entrada.
	frame_out = frame_in.copy()

	# Transformar números de telefone e celular.
	for nome_series in ('phone', 'cell'):
		# Transformar série e substituir a existente.
		# A função lambda retira caracteres adicionais do número e deixa somente os dígitos.
		frame_out[nome_series] = frame_out[nome_series].transform(lambda tel: re.sub(r'''[^0-9]''', '', tel))

	return frame_out

def gerar_relatorio_grafico(frame, report, idades):
	if report:
		print('Criando relatório...')

		# Iniciar relatório em texto.
		f = open('relatorio.txt', 'w')

		# Adicionar parâmetros definidos ao relatório.
		for series in report:
			f.write('{0}:\n'.format(series))
			for value, count in frame[series].value_counts().items():
				f.write('- {0}: {1:.01f}%\n'.format(value, (count / len(frame[series])) * 100))
			f.write('\n')

		# Finalizar relatório.
		f.close()

	if idades:
		print('Criando gráfico...')

		# Gerar gráfico de distribuição de idades.
		matplotlib.pyplot.title('Distribuição de Idades')
		matplotlib.pyplot.hist(frame['dob.age'], bins=idades)

		# Salvar gráfico em arquivo.
		matplotlib.pyplot.savefig('idades.png')

def agrupar(frame, series):
	print('Agrupando dados...')

	# Ordenar DataFrame pelos parâmetros definidos.
	frame = frame.sort_values(series)

	# Salvar novos dados em CSV.
	frame.to_csv('dados.csv')

	return frame

def particionar_dados(frame, series):
	print('Particionando dados...')

	# Efetuar particionamento por séries.
	for group in frame.groupby(series).groups:
		# Converter valor para tuple de 1 elemento se somente uma série for particionada.
		if type(group) != tuple:
			group = (group,)

		# Criar DataFrame particionado série por série, montando o caminho da pasta.
		frame_part = frame
		caminho = 'partitions'
		for i in range(len(group)):
			# Filtrar DataFrame por valor desta série.
			frame_part = frame_part[frame_part[series[i]] == group[i]]

			# Adicionar partição ao caminho.
			caminho = os.path.join(caminho, f'{series[i]}={group[i]}')

		# Criar pasta para este conjunto de partições caso necessário.
		if not os.path.isdir(caminho):
			os.makedirs(caminho)

		# Salvar arquivo particionado.
		caminho = os.path.join(caminho, 'data.csv')
		frame_part.to_csv(caminho)

def main():
	# Definir valores padrão para os parâmetros.
	age = 0
	group = ['location.country', 'location.state']
	number = 1000
	partition = ['location.country', 'location.state']
	phone_number = False
	report = ['gender', 'location.country']

	# Interpretar parâmetros.
	parametros, resto = getopt.getopt(sys.argv[1:], 'a:g:hn:p:r:t', ['age', 'group', 'help', 'number', 'partition', 'report', 'phone-number'])
	for parametro, valor in parametros:
		if parametro in ('-a', '--age'):
			age = int(valor)
		elif parametro in ('-g', '--group'):
			group = valor.split(',')
		elif parametro in ('-h', '--help'):
			# Mostrar ajuda.

			print(f'''
Uso: exercicio.py [-a grupos] [-g] [-h] [-n numero] [-p series] [-r series] [-t]

-a / --age           Gerar gráfico de distribuição de idades por quantidade grupos
-g / --group         Colunas para agrupamento (padrão: {','.join(group)})
-h / --help          Este texto de ajuda
-n / --number        Quantidade de usuários a obter (padrão: {number})
-p / --partition     Colunas para particionamento (padrão: {','.join(partition)})
-r / --report        Gerar relatórios (padrão: {','.join(report)})
-t / --phone-number  Converter números de telefone e celular para padrão único
''')

			# Sair sem executar nenhuma tarefa.
			return
		elif parametro in ('-n', '--number'):
			number = int(valor)
		elif parametro in ('-p', '--partition'):
			partition = valor.split(',')
		elif parametro in ('-r', '--report'):
			report = valor.split(',')
		elif parametro in ('-t', '--phone-number'):
			phone_number = True

	# Obter e converter dados da API para 1000 usuários.
	frame = obter_converter_dados(number)
	if frame is None:
		return

	# Converter números de telefone e celular.
	if phone_number:
		frame = converter_telefone(frame)

	# Gerar relatório e gráfico.
	if report or age:
		gerar_relatorio_grafico(frame, report, age)

	# Agrupar por país e estado.
	if group:
		frame = agrupar(frame, group)

	# Particionar dados.
	if partition:
		particionar_dados(frame, partition)

	print('Concluído. DataFrame final:')
	print(frame)

if __name__ == '__main__':
	main()
