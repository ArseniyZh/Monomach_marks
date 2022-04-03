import os
from commands import commands
from collections import OrderedDict

# Опции для визуального слоя
class Option:
	def __init__(self, name, command, prep_call = None, succes_message = '{result}'):
		self.name = name # Имя, показываемое в меню
		self.command = command # Выполняемая команда
		self.prep_call = prep_call # Необязательный шаг, вызываемый перед выполнением команды
		self.success_message = succes_message # Сохраняте сконфигурированное сообщение об успешности

	# Этот метод вызывается, когда в меню будет выбрана команда
	def choose(self):
		data = self.prep_call() if self.prep_call else None # Вызывает подготовительный шаг, если имеется
		success, result = self.command.execute(data) # Получает статус и результат из команды

		formatted_result = ''

		# Форматирует результат для показа, если это необходимо
		if isinstance(result, list):
			for bookmark in result:
				formatted_result += '\n' + format_bookmark(bookmark)
		else:
			formatted_result = result

		# Выводит сообщение об успешности, вставляя отформатированный результат, если это необходимо
		if success:
			print(self.success_message.format(result = formatted_result))

	# Представляет вариант действия в форме имени
	# вместо дефолтного поведения Python
	def __str__(self):
		return self.name


def format_bookmark(bookmark):
	return '\t'.join(
		str(field) if field else ''
		for field in bookmark
		)


# Вывод опций в консоль
def print_options(options):
	for shortcut, option in options.items():
		print(f'({shortcut}) {option}')
	print()


# Проверка допустимости вводимых данных пользователем
def option_choice_is_valid(choice, options):
	return choice in options or choice.upper() in options # True \ False


# Получает от пользователя вариант действия
def get_option_choice(options):
	choice = input('Выберите вариант действия: ')
	while not option_choice_is_valid(choice, options): # Пока пользователь не введет допустимый вариант
		print('Недопустимый вариант')
		choice = input('Выберите вариант действия: ')
	return options[choice.upper()]


# Общая функция, предлагающая пользователю ввести данные
def get_user_input(label, required = True):
	value = input(f'{label}: ') or None # Первоначальный ввод
	while required and not value:
		value = input(f'{label}: ') or None
	return value


# Получает данные для добавления закладки
def get_new_bookmark_data():
	return {
		'title': get_user_input('Заголовок'),
		'url' : get_user_input('Ссылка'),
		'notes' : get_user_input('Примечание')
	}

# Удаляет запись по ID
def get_bookmark_id_for_deletion():
	return get_user_input('Введите ID закладки для удаления')


# Обновляет запись по ID
def get_bookmark_data_for_edit():
	bookmark_id = get_user_input('Ведите ID закладки для изменения')
	field = get_user_input('Выберите значение для изменения (title, URL, notes)')
	new_value = get_user_input(f'Введите новое значение для {field}')
	return {
	    'id': bookmark_id,
	    'update': {field: new_value},
	}


# Очистка экрана
def clear_screen():
	clear = 'cls' if os.name == 'nt' else 'clear'
	os.system(clear)


# Импортирует помеченные репозитории в виде закладки
def get_github_import_options():
	return {
	'github_username' : get_user_input('Пользовательское имя GitHub'),
	'preserve_timestamps' : get_user_input('Сохранить метки времени? [Y/n]', required = False) in {'Y', 'y', None}
	}


def loop():
	clear_screen()

	options = OrderedDict({
	    'A' : Option(
	    	'Добавить закладку',
	    	commands.AddBookmarkCommands(),
	    	prep_call = get_new_bookmark_data,
	    	succes_message = 'Закладка добавлена!'
	    	),
	    'B' : Option(
	    	'Показать список закладок по дате',
	    	commands.ListBookCommand()
	    	),
	    'T' : Option(
	    	'Показать список закладок по заголовку',
	    	commands.ListBookCommand(order_by = 'title')
	    	),
	    'I' : Option(
	    	'Показать список закладок по ID',
	    	commands.ListBookCommand(order_by = 'id')
	    	),
	    'D' : Option(
	    	'Удалить закладку',
	    	commands.DeleteBookmarkCommand(),
	    	prep_call = get_bookmark_id_for_deletion,
	    	succes_message = 'Закладка удалена!'
	    	),
	    'E' : Option(
	    	'Изменить закладку',
	    	commands.EditBookmarkCommand(),
	    	prep_call = get_bookmark_data_for_edit,
	    	succes_message = 'Закладка изменена!'
	    	),
	    'G' : Option(
	    	'Импортировать звезды GitHub',
	    	commands.ImportGitHubStarsCommand(),
	    	prep_call = get_github_import_options,
	    	succes_message = 'Импортировано {result} закладок из помеченных звёздами репозиториев!'
	    	),
	    'Q' : Option('Выйти', commands.QuitCommand())
	})
	print_options(options)

	chosen_option = get_option_choice(options)
	clear_screen()
	chosen_option.choose()

	_ = input('Нажмите ENTER, чтобы вернуться в меню\n')




if __name__ == '__main__':
    while True:
    	loop()