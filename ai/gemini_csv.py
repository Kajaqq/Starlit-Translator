from enum import Enum
from time import perf_counter as timer
from time import sleep
from google.genai.types import FinishReason


"""
This is the main file handling the translation.
It sends the requests, parses them and adds them back to an updated dict.
There's a lot of options to customize here, with the most important being the prompt.
It's hardcoded here instead of dynamically read from config,
as everytime I tried to move it somewhere the model started speaking in tongues.
"""

def send_request(client, model, config, prompt):
    return client.models.generate_content(
        model=model,
        config=config,

    )

def translate_text(data_dict, client, model_data, lines_per_chunk, token_count, hints=None):
    """
    Translates a dictionary using the Gemini API, chunking by the number of lines.

    Args:
        :param client: The Gemini API client object.
        :param data_dict: The dictionary to be translated (format: {'source': 'translatedstr'}).
        :param model_data: model_data['model_name, generation_config']
        :param lines_per_chunk: The number of lines per chunk.
        :param token_count: count of all tokens in the data_dict

    Returns:
        A dictionary with the translated text (format: {'source': 'translatedstr'}).


    """
    elapsed_time = 0
    translated_dict = {}
    # translation_hints = hints or {}
    model_name, generation_config = model_data

    lines = list(data_dict.items())  # Convert dict to list of (key, value) pairs
    total_lines = len(lines)

    start_index = 0
    start_time = timer()

    while start_index < total_lines:
        chunk_lines = []

        # Build a chunk
        end_index = start_index
        while end_index < start_index + lines_per_chunk and end_index < total_lines:
            chunk_lines.append(lines[end_index])
            end_index += 1
        # Create the prompt for the current chunk
        chunk_text = ""
        for source, translated in chunk_lines:
            chunk_text += f"source: {source}\ntranslatedstr: {translated}\n---\n"
        prompt = f"""Translate the 'source' text from Japanese to English and put it in 'translatedstr'.
                            If 'translatedstr' already has text, keep it as is.
                            Do not use Markdown.
                            Do not output in json
                            Output in the same way as the input.
                            Try to split the lines in text similar to 'source'.
                            **Examples**:

                            User:

                            source: 詩花です。ユニットで活動するのは初めてで、
                            とってもワクワクしています！
                            translatedstr:

                            ---

                            source: みなさん。どうか私たちの応援、
                            よろしくお願いしますっ！
                            translatedstr:

                            ---

                            source: えーっ、玲音と詩花が新ユニットデビュー！？
                            これって、ビッグニュースじゃん！！
                            translatedstr:

                            ---

                            source: すごーい、さっそく友達に連絡しなきゃ！
                            ねぇ、もう一人の子も、すっごくカワイくない！？
                            translatedstr:

                            ---


                            Model:

                            source: 詩花です。ユニットで活動するのは初めてで、
                            とってもワクワクしています！
                            translatedstr: I'm Shika. This will be my first time working in a unit.
                            I am very, very excited!

                            ---

                            source: みなさん。どうか私たちの応援、
                            よろしくお願いしますっ！
                            translatedstr: Everyone, we look forward to being with you,
                            so please support us!

                            ---

                            source: えーっ、玲音と詩花が新ユニットデビュー！？
                            これって、ビッグニュースじゃん！！
                            translatedstr: Ehh, Leon and Shika are debuting in a new unit!?
                            That's big news, isn't it!!

                            ---

                            source: すごーい、さっそく友達に連絡しなきゃ！
                            ねぇ、もう一人の子も、すっごくカワイくない！？
                            translatedstr: Wow, I'll have to call my friends right away!
                            Hey, that other girl, isn't she pretty cute too!?

                            ---


                            Text to translate:
                            {chunk_text}
                            """
        full_response_text = ""
        finish_reason = None

        # Timeout for the loop
        loop_start_time = timer()
        loop_timeout = 120  # Seconds
        retries = 0
        max_retries = 5
        retry_delay = 5  # Initial retry delay in seconds

        while (finish_reason is None or finish_reason != FinishReason.STOP.value) and retries < max_retries:
            try:
                if finish_reason == FinishReason.MAX_TOKENS.value:
                    response = client.models.generate_content(model=model_name, config=generation_config, contents=prompt + full_response_text)
                else:
                    response = client.models.generate_content(model=model_name, config=generation_config, contents=prompt)

                if response.text:
                    print(f"Response from Gemini API: {response}")
                    full_response_text += response.text
                else:
                    print(f"Warning: No text returned for chunk starting at line {start_index}")

                # Check if any candidate finished and for what reason
                finish_reason = None
                for candidate in response.candidates:
                    if candidate.finish_reason:
                        finish_reason = candidate.finish_reason.value
                        break

                if finish_reason == FinishReason.MAX_TOKENS.value:
                    print(
                        f"MAX_TOKENS encountered, continuing generation for chunk starting at line {start_index}"
                    )
                elif finish_reason == FinishReason.STOP.value:
                    print("STOP encountered, finishing chunk.")
                    break
                elif finish_reason:
                    print(
                        f"Other finish reason encountered: {finish_reason}, continuing generation for chunk starting at line {start_index}"
                    )

            except Exception as e:
                print(f"Error during translation: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Max retries exceeded for chunk starting at line {start_index}.")
                    break

            # Check for loop timeout
            if timer() - loop_start_time > loop_timeout + retry_delay:
                print(
                    f"Loop timeout exceeded for chunk starting at line {start_index}. Moving to the next chunk."
                )
                break

        # Process the translated chunk
        if full_response_text:
            print("========================== FULL RESPONSE TEXT ==========================")
            print(full_response_text)
            print("========================== FULL RESPONSE TEXT END ==========================")
            try:
                response_pairs = full_response_text[:-4].strip().split("---")
            except Exception as e:
                response_pairs = []
                print("========================== ERROR ==========================")
                print(f"Couldn't split a pair, continuing {e}")
            for pair in response_pairs:
                if pair:
                    try:
                        split_pair = pair.split('source:')[1].split('translatedstr:')
                        current_source = split_pair[0].strip() if split_pair[0] else None
                        translated_text = split_pair[1].strip() if split_pair[1] else None
                        translated_dict[current_source] = translated_text
                    except Exception as e:
                        # TODO: Check why and when that happens, it's mostly an index out of range error
                        print(f"Error occurred while splitting pairs, continuing: {e}")
                else:
                    print("WARNING: Skipping empty pair")
        start_index = end_index

        # Progress information
        elapsed_time = timer() - start_time
        lines_processed = start_index
        progress_percentage = (lines_processed / total_lines) * 100
        estimated_total_time = (
            (elapsed_time / lines_processed) * total_lines if lines_processed > 0 else 0
        )
        estimated_remaining_time = estimated_total_time - elapsed_time


        print(f"Processed lines: {lines_processed}/{total_lines} ({progress_percentage:.2f}%)")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Estimated total time: {estimated_total_time:.2f} seconds")
        print(f"Estimated remaining time: {estimated_remaining_time:.2f} seconds")
        print("-" * 20)
    print(f'Finished in {elapsed_time:.2f} seconds')
    token_speed = token_count / elapsed_time if elapsed_time > 0 else 0
    print(f'Average speed: {token_speed:.2f} tokens/s')

    return translated_dict
