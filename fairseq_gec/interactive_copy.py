#!/usr/bin/env python3 -u
# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the LICENSE file in
# the root directory of this source tree. An additional grant of patent rights
# can be found in the PATENTS file in the same directory.
"""
Translate raw text with a trained model. Batches data on-the-fly.
"""

from collections import namedtuple
import fileinput
import sys

import torch

from fairseq import data, options, tasks, tokenizer, utils
from fairseq.sequence_generator import SequenceGenerator
from fairseq.utils import import_user_module

from hunspell_custom import correct_sentence

#Batch = namedtuple('Batch', 'ids src_tokens src_lengths, src_strs')
#Translation = namedtuple('Translation', 'src_str hypos pos_scores alignments')
# output_file = "/home/rohan/rohan/grammar_project/rohan/fairseq-gec/custom_out.txt"


def buffered_read(input, buffer_size):
    buffer = []
    with fileinput.input(files=[input], openhook=fileinput.hook_encoded("utf-8")) as h:
        # h is file object
        for src_str in h:
            buffer.append(src_str.strip())
            if len(buffer) >= buffer_size:
#                 print("My buffer",buffer)
                yield buffer
                buffer = []

    if len(buffer) > 0:

        yield buffer


def write_to_file(hypo):
    file = open(output_file,"w")
    file.write(hypo)
    file.close()

def make_batches(lines, args, task, max_positions):
    Batch = namedtuple('Batch', 'ids src_tokens src_lengths, src_strs')
    tokens = [
        task.source_dictionary.encode_line(src_str, add_if_not_exist=False, copy_ext_dict=args.copy_ext_dict).long()
        for src_str in lines
    ]
    lengths = torch.LongTensor([t.numel() for t in tokens])
    itr = task.get_batch_iterator(
        dataset=task.build_dataset_for_inference(tokens, lengths),
        max_tokens=args.max_tokens,
        max_sentences=args.max_sentences,
        max_positions=max_positions,
    ).next_epoch_itr(shuffle=False)
    for batch in itr:
        yield Batch(
            ids=batch['id'],
            src_tokens=batch['net_input']['src_tokens'], src_lengths=batch['net_input']['src_lengths'],
            src_strs=[lines[i] for i in batch['id']],
        )


def getModel():
    parser = options.get_generation_parser(interactive=True)
    args = options.parse_args_and_arch(parser)
    import_user_module(args)

    if args.buffer_size < 1:
        args.buffer_size = 1
    if args.max_tokens is None and args.max_sentences is None:
        args.max_sentences = 1

    assert not args.sampling or args.nbest == args.beam, \
        '--sampling requires --nbest to be equal to --beam'
    assert not args.max_sentences or args.max_sentences <= args.buffer_size, \
        '--max-sentences/--batch-size cannot be larger than --buffer-size'

#     print(args)

    use_cuda = torch.cuda.is_available() and not args.cpu

    # Setup task, e.g., translation
    task = tasks.setup_task(args)

    # Load ensemble
#     print('| loading model(s) from {}'.format(args.path))
    models, _model_args = utils.load_ensemble_for_inference(
        args.path.split(':'), task, model_arg_overrides=eval(args.model_overrides),
    )
    """
    Models is a list of models(different checkpoints), all of which are loaded
    on CPU.
    """

    """
    Do you want to extend target vocabulary with source tokens?
    Yes, for copy mechanism.
    """
    args.copy_ext_dict = getattr(_model_args, "copy_attention", False)



    # Optimize ensemble for generation
    #num_models = len(models)
    if use_cuda:
        cuda_devices = [torch.device('cuda:0'), torch.device('cuda:1'), torch.device('cuda:2')]
        cuda_devices = cuda_devices[:len(models)]
        #print(cuda_devices)
        assert len(models) == len(cuda_devices)

    for i,model in enumerate(models,0):
        model.make_generation_fast_(
            beamable_mm_beam_size=None if args.no_beamable_mm else args.beam,
            need_attn=args.print_alignment,
        )
        if args.fp16:
            model.half()
        if use_cuda:
            model.to(cuda_devices[i])
            #model.cuda()

    # Initialize generator

    generator = task.build_generator(args)

    # Load alignment dictionary for unknown word replacement
    # (None if no unknown word replacement, empty if no path to align dictionary)

    return (models, generator, task, args)

