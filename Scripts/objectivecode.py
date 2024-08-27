import random


def dice_roll(no_throws, no_of_dice, no_of_sides):
    tuple_list = []
    for throw in range(no_throws): # iterating through number of throws
        result_tuple = ()
        t_list = []
        for dice in range(no_of_dice): # iterating through number of dice
            t_list.append(random.randint(1, no_of_sides)) # rolling dice to given side
        result_tuple = result_tuple + tuple(t_list)
        tuple_list.append(result_tuple)
    print(tuple_list)


if __name__ == '__main__':
    no_throw = int(input('Enter Number of Throws = '))
    no_of_dic = int(input('Enter Number of Dices = '))
    no_of_side = int(input('Enter Number of Dice sides = '))
    dice_roll(no_throw, no_of_dic, no_of_side)
