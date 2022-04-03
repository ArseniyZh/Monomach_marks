import sys
from datetime import datetime
from abc import ABC, abstractmethod

import requests

from persistence.persistence import BookmarkDatabase

persistence = BookmarkDatabase()

# Базовый класс Command
class Command(ABC):
	@abstractmethod
	def execute(self, data):
		raise NotImplementedError('Команды должны реализовывать метод execute')

# Создание таблицу
class CreateBookmarksTableCommand(Command):
	def execute(self, data = None):
		db.create_table('bookmarks', {
			'id': 'integer primary key autoincrement',
			'title': 'text not null',
			'url': 'text not null',
			'notes': 'text',
			'date_added': 'text not null'
			})


# Добавление закладки
class AddBookmarkCommands(Command):
	def execute(self, data, timestamp = None):
		data['date_added'] = timestamp or datetime.utcnow().isoformat()
		persistence.create(data)
		return True, None


# Вывод закладок (по умолчанию сортировка по дате добавления)
class ListBookCommand(Command):
	def __init__(self, order_by = 'date_added'):
		self.order_by = order_by

	def execute(self, data = None):
		return True, persistence.list(order_by = self.order_by)

# Удаление закладки по ID
class DeleteBookmarkCommand(Command):
	def execute(self, data):
		persistence.delete(data)
		return True, None

# Изменение закладки по ID
class EditBookmarkCommand(Command):
	def execute(self, data):
		persistence.edit(data['id'], data['update'])
		return True, None

# Выйти из приложения
class QuitCommand(Command):
	def execute(self, data = None):
		print('Возвращайтесь ещё!')
		return sys.exit()


# Импорт звезд из GitHub
class ImportGitHubStarsCommand(Command):
	def _extract_bookmark_info(self, repo): # Извлечение всех необходимых данных для создания закладки
		return {
		'title' : repo['name'],
		'url' : repo['html_url'],
		'notes' : repo['description']
		}

	def execute(self, data):
		bookmarks_imported = 0

		github_username = data['github_username']
		next_page_of_results = f'https://api.github.com/users/{github_username}/starred'

		while next_page_of_results: # Пока существуют страницы результатов
			stars_response = requests.get( # Получаетя следующую страницу
				next_page_of_results,
				headers = {'Accept' : 'application/vnd.github.v3.star+json'}
				)
			next_page_of_results = stars_response.links.get('next', {}).get('url')

			for repo_info in stars_response.json():
				repo = repo_info['repo'] # Информация о помеченном звездой репозитории

				if data['preserve_timestamps']:
					timestamp = datetime.strptime(
						repo_info['starred_at'], # Метка времени создания звезды
						'%Y-%m-%dT%H:%M:%SZ'
						)
				else:
					timestamp = None

				bookmarks_imported += 1

				AddBookmarkCommands().execute(
					self._extract_bookmark_info(repo),
					timestamp = timestamp
					)
			return True, bookmarks_imported