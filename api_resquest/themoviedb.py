from json import loads
from requests import get


class Movies():
    """
        Classe que faz requests no site: The Movie Database
        --------
        Method:
            public: search_movie_by_name
            public: get_trending
            public: get_recommendation
            protected: _print_movies

    """
    global original, red
    original, red = '\033[0;0m', '\033[31m'


    def __init__(self) -> None:
        """
            Construtor da classe '__init__': com as variaveis header e genres
            --------
            Returns:
                None: None
        """
        auth = "YOUR_AUTH"
        self.headers = {"accept": "application/json",
                       "Authorization": auth}
        
        self.genres = {28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 
                       80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family", 
                       14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music", 
                       9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
                       10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"}
                            

    def __request(self, url) -> dict:
        """ 
        Metodo e uso interno para obter request
        --------

        Args:
            url (str): Url para fazer request

        Returns:
            dict: Resultado do request
        """
        response = get(url, headers=self.headers)
        if response.status_code != 200:
            print(self.red, "Falha, filme não encontrado!!", self.original)
            return False
        return loads(response.text)


    def _print_movies(self, results) -> None:
        """
        Mostrar os filmes gerados da request
        --------

        Args:
            results (dict): Filmes obtido
        Returns:
            None: None
        Example:
            >>> ms()._print_movies(results=results)
        """
        control = 0
        for indx in range(len(results)):
            if 'title' not in results[indx].keys(): continue
            print('title: '.upper(), results[indx]['title'])
            print('Overview: '.upper(), results[indx]['overview'])
            print('Language: '.upper(), results[indx]['original_language'])
            list_genres = [self.genres[id] for id in results[indx]['genre_ids']]
            print('Genres: '.upper(), list_genres)
            print('Release date: '.upper(), results[indx]['release_date'])
            print('\n\n')
            control += 1
            if control == 4:
                break
    

    def _print_movies_recommend(self, results) -> None:
        """
        Mostrar os filmes gerados da recomendação
        --------

        Args:
            results (dict): Filmes obtido
        Returns:
            None: None
        Example:
            >>> ms()._print_movies_recommend(results=results)
        """
        control = 0
        for indx in range(results.shape[0]):
            print('Title: '.upper(), results['title'][indx])
            print('Id Movie: '.upper(), results['id_movie'][indx])
            print('Language: '.upper(), results['original_language'][indx])
            print('Genres: '.upper(), results['genre_ids'][indx])
            print('Release date: '.upper(), results['year_publication'][indx])
            print('\n\n')
            control += 1
            if control == 4:
                break
         

    def search_movie_by_name(self, title_name, filter_values='null') -> dict:
        
        """
        Busca filme pelo nome
        --------

        Args:
            title_name (str): Nome do filme
            filter_values (str, optional): Filter de dados, outros valores ['id'/'all']. 
                                           Defaults to 'null'.

        Returns:
            dict: resultados da busca
        
        Example:
            >>> ms().get_recommendation(title_name='Interstellar')
            >>> ms().get_recommendation(title_name='Interstellar', filter_values='id')
            >>> ms().get_recommendation(title_name='Interstellar', filter_values='all')
        """
        url = f"https://api.themoviedb.org/3/search/movie?query={title_name}&include_adult=false&language=en-US&page=1"
        results = self.__request(url)
        results = results['results'][0]
        if not results: return False
        elif filter_values.lower() == 'id':
            return results['id']
        genre_ids = results['genre_ids']


        url = f"https://api.themoviedb.org/3/movie/{str(results['id'])}?language=en-US"
        results = self.__request(url)
        if not results: return False

        dict_results = {'budget' : results['budget'], 'revenue' : results['revenue'],
                        'runtime' : results['runtime'], 'genre_ids': genre_ids, 
                        'original_language' : results['original_language'], 
                        'popularity' : results['popularity'], 'id_movie': results['id'],
                        'vote_average' : results['vote_average'], 'vote_count' : results['vote_count']} 
        if filter_values.lower() == 'all':
            results['genre_ids'] = genre_ids
            return results
        
        return dict_results


    def get_trending(self) -> None:
        """
        Mostra filmes em trending no dia
        --------

        Returns:
            None: None
        Example:
            >>> ms().get_trending()
        """

        url = "https://api.themoviedb.org/3/trending/all/day"
        results = self.__request(url)
        if not results: return False
        results = results['results']
        self._print_movies(results=results)


    def get_recommendation(self, title_name) -> None:
        """
        Mostra recomendação de filmes usando outro como parâmetro 
        --------

        Args:
            title_name (str): Nome do filme

        Returns:
            None: None
        Example:
            >>> ms().get_recommendation(title_name='Interstellar')
        """
        movie_id = self.search_movie_by_name(title_name=title_name, filter_values='id')
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations?language=en-US&page=1'
        results = self.__request(url)
        if not results:
            return False
        results = results['results']
        self._print_movies(results=results)
