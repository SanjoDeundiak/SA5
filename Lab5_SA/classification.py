# coding=utf-8

import numpy as np
import random as rand
from scipy.interpolate import interp1d
from collections import namedtuple

Result_of_memb_func_search = namedtuple("Result_of_memb_func_search", "position memb_func")


class Position:
    from_the_left_side, first_odd_number_left_edge, first_odd_number_equal_range, first_odd_number_right_edge, \
    between_odd_numbers, second_odd_number_left_edge, second_odd_number_equal_range, second_odd_number_right_edge, \
    from_the_right_side = range(9)


def out_intervals(t_left, t_right):
    for i in range(4):
        print 's_' + str(i)
        for j in range(7):
            if t_left[i][j] < t_right[i][j]:
                print "[%0.2f; %0.2f]" % (t_left[i][j], t_right[i][j])
            else:
                print "empty set"


def out(S_classes):
    result = []
    for i in range(4):
        result.append('S' + str(i) + ': ' + S_classes[i])
    return result


def find_boundary_values(cut_level, t_range, range_size, memb_func):
    # returns boundary values on x-axis
    left_boundary = t_range[0]
    for i in range(range_size):
        # if membership func starts from level over cut_level the left_boundary stills equal to current_range[0]
        if left_boundary == t_range[0]:
            if i > 0 and memb_func[i] > memb_func[i - 1] and memb_func[i] == cut_level:
                left_boundary = t_range[i]
        if memb_func[i] == cut_level:
            right_boundary = t_range[i]
    # print [left_boundary, right_boundary]
    return [left_boundary, right_boundary]


def find_memb_func_by_arg(T0_border, arg_first, memb_func_first, arg_second, memb_func_second, left_equal_border,
                          right_equal_border):
    f1 = interp1d(arg_first, memb_func_first, kind='cubic')
    f2 = interp1d(arg_second, memb_func_second, kind='cubic')

    if T0_border <= arg_first[0]:
        memb_func_result = 0
        position = Position.from_the_left_side
    elif T0_border <= arg_first[len(arg_first) - 1]:
        memb_func_result = f1(T0_border)
        if T0_border <= left_equal_border[0]:
            position = Position.first_odd_number_left_edge
        elif T0_border <= left_equal_border[1]:
            position = Position.first_odd_number_equal_range
        else:
            position = Position.first_odd_number_right_edge
    elif T0_border < arg_second[0]:
        memb_func_result = 0
        position = Position.between_odd_numbers
    elif T0_border < arg_second[len(arg_second) - 1]:
        memb_func_result = f2(T0_border)
        if T0_border <= right_equal_border[0]:
            position = Position.second_odd_number_left_edge
        elif T0_border <= right_equal_border[1]:
            position = Position.second_odd_number_equal_range
        else:
            position = Position.second_odd_number_right_edge
    else:
        memb_func_result = 0
        position = Position.from_the_right_side
    return Result_of_memb_func_search(position, memb_func_result)


# --------------------START-----------------------------

def classify(t_s_left, t_s_right):
    print t_s_left
    print t_s_right
    t_left = range(20, 75, 5)
    t_right = range(1, 12)
    # membership functions
    memb_func_t_left = np.arange(1, -0.1, -0.1)
    memb_func_t_right = [0, 0.1, 0.3, 0.5, 0.7, 0.8, 1.0, 0.9, 0.7, 0.5, 0.3]

    '''
    t_s_left_j = np.ndarray(shape=(4, 7))
    t_s_right_j = np.ndarray(shape=(4, 7))
    for i in range(4):
        t_s_left_j[i] = [rand.random() * 20 for x in t_s_left_j[i]]
        t_s_right_j[i] = [rand.random() * 100 for x in t_s_left_j[i]]
    out_intervals(t_s_left_j, t_s_right_j)

    t_s_left=np.ndarray(4)
    t_s_right=np.ndarray(4)

    for i in range(4):
        t_s_left[i] = t_s_left_j[i].min()
        t_s_right[i] = t_s_right_j[i].max()
    #print "and now finally", t_s_left, t_s_right
    '''
    # defining of membership functions' values , upper which we consider t_ij=t
    left_equal_level = 0.9
    right_equal_level = 0.5

    mu_left = np.ndarray(4)
    mu_right = np.ndarray(4)
    # classification = array(4)
    classification = []

    left_equal_border = find_boundary_values(left_equal_level, t_left, len(t_left), memb_func_t_left)
    right_equal_border = find_boundary_values(right_equal_level, t_right, len(t_right), memb_func_t_right)
    for i in range(4):
        if t_s_left[i] > t_s_right[i]:
            # if t_s_left > t_s_right:
            classification.append(u"Классификация невозможна, так как допустимый временной интервал" \
                                  u" для данной ситуации - пустое множество")
        else:
            find_left_border_memb_func = find_memb_func_by_arg(t_s_left[i], t_left, memb_func_t_left, t_right,
                                                               memb_func_t_right, left_equal_border, right_equal_border)
            find_right_border_memb_func = find_memb_func_by_arg(t_s_right[i], t_left, memb_func_t_left, t_right,
                                                                memb_func_t_right, left_equal_border,
                                                                right_equal_border)
            print "lets look at classification positions of left and right boundaries\n", find_left_border_memb_func.position, \
                find_right_border_memb_func.position
            if find_left_border_memb_func.position != find_right_border_memb_func.position:
                classification.append(u"Классификация невозможна. Для классификации измените величину допуска")
            else:
                if find_right_border_memb_func.position <= 2:
                    classification.append(u"Класс особо опасных ситуаций")
                elif find_right_border_memb_func.position <= 7:
                    classification.append(u"Класс потенциально опасных ситуаций")
                else:
                    classification.append(u"Класс почти безопасных ситуаций")

    return out(classification)
