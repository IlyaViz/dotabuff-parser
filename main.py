import os
from classes import GameParser
from exceptions import ServerException, OldGameException

if __name__ == "__main__":
    while True:
        id = input("Game id:")
        os.system("cls")
        if id.isdigit():
            try:
                parser = GameParser(id)
                parser.get_exercises()
            except ServerException:
                print("Id not found or you are banned on dotabuff server")
            except OldGameException:
                print("Cannot calculate for such an old or early game")
        else:
            print("Enter id!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")