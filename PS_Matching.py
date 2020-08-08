import numpy as np
import torch
from sklearn.neighbors import NearestNeighbors

from GAN_Manager import GAN_Manager
from Utils import Utils


class PS_Matching:
    def match_using_prop_score(self, tuple_treated, tuple_control, dL,
                               prop_score_NN_model_path, device):
        print("Propensity score Matching starts: ")
        matched_controls = []

        # do ps match
        np_treated_df_X, np_treated_ps_score, np_treated_df_Y_f, np_treated_df_Y_cf = tuple_treated
        np_control_df_X, np_control_ps_score, np_control_df_Y_f, np_control_df_Y_cf = tuple_control

        # get unmatched controls
        matched_control_indices, unmatched_control_indices = self.get_matched_and_unmatched_control_indices(
            Utils.convert_to_col_vector(np_treated_ps_score),
            Utils.convert_to_col_vector(np_control_ps_score))

        print("Matched Control: {0}".format(len(matched_control_indices)))
        print("Unmatched Control: {0}".format(len(unmatched_control_indices)))

        tuple_matched_control, tuple_unmatched_control = self.filter_matched_and_unmatched_control_samples(
            np_control_df_X, np_control_ps_score,
            np_control_df_Y_f,
            np_control_df_Y_cf, matched_control_indices,
            unmatched_control_indices)

        # generate matched treated for unmatched controls using variable
        # tuple_unmatched_control
        # create GAN code here
        print("Matched Control: {0}".format(tuple_matched_control[0].shape))
        print("Matched Treated: {0}".format(tuple_treated[0].shape))

        tensor_unmatched_control = \
            Utils.create_tensors_to_train_DCN(tuple_unmatched_control, dL)

        GAN_train_parameters = {
            "epochs": 10000,
            "lr": 0.005,
            "shuffle": True,
            "train_set": tensor_unmatched_control,
            "discriminator_in_nodes": 25,
            "generator_out_nodes": 25,
            "batch_size": 64,
            "prop_score_NN_model_path": prop_score_NN_model_path,
            "BETA": 1
        }

        gan = GAN_Manager()
        generator = gan.train_GAN(GAN_train_parameters, device=device)
        treated_generated, ps_score_list_treated = gan.eval_GAN(len(unmatched_control_indices), generator,
                                                                prop_score_NN_model_path,
                                                                device)

        # return all the controls + generated treated
        return {
            "tuple_unmatched_control": tuple_unmatched_control,
            "tuple_matched_control": tuple_matched_control,
            "treated_generated": treated_generated,
            "ps_score_list_treated": ps_score_list_treated
        }

    def filter_matched_and_unmatched_control_samples(self, np_control_df_X, np_control_ps_score,
                                                     np_control_df_Y_f,
                                                     np_control_df_Y_cf, matched_control_indices,
                                                     unmatched_control_indices):
        tuple_matched_control = self.filter_control_groups(np_control_df_X, np_control_ps_score,
                                                           np_control_df_Y_f,
                                                           np_control_df_Y_cf,
                                                           matched_control_indices)

        tuple_unmatched_control = self.filter_control_groups(np_control_df_X, np_control_ps_score,
                                                             np_control_df_Y_f,
                                                             np_control_df_Y_cf,
                                                             unmatched_control_indices)

        return tuple_matched_control, tuple_unmatched_control

    @staticmethod
    def filter_control_groups(np_control_df_X, np_control_ps_score,
                              np_control_df_Y_f,
                              np_control_df_Y_cf, indices):
        np_filter_control_df_X = np.take(np_control_df_X, indices, axis=0)
        np_filter_control_ps_score = np.take(np_control_ps_score, indices, axis=0)
        np_filter_control_df_Y_f = np.take(np_control_df_Y_f, indices, axis=0)
        np_filter_control_df_Y_cf = np.take(np_control_df_Y_cf, indices, axis=0)
        tuple_matched_control = (np_filter_control_df_X, np_filter_control_ps_score,
                                 np_filter_control_df_Y_f, np_filter_control_df_Y_cf)

        return tuple_matched_control

    @staticmethod
    def get_matched_and_unmatched_control_indices(ps_treated, ps_control):
        nn = NearestNeighbors(n_neighbors=1)
        nn.fit(ps_control)
        distance, matched_control = nn.kneighbors(ps_treated)
        matched_control_indices = np.array(matched_control).ravel()

        # remove duplicates
        # matched_control_indices = list(dict.fromkeys(matched_control_indices))
        set_matched_control_indices = set(matched_control_indices)
        total_indices = list(range(len(ps_control)))
        unmatched_control_indices = list(filter(lambda x: x not in set_matched_control_indices,
                                                total_indices))

        return matched_control_indices, unmatched_control_indices

    @staticmethod
    def get_unmatched_prop_list(tensor_unmatched_control):
        control_data_loader_train = torch.utils.data.DataLoader(tensor_unmatched_control,
                                                                batch_size=1,
                                                                shuffle=False,
                                                                num_workers=1)
        ps_unmatched_control_list = []
        for batch in control_data_loader_train:
            covariates_X, ps_score, y_f, y_cf = batch
            ps_unmatched_control_list.append(ps_score.item())

        return ps_unmatched_control_list