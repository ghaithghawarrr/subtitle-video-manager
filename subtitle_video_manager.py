import subprocess
import os
import chardet
import pysubs2
from translate import Translator
import time

def extract_subtitles_from_video(video_file_path, output_directory=None):
    """
    Extracts subtitles from a video file and saves them in an 'output/subtitles' directory.
    If no directory is provided, it saves the subtitles in 'output/subtitles' folder in the same directory as the script.
    """
    # Default output directory
    if output_directory is None:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_directory = os.path.join(script_dir, 'output', 'subtitles')
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Get subtitle track information
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 's', 
           '-show_entries', 'stream=index:stream_tags=language', 
           '-of', 'csv=p=0', video_file_path]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error retrieving subtitle track information:", result.stderr)
        return
    
    subtitle_tracks = result.stdout.strip().splitlines()
    for track in subtitle_tracks:
        try:
            index, lang = track.split(',')
            lang = lang if lang else 'unknown'
            base_name = os.path.splitext(os.path.basename(video_file_path))[0]
            output_file = os.path.join(output_directory, f"{base_name}_sub{index}_{lang}.srt")
            
            # Extract the subtitle track
            cmd = ['ffmpeg', '-i', video_file_path, '-map', f'0:{index}', 
                   '-c:s', 'srt', output_file, '-y']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Extracted subtitle track {index} ({lang}) to {output_file}")
            else:
                print(f"Error extracting subtitle track {index} ({lang}):", result.stderr)
        except Exception as e:
            print(f"An error occurred while processing track {track}: {e}")

def merge_subtitles_with_video(video_file_path, subtitle_files_with_titles, output_file_path):
    cmd = ['ffmpeg', '-i', video_file_path]
    for subtitle_file, title in subtitle_files_with_titles:
        cmd.extend(['-i', subtitle_file])
    cmd.extend(['-map', '0:v', '-map', '0:a'])
    for i in range(1, len(subtitle_files_with_titles) + 1):
        cmd.extend(['-map', f'{i}:s'])
    cmd.extend(['-c:v', 'copy', '-c:a', 'copy', '-c:s', 'srt'])
    for i, (_, title) in enumerate(subtitle_files_with_titles):
        cmd.extend(['-metadata:s:s:{}'.format(i), f'title={title}'])
    cmd.append(output_file_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Subtitles merged with names. Saved output to {output_file_path}")
    else:
        print("Error merging subtitles with names:", result.stderr)

def remove_subtitles_from_video(video_file_path, output_file_path):
    cmd = ['ffmpeg', '-i', video_file_path, '-map', '0:v', '-map', '0:a', 
           '-c:v', 'copy', '-c:a', 'copy', output_file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Subtitles removed. Saved output to {output_file_path}")
    else:
        print("Error removing subtitles:", result.stderr)

def detect_file_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def translate_subtitle_file(subtitle_file_path, target_language_code, batch_size=20):
    translator = Translator(to_lang=target_language_code)
    subtitle_encoding = detect_file_encoding(subtitle_file_path)
    subs = pysubs2.load(subtitle_file_path, encoding=subtitle_encoding)
    translated_subs = pysubs2.SSAFile()
    total_lines = len(subs)
    translated_texts = []
    texts = [line.text for line in subs]
    for i in range(0, total_lines, batch_size):
        batch = texts[i:i+batch_size]
        batch_translated = [translator.translate(text) for text in batch]
        translated_texts.extend(batch_translated)
        progress = min((i + batch_size), total_lines) / total_lines * 100
        print(f"Translating batch {i // batch_size + 1} ({progress:.2f}%)")
    for i, line in enumerate(subs):
        line.text = translated_texts[i]
        translated_subs.append(line)
    translated_path = subtitle_file_path.replace(".srt", f"_{target_language_code}.srt")
    translated_subs.save(translated_path, encoding="utf-8")
    print(f"Translated subtitle saved to {translated_path}")
    return translated_path

def main():
    print("Choose an option:")
    print("1. Extract subtitles from a video")
    print("2. Merge subtitles with a video")
    print("3. Remove subtitles from a video")
    print("4. Translate a subtitle file")
    choice = input("Enter your choice (1-4): ")
    
    if choice == '1':
        video_file_path = input("Enter the path to the video file (absolute path): ")
        output_directory = input("Enter the output directory for extracted subtitles (leave empty for default 'output/subtitles'): ")
        if not output_directory:
            output_directory = None  # Will default to the 'output/subtitles' folder in the script's directory
        extract_subtitles_from_video(video_file_path, output_directory)
    
    elif choice == '2':
        video_file_path = input("Enter the path to the video file (absolute path): ")
        num_subs = int(input("Enter the number of subtitle files to merge: "))
        subtitle_files_with_titles = []
        for _ in range(num_subs):
            subtitle_file = input("Enter the path to a subtitle file (absolute path): ")
            title = input("Enter the title for this subtitle track: ")
            subtitle_files_with_titles.append((subtitle_file, title))
        output_file_path = input("Enter the output path for the video with merged subtitles: ")
        merge_subtitles_with_video(video_file_path, subtitle_files_with_titles, output_file_path)
    
    elif choice == '3':
        video_file_path = input("Enter the path to the video file (absolute path): ")
        output_file_path = input("Enter the output path for the video without subtitles: ")
        remove_subtitles_from_video(video_file_path, output_file_path)
    
    elif choice == '4':
        subtitle_file_path = input("Enter the path to the subtitle file (absolute path): ")
        target_language_code = input("Enter the target language code (e.g., 'en', 'fr', 'ar'): ")
        translate_subtitle_file(subtitle_file_path, target_language_code)
    
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
