
import argparse

import numpy as np
from scipy.optimize import rosen


def downhill_simplex(simplex, function, max_iterations, tol, alpha, beta, gamma):
    assert(alpha > 0)
    assert(0 < beta < 1)
    assert(gamma > 1)

    v = np.apply_along_axis(function, axis=1, arr=simplex)
    iterations = 0
    for it in range(max_iterations):
        iterations = it
        if stop_criteria(v, tol):
            break

        h = np.argmax(v)
        l = np.argmin(v)
        centroid = np.mean(
            [p for i, p in enumerate(simplex) if i != h], axis=0
        )
        x_prime = reflection(alpha, centroid, simplex[h])
        y_prime = function(x_prime)

        v_noh = np.array([p for i, p in enumerate(v) if i != h])
        is_y_prime_best = (
            (y_prime > v_noh).sum() == v_noh.size
        ).astype(np.int)

        if y_prime < v[l]:
            x_second = expansion(gamma, centroid, x_prime)
            y_second = function(x_second)
            if y_second < v[l]:
                simplex[h] = x_second
                v[h] = y_second
            else:
                simplex[h] = x_prime
                v[h] = y_prime
        elif is_y_prime_best:
            if y_prime <= v[h]:
                simplex[h] = x_prime
                v[h] = y_prime
            x_second = contraction(beta, centroid, simplex[h])
            y_second = function(x_second)
            if y_second > v[h]:
                x_min = simplex[l]
                simplex = np.apply_along_axis(
                    lambda x: (x + x_min) / 2, axis=1, arr=simplex
                )
                v = np.apply_along_axis(function, axis=1, arr=simplex)
            else:
                simplex[h] = x_second
                v[h] = y_second
        else:
            simplex[h] = x_prime
            v[h] = y_prime

    return simplex[np.argmin(v)], iterations


def reflection(alpha, centroid, point):
    return (1 + alpha) * centroid - alpha * point


def expansion(gamma, centroid, point):
    return (1 + gamma) * point - gamma * centroid


def contraction(beta, centroid, point):
    return beta * point + (1 - beta) * centroid


def stop_criteria(v, tol):
    mu = np.mean(v)
    n = len(v)
    return np.sqrt(
        np.sum(
            np.apply_along_axis(lambda x: x ** 2, axis=0, arr=(v - mu))
        ) / n
    ) <= tol


def simplex_coordinates(x_zero):
    '''
    Generate a simplex starting from the given initial point.
    Implementation based upon Matlab's fminsearch routine.
    '''
    x = [np.array(x_zero)]
    n = len(x_zero)
    b = np.eye(n)
    for i in range(n):
        h = (
            0.05 if x_zero[i] != 0
            else 0.00025
        )
        x.append(x_zero + h * b[i])
    return np.array(x)


class ListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = [float(x.strip())
                  for x in values.replace('[', '').replace(']', '').split(',')]
        setattr(namespace, self.dest, values)


def parse_args():
    '''
    Parse standard input arguments
    '''
    parser = argparse.ArgumentParser(
        description='Nelder-Mead downhill simplex algorithm'
    )
    parser.add_argument(
        dest='initial_point',
        action=ListAction,
        help='initial point used to compute the simplex'
    ),
    parser.add_argument(
        '--max_iterations',
        action='store',
        default=1000,
        type=int,
        help='maximum number of iterations'
    ),
    parser.add_argument(
        '--tol',
        action='store',
        default=1e-5,
        type=float,
        help='tolerance for the stopping criteria'
    ),
    parser.add_argument(
        '--alpha',
        action='store',
        default=1,
        type=float,
        help='coefficient for reflection'
    ),
    parser.add_argument(
        '--beta',
        action='store',
        default=0.5,
        type=float,
        help='coefficient for contraction'
    ),
    parser.add_argument(
        '--gamma',
        action='store',
        default=2,
        type=float,
        help='coefficient for expansion'
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    simplex = simplex_coordinates(args.initial_point)
    print(simplex)
    result, iterations = downhill_simplex(
        simplex, rosen, args.max_iterations, args.tol, args.alpha, args.beta, args.gamma
    )
    print(result)
    print(iterations)


if __name__ == "__main__":
    main()