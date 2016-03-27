# coding: utf-8
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as pol
import numpy as np
from scipy.optimize import brentq

max_arg = 160.
s_number = 4
f_number = 7

a = np.array([[.6, .5, .4, .55, .0, .755, .45],
              [.0, .0, .7, .35, .0, .0, .7],
              [.65, .0, .8, .65, .7, .65, .7],
              [.0, .0, .4, .55, .45, .85, .0]])

iP = np.array([[.65, .55, .8, .45, .0, .7, .75],
               [.0, .0, .5, .8, .0, .0, .45],
               [.45, .0, .6, .5, .6, .45, .45],
               [.0, .0, .7, .7, .4, .35, .0]])

iD = np.array([[.3, .54, .5, .4, .0, .5, .4],
               [.0, .0, .65, .25, .0, .0, .5],
               [.35, .0, .35, .4, .2, .45, .3],
               [.0, .0, .65, .5, .65, .3, .0]])

iT = np.array([[.7, .8, .4, .6, .0, .85, .5],
               [.0, .0, .5, .4, .0, .0, .4],
               [.25, .0, .76, .45, .3, .5, .6],
               [.0, .0, .5, .5, .6, .3, .0]])


def const_variant(alpha, betta, gamma):
    for i in range(s_number):
        for j in range(f_number):
            if a[i][j] != 0.0:
                alpha[i][j] = (1 + np.exp(iP[i][j]) * iT[i][j]) / (100 * (1 + a[i][j] ** 2))
                betta[i][j] = (1 + 0.0001 * np.exp(iT[i][j])) * iD[i][j] / ((1 + a[i][j]) ** 2)
                gamma[i][j] = (1 + np.exp(iD[i][j])) * a[i][j] / (10 * (1 + a[i][j] ** 2))


alpha = np.zeros((s_number, f_number))
betta = np.zeros((s_number, f_number))
gamma = np.zeros((s_number, f_number))
const_variant(alpha, betta, gamma)


def const_own(alpha, betta, gamma):
    for i in range(s_number):
        for j in range(f_number):
            if a[i][j] != 0.0:
                alpha[i][j] = (np.exp((-iP[i][j] + iT[i][j])) * a[i][j] ** 2) / (1 + iD[i][j] * a[i][j])
                betta[i][j] = iD[i][j] * (iP[i][j] + np.log(1 + a[i][j])) / (1 + np.exp(15 * iP[i][j]))
                gamma[i][j] = iT[i][j] * np.exp(2 * a[i][j]) / (25 * (1 + iD[i][j] ** 0.05))

alpha_own = np.zeros((s_number, f_number))
betta_own = np.zeros((s_number, f_number))
gamma_own = np.zeros((s_number, f_number))
const_own(alpha_own, betta_own, gamma_own)


def i_d(i, j, t):
    res = 0.5 * iD[i][j] * (1 + (alpha[i][j] + gamma[i][j]) * t)
    return min(res, 1)


def i_p(i, j, t):
    res = 0.5 * iP[i][j] * ((1 + (alpha[i][j] + gamma[i][j]) * t) ** 2)
    return min(res, 1)


def i_t(i, j, t):
    res = iT[i][j] * (1 - betta[i][j] * (t ** 6) / 10. ** 12)
    return max(res, 0)


def i_d_own(i, j, t):
    res = 0.025 * iD[i][j] * np.exp(0.5 * alpha_own[i][j]) * (t + 0.2) ** 2
    return min(res, 1)


def i_p_own(i, j, t):
    res = 0.8 ** (-t) * gamma_own[i][j] / alpha_own[i][j] - 0.8 * gamma_own[i][j] / alpha_own[i][j]
    return min(res, 1)


def i_t_own(i, j, t):
    if iT[i][j] == 0:
        addend = 0
    else:
        addend = 1
    res = addend - 0.03 * alpha_own[i][j] * iT[i][j] * (5 * t + gamma_own[i][j])
    return max(res, 0)


