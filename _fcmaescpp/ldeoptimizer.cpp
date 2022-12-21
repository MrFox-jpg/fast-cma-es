// Copyright (c) Dietmar Wolz.
//
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory.

// Eigen based implementation of differential evolution using on the DE/best/1 strategy.
// Uses two deviations from the standard DE algorithm:
// a) temporal locality introduced in 
// https://www.researchgate.net/publication/309179699_Differential_evolution_for_protein_folding_optimization_based_on_a_three-dimensional_AB_off-lattice_model
// b) reinitialization of individuals based on their age.
// To be used to further optimize a given solution. Initial population is created using a normal distribition
// with mean=init and sdev=sigma (normalized over the bounds, defined separately for each variable).
//
// Requires Eigen version >= 3.4 because new slicing capabilities are used, see
// https://eigen.tuxfamily.org/dox-devel/group__TutorialSlicingIndexing.html
// requires https://github.com/bab2min/EigenRand for random number generation.

#include <Eigen/Core>
#include <iostream>
#include <float.h>
#include <stdint.h>
#include <ctime>
#include <random>
#include <EigenRand/EigenRand>

using namespace std;

typedef Eigen::Matrix<double, Eigen::Dynamic, 1> vec;
typedef Eigen::Matrix<int, Eigen::Dynamic, 1> ivec;
typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic> mat;

typedef bool (*callback_type)(int, const double*, double*);

namespace l_differential_evolution {

static uniform_real_distribution<> distr_01 = std::uniform_real_distribution<>(
        0, 1);
static normal_distribution<> gauss_01 = std::normal_distribution<>(0, 1);

static vec zeros(int n) {
    return Eigen::MatrixXd::Zero(n, 1);
}

static vec constant(int n, double val) {
    return vec::Constant(n, val);
}

static Eigen::MatrixXd uniform(int dx, int dy, Eigen::Rand::P8_mt19937_64 &rs) {
    return Eigen::Rand::uniformReal<mat>(dx, dy, rs);
}

static Eigen::MatrixXd uniformVec(int dim, Eigen::Rand::P8_mt19937_64 &rs) {
    return Eigen::Rand::uniformReal<vec>(dim, 1, rs);
}

static double normreal(double mean, double sdev, Eigen::Rand::P8_mt19937_64 &rs) {
    return gauss_01(rs) * sdev + mean;
}

static vec normalVec(const vec &mean, const vec &sdev, int dim, Eigen::Rand::P8_mt19937_64 &rs) {
    vec nv = Eigen::Rand::normal<vec>(dim, 1, rs);
    return (nv.array() * sdev.array()).matrix() + mean;
}

// wrapper around the fitness function, scales according to boundaries

class Fitness {

public:

    Fitness(callback_type func_, int dim_, const vec &lower_limit,
            const vec &upper_limit, const vec &guess_, const vec &sigma_,
            Eigen::Rand::P8_mt19937_64 *rs_) {
        func = func_;
        dim = dim_;
        lower = lower_limit;
        upper = upper_limit;
        // initial guess for the arguments of the fitness function
        guess = guess_;
        xmean = vec(guess);
        rs = rs_;
        evaluationCounter = 0;
        if (lower.size() > 0) // bounds defined
            scale = (upper - lower);
        else
            scale = constant(dim, 1.0);
        invScale = scale.cwiseInverse();
        maxSigma = 0.25 * scale;
        // individual sigma values - initial search volume. inputSigma determines
        // the initial coordinate wise standard deviations for the search.
        if (sigma_.size() == 1)
            sigma0 =
                    0.5
                    * (scale.array()
                            * (vec::Constant(dim, sigma_[0])).array()).matrix();
        else
            sigma0 = 0.5 * (scale.array() * sigma_.array()).matrix();
        sigma = vec(sigma0);
    }

    void updateSigma(const vec &X) {
        vec delta = (xmean - X).cwiseAbs() * 0.5;
        sigma = delta.cwiseMin(maxSigma);
        xmean = X;
    }

    vec normX() {
        return distr_01(*rs) < 0.5 ?
                getClosestFeasible(normalVec(xmean, sigma0, dim, *rs)) :
                getClosestFeasible(normalVec(xmean, sigma, dim, *rs));
    }

    double normXi(int i) {
        double nx;
        if (distr_01(*rs) < 0.5) {
            do {
                nx = normreal(xmean[i], sigma0[i], *rs);
            } while (!feasible(i, nx));
        } else {
            do {
                nx = normreal(xmean[i], sigma[i], *rs);
            } while (!feasible(i, nx));
        }
        return nx;
    }

