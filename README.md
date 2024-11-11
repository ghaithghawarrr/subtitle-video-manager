### Subtitle Video Manager

This Python script allows you to easily manage subtitles and video files. It provides several functionalities to extract, merge, remove, and translate subtitle tracks from video files, specifically targeting formats like MKV and MP4. The script also organizes output files into an `output` directory with separate subfolders for subtitles and videos.

#### Features:
- **Extract Subtitles**: Extracts subtitle tracks from video files and saves them as separate `.srt` files.
- **Merge Subtitles**: Merges multiple subtitle files with a video, allowing you to set a title for each subtitle track.
- **Remove Subtitles**: Removes all subtitle tracks from a video file.
- **Translate Subtitles**: Translates existing subtitle files to a target language using an integrated translation API.

#### File Organization:
- All extracted subtitles are saved in the `output/subtitles` folder.
- Processed video files (after merging or removing subtitles) are saved in the `output/videos` folder.

#### Requirements:
- **FFmpeg**: Used for extracting and merging subtitles.
- **pysubs2**: For reading and saving subtitle files.
- **chardet**: To detect file encoding.
- **translate**: For translating subtitle files.

#### Usage:
1. Choose an operation (extract, merge, remove, translate).
2. Provide the necessary input (video file path, subtitle files, language codes).
3. The script will automatically handle file processing and save results in the appropriate `output` folder.