def inf_plot(i, j):
    plt.figure(figsize=(15, 3))
    x = np.linspace(0.0, max_arg, 1000)
    plt.gcf().subplots_adjust(bottom=0.175)

    plt.subplot(1, 3, 1)
    y = map(lambda x: i_p(i, j, x), x)
    if y[-1] == 1.:
        tick = x[y.index(1.)]
        plt.plot([0], [0], 'w')
        plt.legend(['t* = ' + "%.2f" % tick], loc=4)
    plt.plot(x, y)
    plt.xlabel('$t$')
    plt.ylabel(u'$I_П(t)$')
    plt.axis([0.0, max_arg, 0.0, 1.2])

    plt.subplot(1, 3, 2)
    plt.title('$S=$' + str(i + 1) + u', $Ф=$' + str(j + 1))
    y = map(lambda x: i_d(i, j, x), x)
    if y[-1] == 1.:
        tick = x[y.index(1.)]
        plt.plot([0], [0], 'w')
        plt.legend(['t* = ' + "%.2f" % tick], loc=4)
    plt.plot(x, y)
    plt.xlabel('$t$')
    plt.ylabel(u'$I_Д(t)$')
    plt.axis([0.0, max_arg, 0.0, 1.2])

    plt.subplot(1, 3, 3)
    y = map(lambda x: i_t(i, j, x), x)
    if y[-1] == 0.:
        tick = x[y.index(0.)]
        plt.plot([0], [0], 'w')
        plt.legend(['t* = ' + "%.2f" % tick], loc=1)
    plt.plot(x, y)
    plt.xlabel('$t$')
    plt.ylabel(u'$I_T(t)$')
    plt.axis([0.0, max_arg, 0.0, 1.2])

    plt.show()
    # plt.savefig('plots/plot_' + str(i) + '_' + str(j))


def inf_plot_own(i, j):
    plt.figure(figsize=(15, 3))
    x = np.linspace(0.0, max_arg, 1000)
    plt.gcf().subplots_adjust(bottom=0.175)

    plt.subplot(1, 3, 1)
    y = map(lambda x: i_p_own(i, j, x), x)
    if y[-1] == 1.:
        tick = x[y.index(1.)]
        plt.plot([0], [0], 'w')
        plt.legend(['t* = ' + "%.2f" % tick], loc=4)
    plt.plot(x, y)
    plt.xlabel('$t$')
    plt.ylabel(u'$I_П(t)$')
    plt.axis([0.0, max_arg, 0.0, 1.2])

    plt.subplot(1, 3, 2)
    plt.title('$S=$' + str(i + 1) + u', $Ф=$' + str(j + 1))
    y = map(lambda x: i_d_own(i, j, x), x)
    if y[-1] == 1.:
        tick = x[y.index(1.)]
        plt.plot([0], [0], 'w')
        plt.legend(['t* = ' + "%.2f" % tick], loc=4)
    plt.plot(x, y)
    plt.xlabel('$t$')
    plt.ylabel(u'$I_Д(t)$')
    plt.axis([0.0, max_arg, 0.0, 1.2])

    plt.subplot(1, 3, 3)
    y = map(lambda x: i_t_own(i, j, x), x)
    if y[-1] == 0.:
        tick = x[y.index(0.)]
        plt.plot([0], [0], 'w')
        plt.legend(['t* = ' + "%.2f" % tick], loc=1)
    plt.plot(x, y)
    plt.xlabel('$t$')
    plt.ylabel(u'$I_T(t)$')
    plt.axis([0.0, max_arg, 0.0, 1.2])

    plt.show()
    # plt.savefig('plots/plot_own_' + str(i) + '_' + str(j))


situation = [0]
factor = [0]
magic = [0.0]


def eta(x):
    return 1 - np.log2(1 + a[situation[0]][factor[0]] * i_p(situation[0], factor[0], x) *
                       i_d(situation[0], factor[0], x) * i_t(situation[0], factor[0], x)) - magic[0]


def solve(eta_min, eta_max, i, j):
    res = []
    x_min = 0.0
    x_max = max_arg
    situation[0] = i
    factor[0] = j

    magic[0] = eta_min
    x_middle = 0.0
    temp = eta(x_min)
    s_min = True
    while (temp * eta(x_middle) > 0.0) and (x_middle < x_max):
        x_middle += 1
    if x_middle >= x_max:
        s_min = False
    else:
        d1 = brentq(eta, x_min, x_middle)
        d2 = brentq(eta, x_middle, x_max)

    magic[0] = eta_max
    x_middle = 0.0
    temp = eta(x_min)
    s_max = True
    while (temp * eta(x_middle) > 0.0) and (x_middle < x_max):
        x_middle += 1
    if x_middle >= x_max:
        s_max = False
    else:
        u1 = brentq(eta, x_min, x_middle)
        u2 = brentq(eta, x_middle, x_max)
    if s_max:
        if s_min:
            res = [[u1, d1], [d2, u2]]
        else:
            res = [[u1, u2]]
    return res


def eta_own(x):
    return 1 - np.log2(1 + a[situation[0]][factor[0]] * i_p_own(situation[0], factor[0], x) *
                       i_d_own(situation[0], factor[0], x) * i_t_own(situation[0], factor[0], x)) - magic[0]


