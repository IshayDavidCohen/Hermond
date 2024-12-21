from typing import Optional, List, Dict, Union
from bson import ObjectId
from datetime import datetime
from pymongo.cursor import CursorType
from app.Database import Database


# CategoryModule is unique due to id's having direct correlation to category name.


class CategoryModule:
    def __init__(self, db: Database):
        self.db = db
        self.collection = 'categories'

    # Basic CRUD Operation
    def create_category(self, category_data: Dict) -> str:

        # Push new document
        result = self.db.insert_one(self.collection, category_data)
        return str(result.inserted_id)

    def get_category(self, category_id: str = None, query: Dict = None) -> Optional[Dict]:
        """
        Function is abel to get a category in two ways,
        1) By Category Name(ID)
        2) By a category's subfield/key value (IMPORTANT! - returns the first document with that value)
        :param category_id:
        :param query:
        :return:
        """
        if category_id:
            query_by = {'_id': category_id}
        elif query:
            query_by = query
        else:
            return None

        return self.db.find_one(self.collection, query_by)

    def get_categories_by(self, query: Dict) -> Optional[Union[Dict, CursorType]]:
        """
        Function returns all categories that fill the query's requirements.
        Ex. All the categories that have 'userA', 'userB', ...,

        :param query: Dict
        :return: Can return multiple (Type: CursorType from pymongo) or singular (Type: Dict)
        """
        return self.db.find_all(collection=self.collection, query=query)

    def get_all_categories(self):
        return self.db.find_all(self.collection)

    def update_category(self, category_id: str, update_data: Dict) -> int:
        """
        Function removes ID and updates the category.
        Once it updates it returns the modified_count

        modified_count = 1 -> Success
        modified_count = 0 -> Fail

        :param category_id: str
        :param update_data: Dict
        :return: int
        """
        update_data = update_data.copy()

        # ID Exists, remove it
        if update_data.get('_id'):
            del update_data['_id']

        return self.db.update_one(self.collection, {'_id': category_id}, update_data).modified_count

    def delete_category(self, category_id: str) -> int:
        """
        Deletes document based on category name (ID) and returns confirmation.

        deleted_count = 1 -> Success
        deleted_count = 0 -> Fail

        :param category_id: str
        :return: int
        """
        return self.db.delete_one(self.collection, {'_id': category_id}).deleted_count

    # Complex Operations - subfields
    def get_subfield(self, category_id: str, subfields: List, with_id: bool = False) -> Dict:
        subfield_query = {k: 1 for k in subfields}
        subfield_query['_id'] = with_id

        document = self.db.find_one(collection=self.collection, query={'_id': category_id},
                                    subfield_query=subfield_query)

        if len(document.keys()) == 1 and with_id:
            return {}

        return document

    def get_users(self, category) -> Optional[List]:
        category_doc = self.get_category(category.capitalize())
        if category_doc:
            users = category_doc.get('users')
            if users:
                return users
        print(f"[{category}] has no known users!")
        return None

    def add_user(self, category: str, username: str, user_id: str) -> int:
        try:
            # Using atomic operations to avoid mutex problems and overwrite.
            result = self.db.update_one(
                self.collection,
                {'_id': category.capitalize(), f'users.{username}': {'$exists': False}},
                {f'users.{username}': ObjectId(user_id)}  # Use $push if duplicates are allowed
            )
            return result.modified_count > 0
        except Exception as e:
            # Handle exceptions (e.g., log the error)
            return False
