from enum import Enum
import csv
import io
import time

class API_FINISH_REASONS(Enum):
        FINISH_REASON_UNSPECIFIED = 0
        STOP = 1
        MAX_TOKENS = 2
        SAFETY = 3
        RECITATION = 4
        OTHER = 5

def translate_text(text, model, chunk_size, hints=None):
    """Translates text using the Gemini API, handling long texts by chunking and
    continuing generation if MAX_TOKENS is encountered. Ensures chunks end on
    full lines from a CSV structure.
    This file is cursed beyond belief, but it works.
    It basically takes the CSV without translations, puts it whole into the kraken's mouth
    and spits out the same CSV but now with the empty column filled and hopefully the already translated one untouched.
    Yes it can be done better, but I made it at 3AM on a mission for gods.

        :param text: The CSV text to be translated.
        :param model: Gemini API model object.
        :param chunk_size: Size of chunk to send to API.
        :param hints: A dict with a format ['a':'b'] that includes hints for the translation.

    """

    max_chunk_size = chunk_size

    translated_text = ""

    translation_hints = hints or {}

    # Use StringIO to treat the string as a file for CSV parsing
    csv_file = io.StringIO(text)
    reader = csv.reader(csv_file)
    header = next(reader)  # Get the header row
    translated_text += ",".join(header) + "\n"  # Add header to output

    lines = list(reader)
    total_lines = len(lines)

    start_index = 0
    start_time = time.time()  # Start timer

    while start_index < total_lines:
        chunk_lines = []
        chunk_size = 0

        # Build a chunk, respecting line breaks
        end_index = start_index
        while end_index < total_lines and chunk_size < max_chunk_size:
            line_text = ",".join(lines[end_index]) + "\n"
            if chunk_size + len(line_text) > max_chunk_size:
                break
            chunk_lines.append(lines[end_index])
            chunk_size += len(line_text)
            end_index += 1

        chunk_text_buffer = io.StringIO()
        csv_writer = csv.writer(chunk_text_buffer)
        csv_writer.writerows(chunk_lines)
        chunk_text = chunk_text_buffer.getvalue()

        prompt = f"""Here's a csv file. 
        The schema is as follows: {header}
        Your goal is read every line and if 'translatedstr' is empty fill it with a proper made translation. 
        Keep the original schema and interpunction.
        Output plain text
        Do not use Markdown.
        ---
        {chunk_text}
        ---"""
        full_response_text = ""
        finish_reason = None

        # Timeout for the loop
        loop_start_time = time.time()
        loop_timeout = 120  # Seconds
        retries = 0
        max_retries = 5
        retry_delay = 5 # Initial retry delay in seconds

        while (finish_reason is None or finish_reason != API_FINISH_REASONS.STOP) and retries < max_retries:
            try:
                if finish_reason == API_FINISH_REASONS.MAX_TOKENS:
                    response = model.generate_content(prompt + full_response_text)
                    max_chunk_size = int(max_chunk_size * 0.8)  # Reduce chunk size after MAX_TOKENS
                    print(f"Reducing chunk size to {max_chunk_size}")
                else:
                    response = model.generate_content(prompt)

                if response.text:
                    full_response_text += response.text
                else:
                    print(f"Warning: No text returned for chunk starting at line {start_index}")

                # Check if any candidate finished and for what reason
                finish_reason = None
                for candidate in response.candidates:
                    print(f"Candidate: {candidate.content}")
                    if candidate.finish_reason:
                        finish_reason = int(candidate.finish_reason)
                        break
                if finish_reason == API_FINISH_REASONS.MAX_TOKENS.value:
                    print(f"MAX_TOKENS encountered, continuing generation for chunk starting at line {start_index}")
                elif finish_reason == API_FINISH_REASONS.STOP.value:
                    print("STOP encountered, finishing chunk.")
                    break
                elif finish_reason:
                    print(f"Other finish reason encountered: {API_FINISH_REASONS(finish_reason).name}, continuing generation for chunk starting at line {start_index}")

            except Exception as e:
                print(f"Error during translation: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Max retries exceeded for chunk starting at line {start_index}.")
                    break

            # Check for loop timeout
            if time.time() - loop_start_time > loop_timeout + retry_delay:
                print(
                    f"Loop timeout exceeded for chunk starting at line {start_index}. Moving to the next chunk."
                )
                break

        # Process the translated chunk, ensuring CSV structure
        translated_chunk = ""
        if full_response_text:
            # Replace double quotes to avoid csv errors
            #response_text = full_response_text.strip().replace('"', "'")

            # Split the response into lines
            response_lines = full_response_text.split('\n')

            # Remove the last line if it is empty
            if response_lines and not response_lines[-1]:
                response_lines.pop()

            # Join the lines back into a single string
            translated_chunk = '\n'.join(response_lines) + '\n'

        translated_text += translated_chunk
        start_index = end_index

        # Progress information
        elapsed_time = time.time() - start_time
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

    return translated_text