def solve_own(eta_min, eta_max, i, j):
    res = []
    x_min = 0.0
    x_max = 200.
    situation[0] = i
    factor[0] = j

    magic[0] = eta_min
    x_middle = 0.0
    temp = eta_own(x_min)
    s_min = True
    while (temp * eta_own(x_middle) > 0.0) and (x_middle < x_max):
        x_middle += 1
    if x_middle >= x_max:
        s_min = False
    else:
        d1 = brentq(eta_own, x_min, x_middle)
        d2 = brentq(eta_own, x_middle, x_max)

    magic[0] = eta_max
    x_middle = 0.0
    temp = eta_own(x_min)
    s_max = True
    while (temp * eta_own(x_middle) > 0.0) and (x_middle < x_max):
        x_middle += 1
    if x_middle >= x_max:
        s_max = False
    else:
        u1 = brentq(eta_own, x_min, x_middle)
        u2 = brentq(eta_own, x_middle, x_max)
    if (s_max):
        if (s_min):
            res = [[u1, d1], [d2, u2]]
        else:
            res = [[u1, u2]]
    return res


def getT(i, eta_max):
    res = [0.0, max_arg]
    s = True
    for j in range(f_number):
        if a[i][j] != 0.0:
            temp = solve(0.1, eta_max, i, j)
            if len(temp) == 0:
                s = False
            else:
                res[0] = max(res[0], temp[0][0])
                res[1] = min(res[1], temp[0][1])
    if res[0] >= res[1]:
        s = False
    if not s:
        res = []
    return res


def getT_own(i, eta_max):
    res = [0.0, max_arg]
    s = True
    for j in range(f_number):
        if a[i][j] != 0.0:
            temp = solve_own(0.1, eta_max, i, j)
            if len(temp) == 0:
                s = False
            else:
                res[0] = max(res[0], temp[0][0])
                res[1] = min(res[1], temp[0][1])
    if res[0] >= res[1]:
        s = False
    if not s:
        res = []
    return res


def eta_i_j(i, j, x):
    return 1 - np.log2(1 + a[i][j] * i_p(i, j, x) * i_d(i, j, x) * i_t(i, j, x))


def eta_plot(i):
    plt.figure(figsize=(5, 3))
    x = np.linspace(0.0, max_arg, 1000)
    l = []
    for j in range(f_number):
        if (a[i][j] != 0.0):
            plt.plot(x, map(lambda x: eta_i_j(i, j, x), x))
            l.append(j + 1)
    plt.title('$S=$' + str(i + 1))
    plt.legend([u'$Ф=$' + str(ll) for ll in l], loc=4)
    plt.xlabel('$t$')
    plt.ylabel(u'$eta$')
    plt.axis([0.0, max_arg, 0.5, 1.1])
    plt.yticks(np.linspace(0.0, 1.2, 13))
    plt.grid(axis='y')
    plt.show()


def eta_own_i_j(i, j, x):
    return 1 - np.log2(1 + a[i][j] * i_p_own(i, j, x) * i_d_own(i, j, x) * i_t_own(i, j, x))


def eta_own_plot(i, j):
    plt.figure(figsize=(5, 3))
    x = np.linspace(0.0, max_arg, 1000)
    l = []
    for j in range(f_number):
        if (a[i][j] != 0.0):
            plt.plot(x, map(lambda x: eta_own_i_j(i, j, x), x))
            l.append(j + 1)
    plt.title('$S=$' + str(i + 1))
    plt.legend([u'$Ф=$' + str(ll) for ll in l], loc=4)
    plt.xlabel('$t$')
    plt.ylabel(u'$eta-own$')
    plt.axis([0.0, max_arg, 0.5, 1.1])
    plt.yticks(np.linspace(0.0, 1.2, 13))
    plt.grid(axis='y')
    plt.show()


def out_plots(print_plots):
    # print_plots==[print_variant_inf_plot, print own_inf_plot]
    if print_plots[0]:
        const_variant(alpha, betta, gamma)
        for i in range(s_number):
            for j in range(f_number):
                if (a[i][j] != 0.0):
                    inf_plot(i, j)
    if print_plots[1]:
        const_own(alpha, betta, gamma)
        for i in range(s_number):
            for j in range(f_number):
                if (a[i][j] != 0.0):
                    inf_plot_own(i, j)


# print_plots = [0, 0]
# out_plots(print_plots)


def out_eta_plot(print_eta):
    if print_eta[1]:
        const_own(alpha, betta, gamma)
        for i in range(s_number):
            eta_own_plot(i, j)
    if print_eta[0]:
        const_variant(alpha, betta, gamma)
        for i in range(s_number):
            eta_plot(i)


# out_eta_plot([0, 0])
#
# eta_min = 0.1
# eta_max = np.arange(0.5, 1, 0.1)
# #for k in range(eta_max.size):
# t_s=np.ndarray(shape=(4,2))
# for i in range(s_number):
#     t_s[i] = getT(i, 0.9)
# t_s_transposed = t_s.transpose()
#
# clsf.classify(t_s_transposed[0],t_s_transposed[1])