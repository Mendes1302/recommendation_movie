from pandas import DataFrame
from os.path import abspath
from sys import path as pth
from html import unescape
from requests import get
from time import sleep


path = abspath(__file__)
path = path[:path.find('/crawler')]
pth.insert(1, path) 
from api_resquest.themoviedb import Movies as ms


def __get_movies_of_html(html) -> list:
    """
    Extrair o que precisa do HTML (nomes e ano)
    --------

    Args:
        html (str): HTML da pagina que fez web scraping

    Returns:
        list: Nome e ano dos Filmes
    
    Example:
        >>> list_movies = __get_movies_of_html(html=html)
    """
    # parse general
    indx_1 = html.find('stacks_out_1772')
    indx_2 = html.find('stacks_out_1218915')
    html = html[indx_1:indx_2]
    indx_3 = html.find("</span><span style=\"font-size:16px; \">")
    len_txt_to_remove = len('"</span><span style=\"font-size:16px; \">"')
    html = html[indx_3+len_txt_to_remove:]
    txt_to_remove = "</span><br /></div></div></div></div><div id='"
    html = html.replace(txt_to_remove, '')
    return html.split('<br />')


def __etl_in_list_movie(movies) -> list:
    """
    Extrair ano e nome do filme
    --------

    Args:
        movies (list): Uma lista com strings

    Returns:
        list: Duas lista, um com nome (list_titles) e outra ano do filme (list_years)
    
    Example:
        >>> list_titles, list_years = __etl_in_list_movie(movies=movies)
    """
    list_titles = []
    list_years = []
    for movie in movies:
        if len(movie) == 0: continue
        # parse of movie title
        indx_1 = movie.find(') ') + len(') ')
        movie = movie[indx_1:]
        indx_2 = movie.rfind('(')
        title = movie[:indx_2].lower().strip()
        title = unescape(title)
        list_titles.append(title)

        # parse of year publication
        indx_3 = movie.find(' (')+len(' (')
        movie = movie[indx_3:]
        indx_4 = movie.rfind(', ')+len(', ')
        indx_5 = movie.rfind(')')
        year_publication = movie[indx_4:indx_5].strip()
        if '-' in year_publication:
            indx_6 = year_publication.find('-')
            year_publication = year_publication[:indx_6].strip()
        list_years.append(int(year_publication))
    return list_titles, list_years


def __create_cols_empty(df) -> DataFrame:
    """
    Criar novas colunas com valores vazios

    Args:
        df (DataFrame): _description_

    Returns:
        df: DataFrame com valores criado
    
    Example:
        >>> df = __create_cols_empty(df=dataframe)
    """
    new_cols = ['budget', 'revenue', 'runtime', 'genre_ids', 'original_language', 'popularity', 'id_movie', 'vote_average', 'vote_count']
    list_empty = [' ' for _ in range(df.shape[0])]
    for col in new_cols:
        df[col] = list_empty
    return df


def __new_values_in_df(df, indx_df, dict_new) -> DataFrame:
    """
    Adiciona os valores no DataFrame
    --------

    Args:
        df (DataFrame): Dataframe valores antigo
        indx_df (int): Index para edição
        dict_new (dict): Valores para ser adicionado

    Returns:
        df: Dataframe atualizado

    Example:
        >>> __new_values_in_df(df=dataframe, indx_df=1, dict_new={'budget': 1, 'revenue':5, '...': '...'})
    """
    for key, value in dict_new.items():
        df.at[indx_df, key] = value
        print('\t', key, value)
    return df


def __set_details(df) -> list and str:
    """
    Agrega dados aos filmes e apaga caso não encontre fazendo a busca dos filmes.
    --------

    Args:
        df (DataFrame): Dados dos top 1000 filmes

    Returns:
        list and str: DataFrame com os detalhes e lista de filmes não encontrado
    Example:
        >>> __set_details(df=dataframe) 
    """
    list_rm = []
    for i in range(df.shape[0]):
        title = df.title[i]
        print(i, title)

        results_search = ms().search_movie_by_name(title_name=title)
        if not results_search:
            list_rm.append(i)
            continue
        
        df = __new_values_in_df(df=df, indx_df=i, dict_new=results_search)
        print('\n')
        sleep(5)
    return df, list_rm


def main() -> None:
    """
    Script para buscar os 1000 top filmes e associar ao The Movie Database.
    --------

    Cria um dataframe com algumas colunas importante.

    Colunas: 
        budget (float): Orçamento

        revenue (float): Receita

        runtime (int): Tempo de duração

        genre_ids (list): Ids dos generos 

        original_language (str): Idioma original

        popularity (float): Popularidade do filme
        
        id_movie (int): Id usado no TMDB

        vote_average (float): Media da nota 

        vote_count (float): Quantidade de votos
    Returns:
        None: None
    """
    url = 'https://www.theyshootpictures.com/gf1000_all1000films.htm'
    html = get(url).text

    movies = __get_movies_of_html(html=html)
    list_titles, list_years = __etl_in_list_movie(movies=movies)
    df = DataFrame({'title': list_titles, 'year_publication': list_years})

    df = __create_cols_empty(df=df)
    df, list_rm = __set_details(df=df)
    
    if len(list_rm) > 0:
        df = df.drop(list_rm)

    df.to_csv(path+'/data_source/database_raw.csv')


if __name__ == "__main__":
    main()