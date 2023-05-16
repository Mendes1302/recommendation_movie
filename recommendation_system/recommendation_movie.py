import pandas as pd
from ast import literal_eval
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from os.path import abspath
from sys import path as pth
from pandas import DataFrame


path = abspath(__file__)
path = path[:path.find('/recommendation_system')]
pth.insert(1, path) 
from api_resquest.themoviedb import Movies as ms

from warnings import filterwarnings
filterwarnings("ignore")


class Recommend():
    """
        Classe que faz recomendacao de filmes
        --------
        Method:
            private: __add_movie
            private: __set_database
            private: __model_recommendation
            private: __get_name_genres
            public:  movies

    """

    def __init__(self) -> None:
        """
            Construtor da classe '__init__': com a variavel movies_df (Dataframe)
            --------
            Returns:
                None: None
        """
        self.movies_df = pd.read_csv(path+'/data_source/metadata_movies_oficial.csv')


    def __add_movie(sefl, data, results, title) -> DataFrame:
        """
        Adicionar dados no DataFrame
        --------

        Args:
            data (Dataframe): Dataframe da base interna de filmes
            results (dict): Novo registro (filme)
            title (str): Titulo do filme

        Returns:
            data: Dataframe com valor agregado
        """
        if len(data[data.id_movie == results['id']]) > 0:
            return data
        year = datetime.strptime(results['release_date'], '%Y-%m-%d').strftime('%Y')
        dict_results = {'title': title, 'year_publication': year, 'budget': results['budget'], 'revenue' : results['revenue'],
                            'runtime' : results['runtime'], 'genre_ids': [results['genre_ids']], 
                            'original_language' : results['original_language'], 
                            'popularity' : results['popularity'], 'id_movie': results['id'],
                            'vote_average' : results['vote_average'], 'vote_count' : results['vote_count']} 
        data = pd.concat([data, pd.DataFrame(dict_results)])
        data.index = range(data.shape[0])
        return data


    def __set_database(self, title) -> DataFrame|int:
        """
        Prepara dataframe para ser usado
        --------

        Args:
            title (str): Titulo do filme

        Returns:
            movies_df: Dataframe atualizado

            results['id']: Id do filme
        """
        movies_df = self.movies_df

        types_cols = {'budget': 'int32', 'year_publication': 'int32', 'popularity':'float64'}
        movies_df = movies_df.astype(types_cols)

        movies_df = movies_df.drop(['Unnamed: 0'], axis=1)

        movies_df = movies_df[movies_df.genre_ids != '[]']
        movies_df = movies_df[movies_df.budget > 0]
        movies_df.index = range(movies_df.shape[0])

        results = ms().search_movie_by_name(title_name=title, filter_values='all')
        print('--->> FILME ESCOLHIDO:\n')
        ms()._print_movies(results=[results])
        movies_df = self.__add_movie(movies_df, results, title)

        for i in range(movies_df.shape[0]):
            genre_ids = movies_df.genre_ids[i]
            if type(genre_ids) == str:
                genre_ids = literal_eval(movies_df.genre_ids[i])
            genre_ids.sort()

            txt_id = ''.join(str(i) for i in genre_ids)
            movies_df.at[i, 'concat_genre_ids'] = int(txt_id)


        return movies_df, results['id']


    def __model_recommendation(self, movies_df) -> MinMaxScaler|KMeans|list:
        """

        Prepara modelo para ser usado
        --------

        Args:
            movies_df (Dataframe): Dataframe dos filmes

        Returns:
            scaler: Valor scaler

            kmeans: Valor kmeans

            labels: Lista com labels
        """
        features = ["concat_genre_ids", "revenue", "budget"]
        X = movies_df[features]
        scaler = MinMaxScaler()
        X_normalized = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=7)
        kmeans.fit(X_normalized)

        labels = kmeans.predict(X_normalized)
        score = silhouette_score(X_normalized, labels)
        print("-----> Silhouette Score:", score)

        return scaler, kmeans, labels


    def __get_name_genres(self, movie_show) -> DataFrame:
        """
        Converte id genres para valor tipo string
        --------

        Args:
            movie_show (DataFrame): Valor para converter

        Returns:
            DataFrame: Valor convertido
        """

        genres = {28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 10769: "Foreign", 
                80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family", 
                14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music", 
                9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
                10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"}
        movie_show.index = range(movie_show.shape[0])
        for i in range(movie_show.shape[0]):
            genre_ids = movie_show.genre_ids[i]
            if type(genre_ids) == str:
                genre_ids = literal_eval(genre_ids)
            genre_ids.sort()
            movie_show.at[i, 'genre_ids'] = [genres[int(id)] for id in genre_ids]
        return movie_show


    def movies(self, title, n=5) -> None:
        """
        Metodo principal de recomendação
        --------

        Args:
            title (_type_): _description_
            n (int, optional): Quantidade de recomendação que será mostrada. Defaults to 5.
        """
        self.movies_df, movie_id = self.__set_database(title=title)
        scaler, kmeans, labels = self.__model_recommendation(self.movies_df)

        features_col = ["concat_genre_ids", "revenue", "budget"]
        movie = self.movies_df[self.movies_df["id_movie"] == movie_id][features_col].values
        movie_normalized = scaler.transform(movie)
        cluster = kmeans.predict(movie_normalized)[0]

        cluster_movies = self.movies_df[labels == cluster][["title"] +["id_movie"]+ features_col]

        similarities = []
        for i, row in cluster_movies.iterrows():
            features = row[2:].values.reshape(1, -1)
            var_similarity = cosine_similarity(movie_normalized, features)
            similarities.append((row["id_movie"], var_similarity))

        similarities = sorted(similarities, key=lambda x: x[1], reverse=False)
        top_movies = [movie[0] for movie in similarities[:n]]
        is_present = self.movies_df['id_movie'].isin(top_movies)
        df_recommendation = self.movies_df[is_present]
        df_recommendation = self.__get_name_genres(movie_show=df_recommendation)

        drop_cols = ['budget', 'revenue', 'concat_genre_ids', 'vote_count', 'popularity', 'vote_average']
        df_recommendation = df_recommendation.drop(drop_cols, axis=1)

        ms()._print_movies_recommend(results=df_recommendation)