    bool feasible(int i, double x) {
        return lower.size() == 0 || (x >= lower[i] && x <= upper[i]);
    }

    vec sample() {
        if (lower.size() > 0) {
            vec rv = uniformVec(dim, *rs);
            return (rv.array() * scale.array()).matrix() + lower;
        } else
            return normX();
    }

    double sample_i(int i) {
        if (lower.size() > 0)
            return lower[i] + scale[i] * distr_01(*rs);
        else
            return normXi(i);
    }

    vec getClosestFeasible(const vec &X) const {
        if (lower.size() > 0) {
            return X.cwiseMin(upper).cwiseMax(lower);
        }
        return X;
    }

    double eval(const vec &X) {
        int nobj = 1;
        double res[nobj];
        func(dim, X.data(), res);
        for (int i = 0; i < nobj; i++) {
            if (std::isnan(res[i]) || !std::isfinite(res[i]))
                res[i] = 1E99;
        }
        evaluationCounter++;
        return res[0];
    }

    int getEvaluations() {
        return evaluationCounter;
    }

    vec guess;

private:
    callback_type func;
    int dim;
    vec lower;
    vec upper;
    vec xmean;
    vec sigma0;
    vec sigma;
    vec maxSigma;
    Eigen::Rand::P8_mt19937_64 *rs;
    long evaluationCounter;
    vec scale;
    vec invScale;
};

class LDeOptimizer {

public:

    LDeOptimizer(long runid_, Fitness *fitfun_, int dim_, Eigen::Rand::P8_mt19937_64 *rs_,
            int popsize_, int maxEvaluations_, double keep_,
            double stopfitness_, double F_, double CR_,
            double min_mutate_, double max_mutate_, bool *isInt_) {
        // runid used to identify a specific run
        runid = runid_;
        // fitness function to minimize
        fitfun = fitfun_;
        // Number of objective variables/problem dimension
        dim = dim_;
        // Population size
        popsize = popsize_ > 0 ? popsize_ : 15 * dim;
        // maximal number of evaluations allowed.
        maxEvaluations = maxEvaluations_ > 0 ? maxEvaluations_ : 50000;
        // keep best young after each iteration.
        keep = keep_ > 0 ? keep_ : 30;
        // Limit for fitness value.
        stopfitness = stopfitness_;
        F0 = F_ > 0 ? F_ : 0.5;
        CR0 = CR_ > 0 ? CR_ : 0.9;
        // Number of iterations already performed.
        iterations = 0;
        bestY = DBL_MAX;
        // stop criteria
        stop = 0;
        rs = rs_;
        isInt = isInt_;
        // DE population update parameter used in connection with isInt. Determines
        // the mutation rate for discrete parameters.
        min_mutate = min_mutate_ > 0 ? min_mutate_ : 0.1;
        max_mutate = max_mutate_ > 0 ? max_mutate_ : 0.5;
        init();
    }

    ~LDeOptimizer() {
        delete rs;
    }

    double rnd01() {
        return distr_01(*rs);
    }

    double rnd02() {
        double rnd = distr_01(*rs);
        return rnd * rnd;
    }

    int rndInt(int max) {
        return (int) (max * distr_01(*rs));
    }

    vec next_improve(const vec &xb, const vec &x, const vec &xi) {
        vec nextx = fitfun->getClosestFeasible(xb + ((x - xi) * 0.5));
        modify(nextx);
        return nextx;
    }

    void modify(vec &x) {
        if (isInt == NULL)
            return;
        double n_ints = 0;
        for (int i = 0; i < dim; i++)
            if (isInt[i]) n_ints++;
        double to_mutate = min_mutate + rnd01()*(max_mutate - min_mutate);
        for (int i = 0; i < dim; i++) {
            if (isInt[i]) {
                if (rnd01() < to_mutate/n_ints)
                    x[i] = (int)fitfun->normXi(i); // resample
            }
        }
    }

