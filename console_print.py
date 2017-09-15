from currency import currency


def print_players_together(table1, table2, length):

    print("Player ID\tName\t\t\t\tSalary\t\t\t|\tPlayer ID\tName\t\t\t\tSalary")
    print("----------------------------------------------------------------------------------------------------------------------------------------------")
    for i in range(0,length):

        try:
            table1row = table1[i]
        except IndexError:
            table1row = (" ", " ", " ")
        try:
            table2row = table2[i]
        except IndexError:
            table2row = (" ", " ", " ")

        t1_p_len = len(table1row[1])
        t2_p_len = len(table2row[1])

        if t1_p_len >= 24:
            side1_print = str(table1row[0]) + "\t\t" + table1row[1] + "\t" + table1row[2]
        elif t1_p_len >= 16:
            side1_print = str(table1row[0]) + "\t\t" + table1row[1] + "\t\t" + table1row[2]
        elif t1_p_len == 7:
            side1_print = str(table1row[0]) + "\t\t" + table1row[1] + "\t\t\t\t" + table1row[2]
        elif t1_p_len > 1:
            side1_print = str(table1row[0]) + "\t\t" + table1row[1] + "\t\t\t" + table1row[2]
        else:
            side1_print = str(table1row[0]) + "\t\t\t" + table1row[1] + "\t\t\t" + table1row[2]

        if t2_p_len >= 24:
            side2_print = str(table2row[0]) + "\t\t" + table2row[1] + "\t" + table2row[2]
        elif t2_p_len >= 16:
            side2_print = str(table2row[0]) + "\t\t" + table2row[1] + "\t\t" + table2row[2]
        elif t2_p_len == 7:
            side2_print = str(table2row[0]) + "\t\t" + table2row[1] + "\t\t\t\t" + table2row[2]
        else:
            side2_print = str(table2row[0]) + "\t\t" + table2row[1] + "\t\t\t" + table2row[2]

        if len(str(table1row[2])) <= 4:
            print(side1_print + "\t\t\t|\t" + side2_print)
        else:
            print(side1_print + "\t\t|\t" + side2_print)


def print_exceptions_together(table1, table2, length):

    if table1 == [] and table2 == []:
        pass
    elif table1 != [] and table2 == []:
        print("Trade Exceptions\t\t\t\t\t\t\t|")
        print("Expires\t\tSalary\t\t\t\t\t\t\t|")

    elif table1 == [] and table2 != []:
        print("\t\t\t\t\t\t\t\t\t|\tTrade Exceptions")
        print("\t\t\t\t\t\t\t\t\t|\tExpires\t\tSalary")

    else:
        print("Trade Exceptions\t\t\t\t\t\t\t|\tTrade Exceptions\nExpires\t\tSalary\t\t\t\t\t\t\t|\tExpires\t\tSalary")

    for i in range(0,length):

        try:
            table1row = table1[i]
        except IndexError:
            table1row = (" ", " ")
        try:
            table2row = table2[i]
        except IndexError:
            table2row = (" ", " ")

        if table1row == (" ", " ") and table2row != (" ", " "):
            print("\t\t\t\t\t\t\t\t\t|\t" + str(table2row[0]) + "\t" + str(currency(table2row[1])))
        elif table1 == []:
            print("\t\t\t\t\t\t\t\t\t|\t" + str(table2row[0]) + "\t" + str(currency(table2row[1])))
        else:
            print(str(table1row[0]) + "\t" + str(currency(table1row[1])) + "\t\t\t\t\t\t|\t" + str(table2row[0]) + "\t" + str(currency(table2row[1])))


    if table1 != [] or table2 != []:
        print("----------------------------------------------------------------------------------------------------------------------------------------------")
