import os
from classes import GameParser
from exceptions import ServerException

if __name__ == "__main__":
    while True:
        id = input("Game id:")
        os.system("cls")
        if id.isdigit():
            try:
                parser = GameParser(id)
                parser.get_exercises()
            except ServerException:
                print("Try another id")
        else:
            print("Enter id!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")