def runInference(reqs,spellchecker,sentences=None):
    models, generator, task, args = reqs

    # Set dictionaries
    src_dict = task.source_dictionary
    tgt_dict = task.target_dictionary

    align_dict = utils.load_align_dict(args.replace_unk)
    if align_dict is None and args.copy_ext_dict:
        align_dict = {}

    max_positions = utils.resolve_max_positions(
        task.max_positions(),
        *[model.max_positions() for model in models]
    )


#     if args.buffer_size > 1:
#         print('| Sentence buffer size:', args.buffer_size)

#     print('| Type the input sentence and press return:')
    start_id = 0
    src_strs = []
#     print("args.input",args.input)

#     sentences = [[custom_sentence]]
    #sentences = buffered_read(args.input, args.buffer_size)
    #print(len(sentences))
    #print(list(sentences))
    #print(sentences)
#     for inputs in buffered_read(args.input, args.buffer_size):
    for inputs in sentences:
        inputs = [correct_sentence(x,spellchecker) for x in inputs]
        print("Input sentence",inputs)
#         print("type",type(inputs))
#         for i in range(len(inputs)):
#             print(i," ",inputs[i],type(inputs[i])) # inputs[i] is a sentence
        results = []
        for batch in make_batches(inputs, args, task, max_positions):
            src_tokens = batch.src_tokens
            src_lengths = batch.src_lengths
            src_strs.extend(batch.src_strs)
            """
            Commenting this out. Sample(Input) components to be remain
            on CPU. Move them to corresponding GPU for inference later.
            """
            #if use_cuda:
                #src_tokens = src_tokens.cuda()
                #src_lengths = src_lengths.cuda()

            sample = {
                'net_input': {
                    'src_tokens': src_tokens,
                    'src_lengths': src_lengths,
                },
            }
            translations = task.inference_step(generator, models, sample)
            #print(translations)
            for i, (id, hypos) in enumerate(zip(batch.ids.tolist(), translations)):
                src_tokens_i = utils.strip_pad(src_tokens[i], tgt_dict.pad())
                results.append((start_id + id, src_tokens_i, hypos))

        # sort output to match input order
        final_hypo = ""
        for id, src_tokens, hypos in sorted(results, key=lambda x: x[0]):
            if src_dict is not None:
                src_str = src_dict.string(src_tokens, args.remove_bpe)
#                 print('S-{}\t{}'.format(id, src_str))

            # Process top predictions
            for hypo in hypos[:min(len(hypos), args.nbest)]:
                hypo_tokens, hypo_str, alignment = utils.post_process_prediction(
                    hypo_tokens=hypo['tokens'].int().cpu(),
                    src_str=src_strs[id],
                    alignment=hypo['alignment'].int().cpu() if hypo['alignment'] is not None else None,
                    align_dict=align_dict,
                    tgt_dict=tgt_dict,
                    remove_bpe=args.remove_bpe,
                )
#                 print("Corrected version",hypo_str)
                final_hypo = hypo_str
        return final_hypo
#                 print('H-{}\t{}\t{}'.format(id, hypo['score'], hypo_str))
#                 print('P-{}\t{}'.format(
#                     id,
#                     ' '.join(map(lambda x: '{:.4f}'.format(x), hypo['positional_scores'].tolist()))
#                 ))
#                 if args.print_alignment:
#                     print('A-{}\t{}'.format(
#                         id,
#                         ' '.join(map(lambda x: str(utils.item(x)), alignment))
#                     ))

        # update running id counter
        start_id += len(results)


def cli_main():
    #parser = options.get_generation_parser(interactive=True)
    #args = parser.parse_args()
    # args = options.parse_args_and_arch(parser)
    #print(args)
    reqs = getModel() # reqs wraps model, generator, and args
    #hypo = main(args) #returns corrected sentence
    hypo = runInference(reqs, sentences=[['My name is Khan!']])
    print("Corrected sentence: ",hypo)
    write_to_file(hypo)
    return hypo

# def non_cli_main(custom_sentence):
#     #get custom sentence for correction
#     parser = options.get_generation_parser(interactive=True)
#     args = options.parse_args_and_arch(parser)
#     hypo = main(args,custom_sentence) #returns corrected sentence
#     return hypo

if __name__ == '__main__':
#     custom_sentence = "It is because a carrier with bad gene may not necessary have those genetic disease , if they can have coresponding healthy lifestyle before the age that the gene 's function become stronger ."
#     cli_main(custom_sentence)
    cli_main()
    #This is the sentence corrected by model
#     hypo = non_cli_main(custom_sentence)
#     print("Prediction",hypo)
