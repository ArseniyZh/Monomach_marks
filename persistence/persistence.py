from abc import ABC, abstractmethod

from database.database import DatabaseManager

# Слой, позволяющий, общаться с разными БД (локальными, облачными, API) 

class PersistenceLayer(ABC):
	@abstractmethod
	def create(self, data): 
		raise NotImplementedError('Слои постоянства данных должны реализовать метод create')

	@abstractmethod
	def list(self, order_by=None):
		raise NotImplementedError('Слои постоянства данных должны реализовать метод list')

	@abstractmethod
	def edit(self, bookmark_id, bookmark_data):
		raise NotImplementedError('Слои постоянства данных должны реализовать метод edit')

	@abstractmethod
	def delete(self, bookmark_id):
		raise NotImplementedError('Слои постоянства данных должны реализовать метод delete')


# Специфичная для слоя постоянства реализация, которая использует БД
class BookmarkDatabase(PersistenceLayer):
	def __init__(self):
		self.table_name = 'bookmarks'
		self.db = DatabaseManager('bookmarks.db') #Обрабатывает создание БД с помощью класса DatabaseManager

		self.db.create_table(self.table_name, {
			'id': 'integer primary key autoincrement',
			'title': 'text not null',
			'url': 'text not null',
			'notes': 'text',
			'date_added': 'text not null',
			})

	# Специфичная для БД реализация для каждой формы поведения интерфейса
	def create(self, bookmark_data):
		self.db.add(self.table_name, bookmark_data)

	def list(self, order_by=None):
		return self.db.select(self.table_name, order_by=order_by).fetchall()

	def edit(self, bookmark_id, bookmark_data):
		self.db.update(self.table_name, {'id': bookmark_id}, bookmark_data)

	def delete(self, bookmark_id):
		self.db.delete(self.table_name, {'id': bookmark_id})