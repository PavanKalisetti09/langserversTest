#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
from queue import Queue
import re
import logging
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LSPService")

class LspService:
    def __init__(self, workspace_dir='.'):
        self.workspace_dir = Path(workspace_dir).absolute()
        logger.info(f"Initializing LSP service for workspace: {self.workspace_dir}")
        
        # Maintain a dictionary of servers by language
        self.servers = {}
        
        # Language server commands by file extension
        self.language_servers = {
            ".py": ["pylsp"],
            ".c": ["clangd"],
            ".cpp": ["clangd"],
            ".h": ["clangd"],
            ".hpp": ["clangd"],
            ".java": ["/home/pavan/jdtls.sh"],
            ".js": ["typescript-language-server", "--stdio"],
            ".ts": ["typescript-language-server", "--stdio"],
            ".go": ["gopls"],
            ".rs": ["rust-analyzer"],
            ".cs": ["omnisharp", "-lsp"],
            ".php": ["phpactor", "language-server"],
        }
        
        # Index all files in the workspace
        self.file_index = self._index_workspace()
        
        # Keep track of open documents
        self.open_documents = set()
        
    def _index_workspace(self):
        """Index all code files in the workspace for faster lookup"""
        file_index = {}
        
        logger.info(f"Indexing workspace files...")
        
        for ext in self.language_servers.keys():
            file_index[ext] = []
            for file_path in self.workspace_dir.glob(f"**/*{ext}"):
                if ".git" not in str(file_path) and "__pycache__" not in str(file_path):
                    file_index[ext].append(file_path)
        
        total_files = sum(len(files) for files in file_index.values())
        logger.info(f"Indexed {total_files} code files in the workspace")
        
        return file_index
    
    def get_server_for_file(self, file_path):
        """Get or start a language server for the given file"""
        file_path = Path(file_path)
        file_ext = file_path.suffix
        
        # Check if we have a server for this language
        if file_ext in self.servers and self.servers[file_ext].is_running():
            return self.servers[file_ext]
        
        # Start a new server
        logger.info(f"Starting new language server for {file_ext} files")
        server = LanguageServer(self.workspace_dir, file_ext, self.language_servers.get(file_ext))
        if server.start():
            self.servers[file_ext] = server
            return server
        
        return None
    
    def open_document(self, file_path):
        """Open a document in the appropriate language server"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
        
        # Get server for this file type
        server = self.get_server_for_file(abs_path)
        if not server:
            logger.error(f"Could not find suitable server for {abs_path}")
            return False
        
        # Open the document if not already open
        uri = f"file://{abs_path}"
        if uri not in self.open_documents:
            result = server.open_document(abs_path)
            if result:
                self.open_documents.add(uri)
            return result
        
        return True
    
    def goto_definition(self, file_path, symbol_name):
        """Find the definition of a symbol in a file"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
        
        # Get server for this file type
        server = self.get_server_for_file(abs_path)
        if not server:
            return {"error": f"No language server available for {abs_path}"}
        
        # Make sure document is open
        self.open_document(file_path)
        
        # Find the position of the symbol
        line, character = server.find_symbol_position(abs_path, symbol_name)
        if line is None:
            return {"error": f"Symbol '{symbol_name}' not found in {file_path}"}
        
        # Find definition
        definition = server.find_definition(abs_path, line, character)
        if not definition:
            return {"error": f"No definition found for '{symbol_name}'"}
        
        # Process the response
        return self._process_locations(definition, symbol_name)
    
    def goto_references(self, file_path, symbol_name):
        """Find all references to a symbol in a file"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
        
        # Get server for this file type
        server = self.get_server_for_file(abs_path)
        if not server:
            return {"error": f"No language server available for {abs_path}"}
        
        # Make sure document is open
        self.open_document(file_path)
        
        # Find the position of the symbol
        line, character = server.find_symbol_position(abs_path, symbol_name)
        if line is None:
            return {"error": f"Symbol '{symbol_name}' not found in {file_path}"}
        
        # Find references
        references = server.find_references(abs_path, line, character)
        if not references:
            return {"error": f"No references found for '{symbol_name}'"}
        
        # Process the response
        return self._process_locations(references, symbol_name)
    
    def find_symbol(self, symbol_name):
        """Find a symbol across the entire workspace"""
        # Try each language server until we find the symbol
        results = []
        
        for ext, files in self.file_index.items():
            if not files:
                continue
                
            # Start a server for this language if necessary
            if files:
                server = self.get_server_for_file(files[0])
                if not server:
                    continue
                
                # Ask for workspace symbols
                symbols = server.find_workspace_symbol(symbol_name)
                if symbols:
                    results.extend(self._process_workspace_symbols(symbols))
        
        if not results:
            return {"error": f"No symbols found for '{symbol_name}'"}
        
        return {"results": results}
    
    def get_symbol_context(self, file_path, line):
        """Get the context around a specific line in a file, 
        showing the complete method/function if it's a method definition"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
            
        try:
            with open(abs_path, 'r') as f:
                lines = f.readlines()
                
            line_index = int(line) - 1
            if line_index < 0 or line_index >= len(lines):
                return {
                    "file": str(abs_path),
                    "line": line,
                    "context": [f"Line {line} is out of range"]
                }
                
            # Check if this is a function/method definition
            if line_index < len(lines) and ("def " in lines[line_index] or "class " in lines[line_index]):
                # This is a function/method definition, get the complete implementation
                func_lines = []
                current_indent = None
                
                # Add the function signature
                func_lines.append(f"→ {line_index+1}: {lines[line_index].rstrip()}")
                
                # Determine the indentation of the function body
                i = line_index + 1
                while i < len(lines):
                    stripped_line = lines[i].lstrip()
                    if not stripped_line or stripped_line.startswith('#'):
                        # Skip empty lines and comments
                        func_lines.append(f"  {i+1}: {lines[i].rstrip()}")
                        i += 1
                        continue
                        
                    # Calculate indentation
                    indent = len(lines[i]) - len(stripped_line)
                    if "def " in lines[line_index]:
                        # For methods/functions
                        current_indent = indent
                        break
                    elif "class " in lines[line_index]:
                        # For classes
                        current_indent = indent
                        break
                    i += 1
                
                if current_indent is None:
                    # No indented body found (one-liner or empty function)
                    return {
                        "file": str(abs_path),
                        "line": line,
                        "context": func_lines
                    }
                
                # Add all lines of the function body (with the same or greater indentation)
                i = line_index + 1
                while i < len(lines):
                    if lines[i].strip() and not lines[i].startswith(' ' * current_indent) and not lines[i].startswith('\t'):
                        # We've reached a line with less indentation than the function body
                        # This means we're outside of the function now
                        break
                        
                    func_lines.append(f"  {i+1}: {lines[i].rstrip()}")
                    i += 1
                    
                return {
                    "file": str(abs_path),
                    "line": line,
                    "context": func_lines
                }
            else:
                # Standard context (5 lines before and after)
                context_start = max(0, line_index - 5)
                context_end = min(len(lines), line_index + 6)
                
                context = []
                for i in range(context_start, context_end):
                    prefix = "→ " if i == line_index else "  "
                    context.append(f"{prefix}{i+1}: {lines[i].rstrip()}")
                
                return {
                    "file": str(abs_path),
                    "line": line,
                    "context": context
                }
            
        except Exception as e:
            logger.error(f"Failed to get context: {str(e)}")
            return {
                "file": str(abs_path),
                "line": line,
                "context": [f"Error: {str(e)}"]
            }
    
    def _process_locations(self, locations, symbol_name):
        """Process definition or reference location results"""
        if not locations:
            return {"error": f"No locations found for '{symbol_name}'"}
            
        # Handle both single location and array of locations
        if not isinstance(locations, list):
            locations = [locations]
            
        results = []
        
        for location in locations:
            # Handle both Location and LocationLink formats
            if 'uri' in location:
                # Location format
                uri = location['uri']
                target_file = uri.replace('file://', '')
                line = location['range']['start']['line'] + 1
                character = location['range']['start']['character'] + 1
            elif 'targetUri' in location:
                # LocationLink format
                uri = location['targetUri']
                target_file = uri.replace('file://', '')
                line = location['targetRange']['start']['line'] + 1
                character = location['targetRange']['start']['character'] + 1
            else:
                continue
                
            # Decode URL-encoded characters in the file path
            target_file = urllib.parse.unquote(target_file)
            
            # Get context for this location
            context = self.get_symbol_context(target_file, line)
            
            # Get relative path without URL encoding
            try:
                rel_path = os.path.relpath(target_file, self.workspace_dir)
            except ValueError:
                # Fall back to absolute path if relative path fails
                rel_path = target_file
            
            # Add to results
            results.append({
                "symbol": symbol_name,
                "file": rel_path,
                "line": line,
                "column": character,
                "context": context.get("context", [])
            })
            
        return {"results": results}
    
    def _process_workspace_symbols(self, symbols):
        """Process workspace symbol results"""
        results = []
        
        for symbol in symbols:
            uri = symbol['location']['uri']
            file_path = uri.replace('file://', '')
            rel_path = os.path.relpath(file_path, self.workspace_dir)
            line = symbol['location']['range']['start']['line'] + 1
            
            # Get the kind as a string
            kind = self._symbol_kind_to_string(symbol.get('kind', 0))
            
            results.append({
                "name": symbol['name'],
                "kind": kind,
                "file": rel_path,
                "line": line
            })
            
        return results
    
    def _symbol_kind_to_string(self, kind):
        """Convert symbol kind number to string"""
        kinds = {
            1: "file", 2: "module", 3: "namespace", 4: "package", 5: "class",
            6: "method", 7: "property", 8: "field", 9: "constructor",
            10: "enum", 11: "interface", 12: "function", 13: "variable",
            14: "constant", 15: "string", 16: "number", 17: "boolean",
            18: "array", 19: "object", 20: "key", 21: "null",
            22: "enum member", 23: "struct", 24: "event", 25: "operator",
            26: "type parameter"
        }
        return kinds.get(kind, "symbol")
    
    def shutdown(self):
        """Shutdown all language servers"""
        for server in self.servers.values():
            server.shutdown()

    def find_symbol_position(self, file_path, symbol_name):
        """Find the position of a symbol in a file"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
            
        try:
            with open(abs_path, 'r') as f:
                lines = f.readlines()
                
            # Look for the symbol in each line
            for line_num, line in enumerate(lines):
                # Look for symbol as a function/method definition
                if re.search(rf'\bdef\s+{re.escape(symbol_name)}\b', line):
                    char_pos = line.find(symbol_name)
                    return line_num, char_pos
                    
                # Look for symbol as a class definition
                if re.search(rf'\bclass\s+{re.escape(symbol_name)}\b', line):
                    char_pos = line.find(symbol_name)
                    return line_num, char_pos
                    
                # Look for symbol as a variable or other reference
                match = re.search(rf'\b{re.escape(symbol_name)}\b', line)
                if match:
                    char_pos = match.start()
                    return line_num, char_pos
                    
            return None, None
            
        except Exception as e:
            logger.error(f"Failed to find symbol: {e}")
            return None, None


class LanguageServer:
    def __init__(self, workspace_dir, file_ext, cmd):
        self.workspace_dir = workspace_dir
        self.file_ext = file_ext
        self.cmd = cmd
        self.process = None
        self.response_queue = Queue()
        self.request_id = 0
        self.capabilities = None
        self.is_initialized = False
        
    def start(self):
        """Start the language server process"""
        if self.process and self.is_running():
            return True
            
        try:
            # Adjust command for JDT LS to include workspace directory
            cmd = self.cmd
            if self.file_ext == ".java":
                cmd = self.cmd + [str(self.workspace_dir)]
            
            logger.info(f"Starting language server with command: {cmd}")
            
            # Start the language server process
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            
            # Log stderr immediately to catch early errors
            stderr_thread = threading.Thread(target=self._log_stderr, daemon=True)
            stderr_thread.start()
            
            # Start a thread to read responses
            threading.Thread(target=self._read_responses, daemon=True).start()
            
            # Initialize the server
            if not self.initialize():
                raise Exception("Failed to initialize language server")
                
            logger.info(f"Language server started successfully for {self.file_ext} files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start language server: {e}")
            return False
    def _log_stderr(self):
        """Log stderr output from the language server"""
        while self.is_running():
            line = self.process.stderr.readline()
            if line:
                logger.info(f"STDERR: {line.decode('utf-8').strip()}")
    
    def is_running(self):
        """Check if the server is running"""
        return self.process is not None and self.process.poll() is None
    
    def initialize(self):
        """Initialize the language server"""
        # Prepare initialize request
        encoded_root_uri = urllib.parse.quote(str(self.workspace_dir), safe='/:')
        params = {
            "processId": os.getpid(),
            "rootPath": str(self.workspace_dir),
            "rootUri": f"file://{encoded_root_uri}",
            "capabilities": {
                "textDocument": {
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                    "synchronization": {"dynamicRegistration": True},
                    "completion": {"dynamicRegistration": True}
                },
                "workspace": {
                    "symbol": {"dynamicRegistration": True}
                }
            }
        }
        
        # Send initialize request
        response = self._send_request("initialize", params)
        if not response or 'result' not in response:
            logger.error("Failed to initialize language server")
            return False
            
        self.capabilities = response['result']['capabilities']
        
        # Send initialized notification
        self._send_notification("initialized", {})
        
        self.is_initialized = True
        return True
    
    def shutdown(self):
        """Shutdown the language server"""
        if not self.process:
            return
            
        try:
            # Send shutdown request
            self._send_request("shutdown", None)
            
            # Send exit notification
            self._send_notification("exit", None)
            
            # Give server time to exit gracefully
            time.sleep(0.5)
            
            # Kill if still running
            if self.process.poll() is None:
                self.process.terminate()
                
            self.process = None
            self.is_initialized = False
            
            logger.info(f"Language server for {self.file_ext} shut down successfully")
            
        except Exception as e:
            logger.error(f"Error shutting down server: {e}")
    
    def open_document(self, file_path):
        """Notify the server about an open document"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
            
        # Read the file content
        try:
            with open(abs_path, 'r') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {abs_path}: {e}")
            return False
            
        # Send textDocument/didOpen notification with encoded URI
        encoded_uri = urllib.parse.quote(str(abs_path), safe='/:')
        uri = f"file://{encoded_uri}"
        params = {
            "textDocument": {
                "uri": uri,
                "languageId": abs_path.suffix[1:],  # Remove the leading dot
                "version": 1,
                "text": content
            }
        }
        
        self._send_notification("textDocument/didOpen", params)
        logger.info(f"Opened document {abs_path}")
        return True
    
    def find_definition(self, file_path, line, character):
        """Find the definition of a symbol at a position"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
            
        # Send definition request with encoded URI
        encoded_uri = urllib.parse.quote(str(abs_path), safe='/:')
        params = {
            "textDocument": {
                "uri": f"file://{encoded_uri}"
            },
            "position": {
                "line": line,
                "character": character
            }
        }
        
        response = self._send_request("textDocument/definition", params)
        if not response or 'result' not in response:
            return None
            
        return response['result']
    
    def find_references(self, file_path, line, character, include_declaration=False):
        """Find references to a symbol at a position"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
            
        # Send references request with encoded URI
        encoded_uri = urllib.parse.quote(str(abs_path), safe='/:')
        params = {
            "textDocument": {
                "uri": f"file://{encoded_uri}"
            },
            "position": {
                "line": line,
                "character": character
            },
            "context": {
                "includeDeclaration": include_declaration
            }
        }
        
        response = self._send_request("textDocument/references", params)
        if not response or 'result' not in response:
            return None
            
        return response['result']
    
    def find_workspace_symbol(self, query):
        """Find symbols in the workspace matching a query"""
        params = {
            "query": query
        }
        
        response = self._send_request("workspace/symbol", params)
        if not response or 'result' not in response:
            return None
            
        return response['result']
    
    def find_symbol_position(self, file_path, symbol_name):
        """Find the position of a symbol in a file"""
        abs_path = Path(file_path)
        if not abs_path.is_absolute():
            abs_path = (self.workspace_dir / file_path).resolve()
            
        try:
            with open(abs_path, 'r') as f:
                lines = f.readlines()
                
            # Look for the symbol in each line
            for line_num, line in enumerate(lines):
                # Look for symbol as a function/method definition
                if re.search(rf'\bdef\s+{re.escape(symbol_name)}\b', line):
                    char_pos = line.find(symbol_name)
                    return line_num, char_pos
                    
                # Look for symbol as a class definition
                if re.search(rf'\bclass\s+{re.escape(symbol_name)}\b', line):
                    char_pos = line.find(symbol_name)
                    return line_num, char_pos
                    
                # Look for symbol as a variable or other reference
                match = re.search(rf'\b{re.escape(symbol_name)}\b', line)
                if match:
                    char_pos = match.start()
                    return line_num, char_pos
                    
            return None, None
            
        except Exception as e:
            logger.error(f"Failed to find symbol: {e}")
            return None, None
    
    def _send_request(self, method, params):
        """Send a request to the language server and wait for response"""
        if not self.is_running():
            logger.error("No language server is running")
            return None
            
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        # Send the request
        self._send_message(request)
        
        # Wait for response with matching ID
        timeout = 10  # seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check for response with matching ID
                responses = []
                while not self.response_queue.empty():
                    response = self.response_queue.get()
                    if 'id' in response and response['id'] == self.request_id:
                        return response
                    responses.append(response)
                
                # Put back any non-matching responses
                for response in responses:
                    self.response_queue.put(response)
                    
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error waiting for response: {e}")
                break
                
        logger.error(f"Timeout waiting for response to {method}")
        return None
    
    def _send_notification(self, method, params):
        """Send a notification to the language server"""
        if not self.is_running():
            logger.error("No language server is running")
            return
            
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        self._send_message(notification)
    
    def _send_message(self, message):
        """Send a JSON-RPC message to the language server"""
        if not self.is_running():
            return
            
        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"
        
        try:
            self.process.stdin.write(header.encode('utf-8'))
            self.process.stdin.write(content.encode('utf-8'))
            self.process.stdin.flush()
        except BrokenPipeError:
            logger.error("Pipe to language server is broken")
            self.process = None
    
    def _read_responses(self):
        """Thread function to read responses from the language server"""
        while self.is_running():
            try:
                # Read the header
                header = b""
                content_length = None
                
                while True:
                    chunk = self.process.stdout.read(1)
                    if not chunk:
                        break
                        
                    header += chunk
                    if header.endswith(b'\r\n\r\n'):
                        # Parse content length
                        for line in header.decode('utf-8').split('\r\n'):
                            if line.startswith('Content-Length: '):
                                content_length = int(line[16:])
                                break
                        break
                
                if not content_length:
                    continue
                    
                # Read the content
                content = self.process.stdout.read(content_length)
                if content:
                    logger.info(f"RAW RESPONSE: {content.decode('utf-8')}")
                    try:
                        response = json.loads(content.decode('utf-8'))
                        self.response_queue.put(response)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse server response: {e}")
            except Exception as e:
                logger.error(f"Error reading from language server: {e}")
                break
