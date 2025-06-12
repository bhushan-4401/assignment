"""Excel file processing module for Excel Query Bot.

Classes:
    ExcelProcessor: Main class for Excel file processing and database storage.
"""

import pandas as pd


class ExcelProcessor:
    """Excel file processor for database integration.
    
    Attributes:
        db: Database interface object for data persistence.
        cfg: Configuration object containing processing settings.
        
    """
    
    def __init__(self, db, cfg):
        """Initialize ExcelProcessor with database and configuration.
        
        Sets up the processor with necessary dependencies for Excel file
        processing and database operations.
        
        Args:
            db: Database interface object with save_df method.
            cfg: Configuration object containing processing settings.
                
        """
        self.db = db
        self.cfg = cfg
    
    def process_excel(self, file_path: str, header_row=0):
        """Process Excel file and save cleaned data to database.
        
        Args:
            file_path (str): Path to the Excel file to process.
                Must be a valid Excel file (.xlsx, .xls).
            header_row (int, optional): Row index to use as column headers.
                Defaults to 0 (first row).
                
        Returns:
            pandas.DataFrame: Processed DataFrame with cleaned column names
                and normalized data structure.
                
        """
        # Read Excel file
        df = pd.read_excel(file_path, header=header_row)
        
        # Clean column names (strip whitespace, replace spaces with underscores, lowercase)
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
        
        # Save to database
        self.db.save_df(df, table_name=self.cfg["EXCEL_TABLE_NAME"])
        
        return df
    