    void doOptimize() {

        // -------------------- Generation Loop --------------------------------
        for (iterations = 1; fitfun->getEvaluations() < maxEvaluations;
                iterations++) {

            double CR = iterations % 2 == 0 ? 0.5 * CR0 : CR0;
            double F = iterations % 2 == 0 ? 0.5 * F0 : F0;

            for (int p = 0; p < popsize; p++) {
                vec xp = popX.col(p);
                vec xb = popX.col(bestI);

                int r1, r2;
                do {
                    r1 = rndInt(popsize);
                } while (r1 == p || r1 == bestI);
                do {
                    r2 = rndInt(popsize);
                } while (r2 == p || r2 == bestI || r2 == r1);
                vec x1 = popX.col(r1);
                vec x2 = popX.col(r2);
                int r = rndInt(dim);
                vec x = vec(xp);
                for (int j = 0; j < dim; j++) {
                    if (j == r || rnd01() < CR) {
                        x[j] = xb[j] + F * (x1[j] - x2[j]);
                        if (!fitfun->feasible(j, x[j]))
                            x[j] = fitfun->normXi(j);
                    }
                }
                modify(x);
                double y = fitfun->eval(x);
                if (isfinite(y) && y < popY[p]) {
                    // temporal locality
                    vec x2 = next_improve(xb, x, xp);
                    double y2 = fitfun->eval(x2);
                    if (isfinite(y2) && y2 < y) {
                        y = y2;
                        x = x2;
                    }
                    popX.col(p) = x;
                    popY(p) = y;
                    popIter[p] = iterations;
                    if (y < popY[bestI]) {
                        bestI = p;
                        if (y < bestY) {
                            fitfun->updateSigma(x);
                            bestY = y;
                            bestX = x;
                            if (isfinite(stopfitness) && bestY < stopfitness) {
                                stop = 1;
                                return;
                            }
                        }
                    }
                } else {
                    // reinitialize individual
                    if (keep * rnd01() < iterations - popIter[p]) {
                        popX.col(p) = fitfun->normX();
                        popY[p] = DBL_MAX;
                    }
                }
            }
        }
    }

    void init() {
        popX = mat(dim, popsize);
        popY = vec(popsize);
        for (int p = 0; p < popsize; p++) {
            popX.col(p) = fitfun->guess;
            popY[p] = DBL_MAX; // compute fitness
        }
        bestI = 0;
        bestX = popX.col(bestI);
        popIter = zeros(popsize);
    }

    vec getBestX() {
        return bestX;
    }

    double getBestValue() {
        return bestY;
    }

    double getIterations() {
        return iterations;
    }

    double getStop() {
        return stop;
    }

private:
    long runid;
    Fitness *fitfun;
    int popsize; // population size
    int dim;
    int maxEvaluations;
    double keep;
    double stopfitness;
    int iterations;
    double bestY;
    vec bestX;
    int bestI;
    int stop;
    double F0;
    double CR0;
    Eigen::Rand::P8_mt19937_64 *rs;
    mat popX;
    vec popY;
    vec popIter;
    double min_mutate;
    double max_mutate;
    bool *isInt;
};

// see https://cvstuff.wordpress.com/2014/11/27/wraping-c-code-with-python-ctypes-memory-and-pointers/

}

using namespace l_differential_evolution;

extern "C" {
void optimizeLDE_C(long runid, callback_type func, int dim, double *init,
        double *sigma, int seed, double *lower, double *upper, int maxEvals,
        double keep, double stopfitness, int popsize, double F, double CR, 
        double min_mutate, double max_mutate, bool *ints, double* res) {
    vec guess(dim), lower_limit(dim), upper_limit(dim), inputSigma(dim);
    bool isInt[dim];
    bool useLimit = false;
    bool useIsInt = false;
    for (int i = 0; i < dim; i++) {
        guess[i] = init[i];
        inputSigma[i] = sigma[i];
        lower_limit[i] = lower[i];
        upper_limit[i] = upper[i];
        useLimit |= (lower[i] != 0);
        useLimit |= (upper[i] != 0);
        isInt[i] = ints[i];
        useIsInt |= ints[i];
    }
    if (useLimit == false) {
        lower_limit.resize(0);
        upper_limit.resize(0);
    }
    Eigen::Rand::P8_mt19937_64 *rs = new Eigen::Rand::P8_mt19937_64(seed);
    Fitness fitfun(func, dim, lower_limit, upper_limit, guess, inputSigma, rs);
    LDeOptimizer opt(runid, &fitfun, dim, rs, popsize, maxEvals, keep,
            stopfitness, F, CR, min_mutate, max_mutate,
            useIsInt ? isInt : NULL);
    try {
        opt.doOptimize();
        vec bestX = opt.getBestX();
        double bestY = opt.getBestValue();
        for (int i = 0; i < dim; i++)
            res[i] = bestX[i];
        res[dim] = bestY;
        res[dim + 1] = fitfun.getEvaluations();
        res[dim + 2] = opt.getIterations();
        res[dim + 3] = opt.getStop();
    } catch (std::exception &e) {
        cout << e.what() << endl;
    }
}
}
