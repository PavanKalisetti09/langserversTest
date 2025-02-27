#!/usr/bin/env python3
import json
import os
import argparse
from pathlib import Path
import logging
from lsp_service import LspService

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CodeBrowserAPI")

class CodeBrowserAPI:
    def __init__(self, workspace_dir=None):
        """Initialize the Code Browser API with a workspace directory"""
        if workspace_dir:
            self.workspace_dir = Path(workspace_dir).absolute()
        else:
            self.workspace_dir = Path.cwd().absolute()
            
        logger.info(f"Initializing Code Browser API with workspace: {self.workspace_dir}")
        self.lsp_service = LspService(self.workspace_dir)
    
    def goto_definition(self, symbol_name):
        """Find where a symbol is defined across the workspace"""
        logger.info(f"Looking for definition of '{symbol_name}' across workspace")
        
        # Search through all indexed files
        seen_locations = set()  # Track unique locations
        results = []
        
        for file_ext, files in self.lsp_service.file_index.items():
            for file_path in files:
                try:
                    # Get server for this file type
                    server = self.lsp_service.get_server_for_file(file_path)
                    if not server:
                        continue
                        
                    # Open the document
                    self.lsp_service.open_document(file_path)
                    
                    # Find the position of the symbol in this file
                    line, character = server.find_symbol_position(file_path, symbol_name)
                    if line is not None:
                        # Found the symbol, get its definition
                        definition = server.find_definition(file_path, line, character)
                        if definition:
                            # Process and deduplicate definitions
                            for def_loc in self.lsp_service._process_locations(definition, symbol_name)["results"]:
                                # Create a unique key for this location
                                loc_key = (def_loc['file'], def_loc['line'], def_loc['column'])
                                if loc_key not in seen_locations:
                                    seen_locations.add(loc_key)
                                    results.append(def_loc)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    
        if not results:
            return json.dumps({"error": f"No definition found for '{symbol_name}'"}, indent=2)
        return json.dumps({"results": results}, indent=2)
    
    def goto_references(self, symbol_name):
        """Find all references to a symbol across the workspace"""
        logger.info(f"Looking for references to '{symbol_name}' across workspace")
        
        # Search through all indexed files
        seen_locations = set()  # Track unique locations
        results = []
        definition_locations = set()  # Track definition locations
        
        # First, find all definitions to exclude them from references
        for file_ext, files in self.lsp_service.file_index.items():
            for file_path in files:
                try:
                    server = self.lsp_service.get_server_for_file(file_path)
                    if not server:
                        continue
                        
                    self.lsp_service.open_document(file_path)
                    line, character = server.find_symbol_position(file_path, symbol_name)
                    if line is not None:
                        definition = server.find_definition(file_path, line, character)
                        if definition:
                            for def_loc in self.lsp_service._process_locations(definition, symbol_name)["results"]:
                                def_key = (def_loc['file'], def_loc['line'], def_loc['column'])
                                definition_locations.add(def_key)
                except Exception as e:
                    logger.error(f"Error finding definition in {file_path}: {e}")
        
        # Now find all references
        for file_ext, files in self.lsp_service.file_index.items():
            for file_path in files:
                try:
                    server = self.lsp_service.get_server_for_file(file_path)
                    if not server:
                        continue
                        
                    self.lsp_service.open_document(file_path)
                    line, character = server.find_symbol_position(file_path, symbol_name)
                    if line is not None:
                        # Set includeDeclaration to True to get all references
                        references = server.find_references(file_path, line, character, include_declaration=True)
                        if references:
                            for ref in self.lsp_service._process_locations(references, symbol_name)["results"]:
                                loc_key = (ref['file'], ref['line'], ref['column'])
                                # Only add if not a definition and not already seen
                                if loc_key not in definition_locations and loc_key not in seen_locations:
                                    seen_locations.add(loc_key)
                                    results.append(ref)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                
        if not results:
            return json.dumps({"error": f"No references found for '{symbol_name}'"}, indent=2)
        return json.dumps({"results": results}, indent=2)
    
    def _is_definition(self, location):
        """Check if a location is likely to be a definition"""
        if not location.get('context'):
            return False
        
        for ctx_line in location['context']:
            if ctx_line.startswith('→'):
                line = ctx_line.split(':', 1)[1].strip()
                # Check if this line defines a function, class, or variable
                if (line.startswith('def ') or 
                    line.startswith('class ') or 
                    '=' in line or 
                    line.startswith('import ') or 
                    line.startswith('from ')):
                    return True
        return False
    
    def find_symbol(self, symbol_name):
        """Find a symbol across the workspace"""
        logger.info(f"Looking for symbol '{symbol_name}' across workspace")
        result = self.lsp_service.find_symbol(symbol_name)
        return json.dumps(result, indent=2)
    
    def get_symbol_context(self, file_path, line):
        """Get the context around a symbol"""
        logger.info(f"Getting context at {file_path}:{line}")
        result = self.lsp_service.get_symbol_context(file_path, line)
        return json.dumps(result, indent=2)
    
    def shutdown(self):
        """Shutdown the LSP service"""
        logger.info("Shutting down LSP service")
        self.lsp_service.shutdown()


def main():
    """Command-line interface for the Code Browser API"""
    parser = argparse.ArgumentParser(description='Code Browser API')
    parser.add_argument('--workspace', help='Workspace directory', default=None)
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # goto_definition command
    definition_parser = subparsers.add_parser('goto_definition', help='Go to definition of a symbol')
    definition_parser.add_argument('symbol', help='Symbol to find definition for')
    
    # goto_references command
    references_parser = subparsers.add_parser('goto_references', help='Find references to a symbol')
    references_parser.add_argument('symbol', help='Symbol to find references for')
    
    # find_symbol command
    symbol_parser = subparsers.add_parser('find_symbol', help='Find a symbol in the workspace')
    symbol_parser.add_argument('symbol', help='Symbol to find')
    
    # get_symbol_context command
    context_parser = subparsers.add_parser('get_symbol_context', help='Get context around a symbol')
    context_parser.add_argument('file', help='File containing the symbol')
    context_parser.add_argument('line', type=int, help='Line number')
    
    args = parser.parse_args()
    
    browser = CodeBrowserAPI(args.workspace)
    
    try:
        if args.command == 'goto_definition':
            print(browser.goto_definition(args.symbol))
        elif args.command == 'goto_references':
            print(browser.goto_references(args.symbol))
        elif args.command == 'find_symbol':
            print(browser.find_symbol(args.symbol))
        elif args.command == 'get_symbol_context':
            print(browser.get_symbol_context(args.file, args.line))
        else:
            parser.print_help()
    finally:
        browser.shutdown()

if __name__ == "__main__":
    main()
