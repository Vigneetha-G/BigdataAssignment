import requests
import json
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog
from db_config import get_redis_connection

class DataProcessor:
    """A class for processing data from an API."""

    def __init__(self, api_url):
        """
        Initialize the DataProcessor.

        Parameters:
        api_url (str): The URL of the API.
        """
        self.api_url = api_url

    def retrieve_data(self):
        """
        Retrieve data from the API.

        Returns:
        list: The retrieved data.
        """
        print("Retrieving data from the API:", self.api_url)
        response = requests.get(self.api_url)
        if response.status_code == 200:
            print("Data retrieval successful")
            data = response.json()
            return data[:60]  
        else:
            print("Failed to retrieve data from the API")
            raise Exception("Failed to retrieve data from the API")

    def store_data_in_redis(self, data):
        """
        Store data in Redis.

        Parameters:
        data (list): The data to store.
        """
        redis_connection = get_redis_connection()
        for index, item in enumerate(data):
            redis_connection.json().set(f'record_{index}', '.', json.dumps(item))
        print("Data stored successfully")

    def analyze_data(self, data):
        """
        Analyze data and count keywords.
        Parameters:
        data (list): The data to analyze.
        Returns:
        dict: Keyword counts.
        """
        keyword_counts = {}
        for item in data:
            for keyword in item.get('keywords', []):
                if keyword in keyword_counts:
                    keyword_counts[keyword] += 1
                else:
                    keyword_counts[keyword] = 1
        return keyword_counts

    def search_data(self, data, search_query):
        """
        Search data for a query.
        Parameters:
        data (list): The data to search.
        search_query (str): The query to search for.
        Returns:
        list: Search results.
        """
        search_results = []
        for item in data:
            for key, value in item.items():
                if search_query in str(value):
                    search_results.append(item)
                    break
        return search_results

    def plot_keyword_counts(self, keyword_counts):
        """
        Plot keyword counts.

        Parameters:
        keyword_counts (dict): The keyword counts to plot.
        """
        plt.bar(keyword_counts.keys(), keyword_counts.values())
        plt.xlabel('Keyword')
        plt.ylabel('Count')
        plt.title('Keyword Distribution')
        plt.xticks(rotation=60, ha='right')
        plt.tight_layout()
        plt.show()

    def get_user_search_query(self):
        """
        Get user search query from GUI.
        Returns:
        str: The search query.
        """
        root = tk.Tk()
        root.withdraw()
        search_query = simpledialog.askstring("Search", "Enter a keyword:")
        return search_query

if __name__ == "__main__":
    data_processor = DataProcessor(api_url="https://api.opensource.org/licenses/osi-approved")
    data = data_processor.retrieve_data()

    data_processor.store_data_in_redis(data)

    keyword_counts = data_processor.analyze_data(data)
    print("Keyword counts:", keyword_counts)

    data_processor.plot_keyword_counts(keyword_counts)

    search_query = data_processor.get_user_search_query()

    search_results = data_processor.search_data(data, search_query)
    print(f"Search results for '{search_query}':")
    for result in search_results:
        print(result)
