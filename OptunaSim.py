import optuna
from functools import partial
from numba import jit
import SimpleSimOhlc

class OptunaSim:

    @jit
    def objective(self, start, end, trial):
        kairi_term = trial.suggest_categorical('kairi_term', [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        kairi_kijun = trial.suggest_int('kairi_kijun', 5, 100000)
        pt = trial.suggest_int('pt', 100, 20000)
        lc = trial.suggest_int('lc', 100, 20000)
        sim = SimpleSimOhlc.SimpleSimOhlc()
        pl = sim.sim_contrarian_kairi(start, end, str(kairi_term), float(kairi_kijun) / 10000.0, pt, lc)[0]
        return -pl

    @jit
    def get_opt_param_for_simplesimohlc(self, start_ind, end_ind):
        if start_ind > 100:
            study = optuna.create_study()
            f = partial(self.objective, start_ind, end_ind)
            # study.optimize(objective, n_trials=100)
            study.optimize(f, n_trials=300)
            study.best_params['kairi_kijun'] = float(study.best_params['kairi_kijun']) / 10000.0
            study.best_params['kairi_term'] = str(study.best_params['kairi_term'])
            print('kairi_term={},kairi_kijun={},pt={},lc={}'.
                  format(study.best_params['kairi_term'],study.best_params['kairi_kijun'],study.best_params['pt'],study.best_params['lc']))
            return study.best_params
        else:
            print('start_ind should be bigger than 100(kairi term)')