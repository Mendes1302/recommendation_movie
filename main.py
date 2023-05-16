from api_resquest.themoviedb import Movies as ms
from recommendation_system.recommendation_movie import Recommend as rd
from os import system

original, red = '\033[0;0m', '\033[31m'
green, blue = '\033[32m', '\033[34m'
yellow = '\033[33m'


def __user_interaction() -> None:
    """
    Script que faz interação com o usuário. E continua até sair do while
    --------
    Returns:
        None: None
    """
    while True:
        print(blue, '\b1 - Pesquisar detalhes do Filme;')
        print('2 - Pesquisar filmes em Trending;')
        print('3 - Recomendar filme a partir de outro;')
        print('4 - Limpar tela')
        print('5 - Sair\n', original)
        try:
            chosen = int(input(yellow+'Escolha uma opção: '+original))
            if chosen == 5: break
            elif chosen == 1:
                print()
                title_name = str(input(yellow+'Nome do filme: '+original))
                results = ms().search_movie_by_name(title_name=title_name, filter_values='all')
                ms()._print_movies([results])
                print('\n\n')
            elif chosen == 2: 
                print()
                ms().get_trending()
                print('\n\n')
            elif chosen == 3:
                print()
                title_name = str(input(yellow+'Nome do filme: '+original))
                print('RECOMENDAÇÃO VIA KMEANS (LOCAL):\n')
                rd().movies(title=title_name)
                print('RECOMENDAÇÃO VIA THE MOVIE DATABASE\n')
                ms().get_recommendation(title_name=title_name)
                print('\n\n')
            elif chosen == 4:
                system('clear')
            else: print(red, '\n\nERROR: Tente novamente!!\n\n', original)
        except Exception as error:
            print(red, '\n\nERROR: Tente novamente!!\n\n')
            print(f'ERROR: {error} \n\n', original)


def main() -> None:
    """
    Script que faz interação com o usuário.
    ----
    Tem 5 opções de interação
    Opções:
        1: Pesquisar detalhes do Filme;
        2: Pesquisar filmes em Trending;
        3: Recomendar filme a partir de outro;
        4: Limpar tela
        5: Sair
    OBS: 
        ``O nome do filme TEM que ser em inglês!!``
    """
    print(green, '_='*20, 'Busca e recomendação de Filmes','_='*20, original)
    print(yellow, '\n\b----> Digite o nome do Filme em INGLES!')
    print('\b----> Escolha o que deseja fazer:\n', original)
    try:
        __user_interaction()
    except Exception as error:
        print(red, '\n\nERROR: Tente novamente!!\n\n')
        print(f'ERROR: {error}', original)

    print(green, '_='*20, 'FIM','_='*20, original)
    

if __name__ == "__main__":
    main()