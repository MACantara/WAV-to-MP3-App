import os
import pickle
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleServices:
    def __init__(self):
        """Initialize the Google Services."""
        try:
            # Get the directory where the executable/script is located
            if getattr(sys, 'frozen', False):
                # If the application is run as a bundle (exe)
                application_path = sys._MEIPASS
                working_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            else:
                # If the application is run as a script
                application_path = os.path.dirname(os.path.abspath(__file__))
                working_dir = application_path

            # Set up paths for credentials and token
            credentials_path = os.path.join(application_path, 'credentials.json')
            token_path = os.path.join(working_dir, 'token.pickle')

            print(f"Credentials path: {credentials_path}")
            print(f"Token path: {token_path}")

            self.scopes = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]

            self.creds = None

            # Check if token.pickle exists and is valid
            if os.path.exists(token_path):
                try:
                    with open(token_path, 'rb') as token:
                        self.creds = pickle.load(token)
                    print("Loaded existing token")
                except Exception as e:
                    print(f"Error loading token: {str(e)}")
                    self.creds = None

            # If no valid credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("Token expired, refreshing...")
                    try:
                        self.creds.refresh(Request())
                        print("Token refreshed successfully")
                    except Exception as e:
                        print(f"Error refreshing token: {str(e)}")
                        self.creds = None

                if not self.creds:
                    print("No valid credentials, starting OAuth flow...")
                    if not os.path.exists(credentials_path):
                        raise FileNotFoundError(
                            f"credentials.json not found at {credentials_path}. Please ensure it exists in the same directory as the application."
                        )
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.scopes)
                        self.creds = flow.run_local_server(port=0)
                        print("OAuth flow completed successfully")
                    except Exception as e:
                        raise Exception(f"Failed to complete OAuth flow: {str(e)}")

                # Save the credentials for the next run
                try:
                    with open(token_path, 'wb') as token:
                        pickle.dump(self.creds, token)
                    print(f"Saved new token to {token_path}")
                except Exception as e:
                    print(f"Warning: Could not save token: {str(e)}")

            # Create API service instances
            try:
                self.drive_service = build('drive', 'v3', credentials=self.creds)
                self.sheets_service = build('sheets', 'v4', credentials=self.creds)
                print("Successfully created API service instances")
            except Exception as e:
                raise Exception(f"Failed to create API services: {str(e)}")

        except Exception as e:
            raise Exception(f"Failed to initialize Google Services: {str(e)}")

    def initialize_credentials(self):
        """Authenticate with Google services."""
        if os.path.exists('token.pickle'):
            try:
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)
            except:
                if os.path.exists('token.pickle'):
                    os.remove('token.pickle')
                self.creds = None

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except:
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    self.creds = None
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.scopes)
                    self.creds = flow.run_local_server(port=0)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def upload_to_drive(self, file_path, folder_id, progress_callback=None):
        """Upload a file to Google Drive in the specified folder."""
        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [folder_id]
            }
            
            # Get file size for progress tracking
            file_size = os.path.getsize(file_path)
            
            # Create a media uploader with progress tracking
            media = MediaFileUpload(
                file_path,
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            # Create the file first
            request = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            )
            
            # Upload the file in chunks and track progress
            response = None
            uploaded_bytes = 0
            while response is None:
                status, response = request.next_chunk()
                if status:
                    uploaded_bytes = status.resumable_progress
                    if progress_callback:
                        progress = (uploaded_bytes / file_size) * 100
                        progress_callback(progress)
            
            # Ensure 100% progress is reported
            if progress_callback:
                progress_callback(100)
                
            file = response
            return file.get('id'), file.get('webViewLink')
            
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")

    def update_spreadsheet(self, spreadsheet_id, range_name, values, unmatched_handler=None):
        """Update the spreadsheet with file links.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The range in A1 notation (e.g., 'Sheet1!A:B')
            values: List of [filename, link] pairs
            unmatched_handler: Callback function for handling unmatched files
        """
        try:
            print(f"Starting spreadsheet update with ID: {spreadsheet_id}")
            sheet_name = range_name.split('!')[0]
            
            # Get existing data starting from row 4
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A4:B"
            ).execute()
            
            existing_rows = result.get('values', [])
            print(f"Found {len(existing_rows)} existing rows")
            updated_rows = []  # Track which rows were updated
            unmatched_files = []  # Track files without exact matches
            
            # Process each new file
            for filename, link in values:
                print(f"Processing file: {filename}")
                # Create a hyperlink formula with filename as the display text
                display_name = os.path.splitext(os.path.basename(filename))[0]  # Remove extension if present
                hyperlink_formula = f'=HYPERLINK("{link}","{display_name}.mp3")'
                found_match = False
                
                # Look for exact matching filename in existing rows
                for i, row in enumerate(existing_rows):
                    if not row:  # Skip empty rows
                        continue
                    
                    existing_filename = row[0] if row else ""
                    print(f"Comparing with existing: {existing_filename}")
                    # Check for exact match (case-insensitive)
                    if filename.lower() == existing_filename.lower():
                        print(f"Found match at row {i+4}")
                        # Update the link in column B with hyperlink formula
                        update_range = f"{sheet_name}!B{i+4}"
                        self.sheets_service.spreadsheets().values().update(
                            spreadsheetId=spreadsheet_id,
                            range=update_range,
                            valueInputOption='USER_ENTERED',
                            body={'values': [[hyperlink_formula]]}
                        ).execute()
                        updated_rows.append(i+4)
                        found_match = True
                        break
                
                if not found_match:
                    print(f"No match found for: {filename}")
                    unmatched_files.append([filename, hyperlink_formula])
            
            # If we have unmatched files and a handler function
            if unmatched_files and unmatched_handler:
                print(f"Found {len(unmatched_files)} unmatched files")
                # Ask user what to do with unmatched files
                if unmatched_handler(unmatched_files):
                    print("User chose to create new entries")
                    # Find the first empty row after row 4 or after the last existing row
                    next_row = 4
                    if existing_rows:
                        # Skip empty rows at the end
                        last_row = 4
                        for i, row in enumerate(existing_rows, start=4):
                            if row and any(row):  # Non-empty row
                                last_row = i
                        next_row = last_row + 1
                    
                    print(f"Adding new entries starting at row {next_row}")
                    # Add new values with hyperlink formulas
                    update_range = f"{sheet_name}!A{next_row}"
                    result = self.sheets_service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=update_range,
                        valueInputOption='USER_ENTERED',
                        body={'values': unmatched_files}
                    ).execute()
                    print(f"Update result: {result}")
            
            return True
            
        except Exception as e:
            print(f"Error in update_spreadsheet: {str(e)}")
            raise Exception(f"Error updating spreadsheet: {str(e)}")

    def get_folder_list(self):
        """Get list of folders from Google Drive."""
        try:
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)',
                pageSize=100
            ).execute()
            
            return sorted(results.get('files', []), key=lambda x: x.get('name', '').lower())
        except Exception as e:
            print(f"Error getting folder list: {str(e)}")
            return []

    def get_spreadsheet_list(self):
        """Get list of spreadsheets from Google Drive."""
        try:
            # Search for Google Sheets files
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            spreadsheets = results.get('files', [])
            return [(sheet['id'], sheet['name']) for sheet in spreadsheets]
            
        except Exception as e:
            raise Exception(f"Error getting spreadsheet list: {str(e)}")

    def get_sheets_in_spreadsheet(self, spreadsheet_id):
        """Get list of sheets/tabs in a spreadsheet."""
        try:
            # Get spreadsheet metadata including sheets
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            return [sheet['properties']['title'] for sheet in sheets]
            
        except Exception as e:
            raise Exception(f"Error getting sheets in spreadsheet: {str(e)}")
