# -*- coding: utf-8 -*-
"""
    data
    ~~~~

    `data` module of the `crosswalk` package.
"""
import numpy as np
import warnings
from . import utils


class CWData:
    """Cross Walk data structure.
    """
    def __init__(self,
                 obs,
                 obs_se,
                 alt_dorms,
                 ref_dorms,
                 covs=None,
                 study_id=None,
                 add_intercept=True):
        """Constructor of CWData

        Args:
            obs (numpy.ndarray):
                Observations of the problem, can be log or logit differences.
            obs_se (numpy.ndarray):
                Standard error of the observations.
            alt_dorms (numpy.ndarray):
                Alternative definitions/methods for each observation.
            ref_dorms (numpy.ndarray):
                Reference definitions/methods for each observation.
            covs (dict{str: numpy.ndarray} | None, optional):
                Covariates linearly parametrized the observation.
            study_id (numpy.ndarray | None, optional):
                Study id for each observation.
            add_intercept (bool, optional):
                If `True`, add intercept to the current covariates.
        """
        self.obs = obs
        self.obs_se = obs_se
        self.alt_dorms = alt_dorms.astype(str)
        self.ref_dorms = ref_dorms.astype(str)
        self.covs = {} if covs is None else covs
        self.study_id = study_id

        # dimensions of observations and covariates
        self.num_obs = self.obs.size
        if not self.covs and not add_intercept:
            warnings.warn("Covariates must at least include intercept."
                          "Adding intercept automatically.")
            add_intercept = True

        if add_intercept:
            self.covs.update({'intercept': np.ones(self.num_obs)})

        self.num_covs = len(self.covs)

        # check inputs
        self.check()

        # definition structure
        self.num_dorms, \
        self.dorm_sizes,\
        self.unique_dorms = utils.array_structure(
            np.hstack((self.alt_dorms, self.ref_dorms))
        )
        self.num_alt_dorms, \
        self.alt_dorm_sizes, \
        self.unique_alt_dorms = utils.array_structure(
            self.alt_dorms
        )
        self.num_ref_dorms, \
        self.ref_dorm_sizes, \
        self.unique_ref_dorms = utils.array_structure(
            self.ref_dorms
        )
        self.max_dorm = self.unique_dorms[np.argmax(self.dorm_sizes)]
        self.min_dorm = self.unique_dorms[np.argmin(self.dorm_sizes)]
        self.max_alt_dorm = self.unique_alt_dorms[
            np.argmax(self.alt_dorm_sizes)]
        self.min_alt_dorm = self.unique_alt_dorms[
            np.argmin(self.alt_dorm_sizes)]
        self.max_ref_dorm = self.unique_ref_dorms[
            np.argmax(self.ref_dorm_sizes)]
        self.min_alt_dorm = self.unique_ref_dorms[
            np.argmin(self.ref_dorm_sizes)]

        self.dorm_idx = {
            dorm: i
            for i, dorm in enumerate(self.unique_dorms)
        }

        # study structure
        if self.study_id is None:
            self.num_studies = self.num_obs
            self.study_sizes = np.array([1]*self.num_obs)
            self.unique_study_id = None
        else:
            self.num_studies, \
            self.study_sizes, \
            self.unique_study_id = utils.array_structure(self.study_id)
        self.sort_by_study_id()


    def check(self):
        """Check inputs type, shape and value.
        """
        assert utils.is_numerical_array(self.obs,
                                        shape=(self.num_obs,))
        assert utils.is_numerical_array(self.obs_se,
                                        shape=(self.num_obs,))
        assert (self.obs_se > 0.0).all()

        assert isinstance(self.alt_dorms, np.ndarray)
        assert isinstance(self.ref_dorms, np.ndarray)
        assert self.alt_dorms.shape == (self.num_obs,)
        assert self.ref_dorms.shape == (self.num_obs,)

        assert isinstance(self.covs, dict)
        assert len(self.covs) == self.num_covs
        for cov_name in self.covs:
            assert isinstance(cov_name, str)
            assert utils.is_numerical_array(self.covs[cov_name],
                                            shape=(self.num_obs,))

        if self.study_id is not None:
            assert utils.is_numerical_array(self.study_id,
                                            shape=(self.num_obs,))

    def sort_by_study_id(self):
        """Sort the observations and covariates by the study id.
        """
        if self.study_id is not None:
            sort_id = np.argsort(self.study_id)
            self.study_id = self.study_id[sort_id]
            self.obs = self.obs[sort_id]
            self.obs_se = self.obs_se[sort_id]
            self.alt_dorms = self.alt_dorms[sort_id]
            self.ref_dorms = self.ref_dorms[sort_id]
            for cov_name in self.covs:
                self.covs[cov_name] = self.covs[cov_name][sort_id]


    def __repr__(self):
        """Summary of the object.
        """
        dimension_summary = [
            "number of observations: %i" % self.num_obs,
            "number of covariates  : %i" % self.num_covs,
            "number of defs/methods: %i" % self.num_dorms,
            "number of studies     : %i" % self.num_studies,
        ]
        return "\n".join(dimension_summary)
