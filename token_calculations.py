import random
import re
from time import perf_counter as timer

from datasets import load_dataset

from tokenizer import count_tokens

begin = timer()

sample_size = 1000

elapsed_dataset = (timer() - begin)

# Setting up variables

begin = timer()
en_list = []
jp_list = []

'''This file is an experiment on how many tokens does a line use for English and Japanese
We download the VNTL dataset with jp:en pairs from various visual novels, 
calculate tokens for a Japanese line, then for a English one, then compare them
The results in my testing were that for a given japanese line, the English one uses on average 10-15% more tokens
'''


def process_dataset(dataset):
    print('Processing dataset')
    en_jp_dict = {}
    for line in dataset['text']:
        start = line.find('<<JAPANESE>>')
        line = line[start:]
        pattern = r"<<JAPANESE>>\n(.*?)(?=\n<<ENGLISH>>)\n<<ENGLISH>>\n(.*?)(?=</s>)"
        matches = re.findall(pattern, line)
        for match in matches:
            japanese_text = match[0]
            jp_list.append(japanese_text)
            english_text = match[1]
            en_list.append(english_text)
            en_jp_dict[japanese_text] = english_text
    return en_jp_dict


elapsed_sort = (timer() - begin)


def tokenize_samples(samples, typex):
    all_tokens = 0
    print(f"Beginning tokenizing of samples for type: {typex}")
    for idx, sample in enumerate(samples):
        # print(f"Processing Sample {idx} for type: {typex}")
        tokens = count_tokens(sample)
        # print(f"Token Count: {tokens}")
        all_tokens += tokens
        # print(f'All Tokens Count: {tokens}')
    average_tokens = all_tokens / len(samples)
    return average_tokens


def model_benchmark(dataset):
    # This can be used for creating a dict of only the JP:EN pairs to further benchmark the model.
    jp_dict = {key: '' for key in dataset}


ds = load_dataset("lmg-anon/VNTL-v3.1-1k", split='val').shuffle()
print(f'Loaded dataset in {elapsed_dataset:.2f} seconds')
print('=' * 24)
process_dataset(ds)
print(f'Processed dataset in {elapsed_sort:.2f} seconds')
print('=' * 24)
print("JP lines: ", len(jp_list))
print("EN lines: ", len(en_list))
print("Sample size: ", sample_size)
en_samples = random.sample(en_list, sample_size)
jp_samples = random.sample(jp_list, sample_size)
average_en_tokens = tokenize_samples(en_samples, 'en')
average_jp_tokens = tokenize_samples(jp_samples, 'jp')
token_coefficient = average_en_tokens / average_jp_tokens
print("Average JP tokens: ", average_jp_tokens)
print("Average EN tokens: ", average_en_tokens)
print(f"Token coefficient(How much EN Tokens for JP Token): {token_coefficient:.2f}")
