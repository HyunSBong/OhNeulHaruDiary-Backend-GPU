import argparse
import logging
import os
import numpy as np
import pandas as pd

import lightning.pytorch as pl
from lightning.pytorch.callbacks import Callback
from lightning.pytorch import Trainer
import torch
from torch.utils.data import DataLoader, Dataset

from kobart_summ_dataset import KobartSummaryModule
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
from transformers.optimization import AdamW, get_cosine_schedule_with_warmup

from pytorch_lightning.loggers import WandbLogger

parser = argparse.ArgumentParser(description='KoBART Summarization')

class ArgsBase():
    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = argparse.ArgumentParser(
            parents=[parent_parser], add_help=False)
        parser.add_argument('--train_file',
                            type=str,
                            default='data/summary_train.tsv',
                            help='train file')

        parser.add_argument('--test_file',
                            type=str,
                            default='data/summary_test.tsv',
                            help='test file')

        parser.add_argument('--batch_size',
                            type=int,
                            default=14,
                            help='batch_size')
        
        parser.add_argument('--max_len',
                            type=int,
                            default=512,
                            help='max seq len')
        
        parser.add_argument('--checkpoint_path',
                    default='checkpoint/kobart/',
                    type=str,
                    help='checkpoint path')
        return parser

class Base(pl.LightningModule):
    def __init__(self, hparams, trainer, **kwargs) -> None:
        super(Base, self).__init__()
        self.save_hyperparameters(hparams)
        self.trainer = trainer

    @staticmethod
    def add_model_specific_args(parent_parser):
        # add model specific args
        parser = argparse.ArgumentParser(
            parents=[parent_parser], add_help=False)

        parser.add_argument('--batch-size',
                            type=int,
                            default=14,
                            help='batch size for training (default: 96)')

        parser.add_argument('--lr',
                            type=float,
                            default=3e-5,
                            help='The initial learning rate')

        parser.add_argument('--warmup_ratio',
                            type=float,
                            default=0.1,
                            help='warmup ratio')

        parser.add_argument('--model_path',
                            type=str,
                            default=None,
                            help='kobart model path')
        return parser
    
    def setup_steps(self, stage=None):
        train_loader = self.trainer._data_connector._train_dataloader_source.dataloader()
        return len(train_loader)

    def configure_optimizers(self):
        # Prepare optimizer
        param_optimizer = list(self.model.named_parameters())
        no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in param_optimizer if not any(
                nd in n for nd in no_decay)], 'weight_decay': 0.01},
            {'params': [p for n, p in param_optimizer if any(
                nd in n for nd in no_decay)], 'weight_decay': 0.0}
        ]
        optimizer = AdamW(optimizer_grouped_parameters,lr=self.hparams.lr, correct_bias=False)
        return optimizer


class KoBARTConditionalGeneration(Base):
    def __init__(self, hparams, trainer=None, **kwargs):
        super(KoBARTConditionalGeneration, self).__init__(hparams, trainer, **kwargs)
        self.model = BartForConditionalGeneration.from_pretrained('models/kobart-base-v2/')
        self.model.train()
        self.bos_token = '<s>'
        self.eos_token = '</s>'
        
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained('models/kobart-base-v2/')
        self.pad_token_id = self.tokenizer.pad_token_id

    def forward(self, inputs):

        attention_mask = inputs['input_ids'].ne(self.pad_token_id).float()
        decoder_attention_mask = inputs['decoder_input_ids'].ne(self.pad_token_id).float()
        
        return self.model(input_ids=inputs['input_ids'],
                          attention_mask=attention_mask,
                          decoder_input_ids=inputs['decoder_input_ids'],
                          decoder_attention_mask=decoder_attention_mask,
                          labels=inputs['labels'], return_dict=True)


    def training_step(self, batch, batch_idx):
        outs = self(batch)
        loss = outs.loss
        self.log('train_loss', loss, on_step=True, on_epoch=True, logger=True)
        return loss

    def validation_step(self, batch, batch_idx):
        outs = self(batch)
        loss = outs['loss']
        self.log('val_loss', loss, prog_bar=True)
        return loss
    
    def test_step_step(self, batch, batch_idx):
        outs = self(batch)
        loss = outs['loss']
        self.log('test_loss', loss, prog_bar=True)
        return loss

#     def on_validation_epoch_end(self, outputs):
#         losses = []
#         for loss in outputs:
#             losses.append(loss)
# #         self.log('val_loss', torch.stack(losses).mean(), prog_bar=True)
#         avg_loss = torch.stack(losses).mean()
#         return {'val_loss': avg_loss}
        
if __name__ == '__main__':
    
    accelerator = 'mps' if torch.backends.mps.is_available() else 'gpu'
    trainer = Trainer(accelerator=accelerator, devices=1)
    trainer = Trainer(max_epochs=50)
#     trainer = Trainer(max_epochs=50, logger=wandb_logger)
    
    parser = Base.add_model_specific_args(parser)
    parser = ArgsBase.add_model_specific_args(parser)
    parser = KobartSummaryModule.add_model_specific_args(parser)
    tokenizer = PreTrainedTokenizerFast.from_pretrained('models/kobart-base-v2/')
    args = parser.parse_args()
    
    wandb_logger = WandbLogger(project='koBart summarization optimization', job_type='train')

    dm = KobartSummaryModule(args.train_file,
                        args.test_file,
                        tokenizer,
                        batch_size=args.batch_size,
                        max_len=args.max_len,
                        num_workers=args.num_workers)

    model = KoBARTConditionalGeneration(args, trainer)
    trainer.fit(model, dm)
    wandb.finish()