from Constants import Constants
from DCN_Manager import DCN_Manager
from Utils import Utils


class DCN_Experiments:
    def __init__(self, input_nodes, device):
        self.data_loader_dict_test = None
        self.input_nodes = input_nodes
        self.device = device

    def evaluate_DCN_Model(self, tensor_treated_train_original, tensor_control_train_original,
                           n_treated_original,
                           n_control_original,
                           tensor_treated_balanced, tensor_control_balanced,
                           n_treated_balanced_dcn,
                           n_control_balanced_dcn,
                           data_loader_dict_test):
        # data loader -> (np_treated_df_X, np_treated_ps_score, np_treated_df_Y_f, np_treated_df_Y_cf)

        self.data_loader_dict_test = data_loader_dict_test

        # Model 1: DCN - PD
        print("--" * 20)
        print("###### Model 1: DCN - PD Supervised Training started ######")
        print("Train_mode: " + Constants.DCN_TRAIN_PD)
        print("n_treated: {0}".format(n_treated_original))
        print("n_control: {0}".format(n_control_original))
        dcn_pd_eval_dict = self.evaluate_DCN_PD(tensor_treated_train_original,
                                                tensor_control_train_original,
                                                n_treated_original,
                                                n_control_original,
                                                train_mode=Constants.DCN_TRAIN_PD)

        # Model 2: DCN - Dropout 0.2
        print("--" * 20)
        print("###### Model 2: DCN - Dropout 0.2 Supervised Training started ######")
        print("Train_mode: " + Constants.DCN_TRAIN_CONSTANT_DROPOUT_2)
        print("n_treated: {0}".format(n_treated_original))
        print("n_control: {0}".format(n_control_original))
        dcn_pd_02_eval_dict = self.evaluate_DCN_PD(tensor_treated_train_original,
                                                   tensor_control_train_original,
                                                   n_treated_original,
                                                   n_control_original,
                                                   train_mode=Constants.DCN_TRAIN_CONSTANT_DROPOUT_2)

        # Model 3: DCN - Dropout 0.5
        print("--" * 20)
        print("###### Model 3: DCN - Dropout 0.5 Supervised Training started ######")
        print("Train_mode: " + Constants.DCN_TRAIN_CONSTANT_DROPOUT_5)
        print("n_treated: {0}".format(n_treated_original))
        print("n_control: {0}".format(n_control_original))
        dcn_pd_05_eval_dict = self.evaluate_DCN_PD(tensor_treated_train_original,
                                                   tensor_control_train_original,
                                                   n_treated_original,
                                                   n_control_original,
                                                   train_mode=Constants.DCN_TRAIN_CONSTANT_DROPOUT_5)

        # Model 4: PM GAN - No dropout
        print("--" * 20)
        print("###### Model 4: DCN PM GAN - No dropout - Supervised Training started ######")
        print("Train_mode: " + Constants.DCN_TRAIN_NO_DROPOUT)
        print("n_treated: {0}".format(n_treated_balanced_dcn))
        print("n_control: {0}".format(n_control_balanced_dcn))
        dcn_pm_gan_eval_dict = self.evaluate_DCN_PD(tensor_treated_balanced,
                                                    tensor_control_balanced,
                                                    n_treated_balanced_dcn,
                                                    n_control_balanced_dcn,
                                                    train_mode=Constants.DCN_TRAIN_NO_DROPOUT)
        # Model 5: PM GAN - dropout - 0.2
        print("--" * 20)
        print("###### Model 5: DCN PM GAN - Probability 0.2 - Supervised Training started ######")
        print("Train_mode: " + Constants.DCN_TRAIN_CONSTANT_DROPOUT_2)
        print("n_treated: {0}".format(n_treated_balanced_dcn))
        print("n_control: {0}".format(n_control_balanced_dcn))
        dcn_pm_gan_eval_drp_02_dict = self.evaluate_DCN_PD(tensor_treated_balanced,
                                                           tensor_control_balanced,
                                                           n_treated_balanced_dcn,
                                                           n_control_balanced_dcn,
                                                           train_mode=Constants.DCN_TRAIN_CONSTANT_DROPOUT_2)

        # Model 6: PM GAN - dropout - 0.5
        print("--" * 20)
        print("###### Model 6: DCN PM GAN - Probability 0.5 - Supervised Training started ######")
        print("Train_mode: " + Constants.DCN_TRAIN_CONSTANT_DROPOUT_5)
        print("n_treated: {0}".format(n_treated_balanced_dcn))
        print("n_control: {0}".format(n_control_balanced_dcn))
        dcn_pm_gan_eval_drp_05_dict = self.evaluate_DCN_PD(tensor_treated_balanced,
                                                           tensor_control_balanced,
                                                           n_treated_balanced_dcn,
                                                           n_control_balanced_dcn,
                                                           train_mode=Constants.DCN_TRAIN_CONSTANT_DROPOUT_5)

        # Model 7: PM GAN - PD
        print("--" * 20)
        print("###### Model 7: DCN PM GAN - PD - Supervised Training started ######")
        print("Train_mode: " + Constants.DCN_TRAIN_PD)
        print("n_treated: {0}".format(n_treated_balanced_dcn))
        print("n_control: {0}".format(n_control_balanced_dcn))
        dcn_pm_gan_eval_pd_dict = self.evaluate_DCN_PD(tensor_treated_balanced,
                                                       tensor_control_balanced,
                                                       n_treated_balanced_dcn,
                                                       n_control_balanced_dcn,
                                                       train_mode=Constants.DCN_TRAIN_PD)

        return {
            "dcn_pd_eval_dict": dcn_pd_eval_dict,
            "dcn_pd_02_eval_dict": dcn_pd_02_eval_dict,
            "dcn_pd_05_eval_dict": dcn_pd_05_eval_dict,
            "dcn_pm_gan_eval_dict": dcn_pm_gan_eval_dict,
            "dcn_pm_gan_eval_drp_02_dict": dcn_pm_gan_eval_drp_02_dict,
            "dcn_pm_gan_eval_drp_05_dict": dcn_pm_gan_eval_drp_05_dict,
            "dcn_pm_gan_eval_pd_dict": dcn_pm_gan_eval_pd_dict
        }

    def evaluate_DCN_PD(self, tensor_treated_train, tensor_control_train,
                        n_treated,
                        n_control,
                        train_mode):
        DCN_train_parameters = self.__get_train_parameters(tensor_treated_train,
                                                           tensor_control_train,
                                                           n_treated,
                                                           n_control)

        tensor_treated_test = \
            Utils.create_tensors_from_tuple(self.data_loader_dict_test["treated_data"])
        tensor_control_test = \
            Utils.create_tensors_from_tuple(self.data_loader_dict_test["control_data"])
        DCN_test_parameters = self.__get_test_parameters(tensor_treated_test, tensor_control_test)

        return self.__supervised_train_eval(train_mode, DCN_train_parameters,
                                            DCN_test_parameters)

    def __supervised_train_eval(self, train_mode, DCN_train_parameters,
                                DCN_test_parameters):
        dcn_pd = DCN_Manager(self.input_nodes, self.device)
        dcn_pd.train(DCN_train_parameters, self.device, train_mode=train_mode)
        dcn_eval_dict = dcn_pd.eval(DCN_test_parameters, self.device)
        return dcn_eval_dict

    def semi_supervised_train_eval(self, treated_tensor_full_train, control_tensor_full_train,
                                   n_treated,
                                   n_control,
                                   eval_set):
        DCN_train_parameters = self.__get_train_parameters(treated_tensor_full_train,
                                                           control_tensor_full_train,
                                                           n_treated,
                                                           n_control)
        train_mode = Constants.DCN_TRAIN_PD
        dcn_pd = DCN_Manager(self.input_nodes, self.device)
        dcn_pd.train(DCN_train_parameters, self.device, train_mode=train_mode)
        DCN_test_parameters = {
            "eval_set": eval_set
        }
        return dcn_pd.eval_semi_supervised(DCN_test_parameters, self.device,
                                           treated_flag=True)

    @staticmethod
    def __get_train_parameters(tensor_treated_train, tensor_control_train,
                               n_treated,
                               n_control):
        return {
            "epochs": Constants.DCN_EPOCHS,
            "lr": Constants.DCN_LR,
            "treated_batch_size": n_treated,
            "control_batch_size": n_control,
            "shuffle": True,
            "treated_set_train": tensor_treated_train,
            "control_set_train": tensor_control_train
        }

    @staticmethod
    def __get_test_parameters(tensor_treated_test, tensor_control_test):
        return {
            "treated_set": tensor_treated_test,
            "control_set": tensor_control_test
        }
