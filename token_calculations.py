from datasets import load_dataset
import time
import re
import random
from tokenizer import count_tokens

begin = time.time()
en_list = []
jp_list = []
sample_size = 9000
ds = load_dataset("lmg-anon/VNTL-v3.1-1k", split='val[1%:50%]')
elapsed_dataset = ( time.time() - begin).__round__(2)

# Setting up variables

begin = time.time()

def process_dataset(dataset):
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

elapsed_sort = ( time.time() - begin).__round__(2)



def tokenize_samples(samples, typex):
    all_tokens = 0
    print(f"Beginning tokenizing of samples for type: {typex}")
    for idx, sample in enumerate(samples):
        #print(f"Processing Sample {idx} for type: {typex}")
        tokens = count_tokens(sample)
        #print(f"Token Count: {tokens}")
        all_tokens += tokens
        #print(f'All Tokens Count: {tokens}')
    average_tokens = all_tokens / len(samples)
    return average_tokens

print(f'Loaded dataset in {elapsed_dataset} seconds')
process_dataset(ds)
print(f'Processed dataset in {elapsed_sort} seconds')
print("JP lines: ",len(jp_list))
print("EN lines: ",len(en_list))
print("Sample size: ", sample_size)
en_samples = random.sample(en_list, sample_size)
jp_samples = random.sample(jp_list, sample_size)
average_en_tokens = tokenize_samples(en_samples, 'en')
average_jp_tokens = tokenize_samples(jp_samples, 'jp')
token_coefficient = average_en_tokens / average_jp_tokens
print("Average JP tokens: ", average_jp_tokens)
print("Average EN tokens: ", average_en_tokens)
print(f"Token coefficient(How much EN Tokens for JP Token): {token_coefficient}")


















