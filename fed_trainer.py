import copy
import clients.alg_client as alg_client
import torch
from omegaconf import DictConfig, OmegaConf
from typing import *
import numpy as np
import time
from torch import Tensor, nn, optim
import utils
from utils import my_accuracy
from copy import deepcopy

class fed_task_train():
    def __init__(self, task__dataloader: dict, cfg: DictConfig, client_cfg: Dict,root_state_dict):
        self.task_id = client_cfg['task_id']
        self.task__dataloader = task__dataloader
        self.cfg = cfg
        self.client_cfg = client_cfg
        self.root_state_dict = root_state_dict

        self.num_clients = cfg.fed.num_clients[self.task_id]
        assert self.num_clients > 0, "At least one client is required."
        self.tags = self.switch_tag(self.num_clients, len(self.task__dataloader))
        self.client_models = []
        self.client_losses = []

        # Initialization
        client = getattr(alg_client, cfg.fed.alg)
        self.clients = [client(client_cfg, root_state_dict)] * self.num_clients

    def switch_tag(self, num_clients, num_batches):
        tags = [0]
        for client_id in range(num_clients):
            tags.append(tags[-1] + num_batches / num_clients - 1)
        tags[-1] += num_batches % num_clients
        return tags[1:-1]

    def train(self):
        for client_id in range(self.num_clients):
            self.clients[client_id].model.train()

        for epoch in range(self.client_cfg['epoch_max']):
            self.train_epoch()
            self.sever_epoch()

        for client_id in range(self.num_clients):
            info = self.clients[client_id].client_info()
            self.client_models.append(info['model'])
            self.client_losses.append(info['loss'])
        return self.client_models, self.client_losses

    # TODO client epoch

    def train_epoch(self):
        for epoch in self.client_cfg['client_epochs']:
            for i in range(self.num_clients):
                self.clients[i].client_epoch_reset()
            client_id = 0
            for idx_batch, (x, y) in enumerate(self.task__dataloader):
                self.clients[client_id].batch_train(x, y)
                if idx_batch in self.tags:
                    client_id += 1


    #TODO Federated Aggregation for each epoch
    def sever_epoch(self):
        pass

    #TODO Scheduler







