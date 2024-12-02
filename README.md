# Podcast Episode Uploader

A Python application that automates the workflow of converting WAV files to MP3, uploading them to Google Drive, and updating documentation in Google Sheets.

## Features

- Convert WAV files to MP3 format using FFmpeg
- Upload converted files to specified Google Drive folders
- Automatically update Google Sheets with file links
- Modern and user-friendly interface
- Progress tracking for all operations

## Prerequisites

1. Python 3.6 or higher
2. FFmpeg installed and available in system PATH
3. Google Cloud Project with Drive and Sheets APIs enabled
4. OAuth 2.0 credentials (`credentials.json`) from Google Cloud Console

## Installation

1. Clone this repository
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your Google OAuth credentials file (`credentials.json`) in the project root directory

## Setting Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Sheets API
4. Create OAuth 2.0 credentials:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials and save as `credentials.json` in the project directory

## Usage

1. Run the application:
   ```bash
   python wav_to_mp3_converter.py
   ```

2. In the application:
   - Select WAV files or a folder containing WAV files
   - Choose an output folder for MP3 files
   - Select a Google Drive folder for uploading
   - Enter the Google Sheets ID and range for documentation
   - Click "Start Processing"

3. The application will:
   - Convert WAV files to MP3
   - Upload the MP3 files to Google Drive
   - Update the specified Google Sheets with file links

## Google Sheets Format

The application expects the Google Sheets to have columns for:
- File name
- Google Drive link

Make sure to specify the correct range in the application (e.g., "Sheet1!A:B").

## Troubleshooting

1. FFmpeg not found:
   - Ensure FFmpeg is installed and added to system PATH

2. Google API errors:
   - Verify that `credentials.json` is present in the project directory
   - Check if the required APIs are enabled in Google Cloud Console
   - Ensure the Google Sheets ID and range are correct

3. Permission errors:
   - Make sure you have write access to the output folder
   - Verify that you have permission to upload to the selected Google Drive folder
   - Confirm you have edit access to the Google Sheets document
