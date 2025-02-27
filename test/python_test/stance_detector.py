from typing import Tuple, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv
import yaml
import xml.etree.ElementTree as ET
from dataclasses import dataclass

@dataclass
class StanceAnalysis:
    text: str
    target: str
    stance: str
    confidence: str
    explanation: str

class StanceDetector:
    def __init__(self, api_key: str):
        """Initialize the StanceDetector with Gemini API key"""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load configuration from yaml file"""
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
        
    def _create_explicit_prompt(self, text: str, target: str) -> str:
        """Create a structured prompt for explicit stance detection"""
        prompt_template = self.config['stance_detection']['explicit_prompt_template']
        return prompt_template.format(text=text, target=target)

    def _create_implicit_prompt(self, text: str) -> str:
        """Create a structured prompt for implicit stance detection"""
        prompt_template = self.config['stance_detection']['implicit_prompt_template']
        return prompt_template.format(text=text)

    def _parse_xml_response(self, xml_string: str) -> StanceAnalysis:
        """Parse XML response from LLM"""
        try:
            root = ET.fromstring(xml_string)
            
            # Extract values from XML
            text = root.find('text').text
            target = root.find('target').text if root.find('target') is not None else root.find('detected_target').text
            
            # Validate target length for implicit detection
            if root.find('detected_target') is not None:  # This means it's implicit detection
                target_words = target.split()
                if len(target_words) > 4:
                    # Take first 4 words if target is too long
                    target = ' '.join(target_words[:4])
                elif len(target_words) < 1:
                    raise ValueError("Target must be at least one word")
            
            stance = root.find('stance').text
            confidence = root.find('confidence').text
            explanation = root.find('explanation').text
            
            # Validate stance
            valid_stances = self.config['stance_detection']['valid_stances']
            if stance not in valid_stances:
                raise ValueError(f"Invalid stance detected: {stance}")
            
            return StanceAnalysis(
                text=text,
                target=target,
                stance=stance,
                confidence=confidence,
                explanation=explanation
            )
            
        except ET.ParseError as e:
            raise StanceDetectionError(f"Failed to parse XML response: {str(e)}")

    async def detect_stance(self, text: str, target: str = None) -> StanceAnalysis:
        """
        Detect the stance of a given text towards a target
        If target is None, performs implicit stance detection
        Returns: StanceAnalysis object
        """
        try:
            system_prompt = self.config['stance_detection']['system_prompt']
            
            if target:
                # Explicit stance detection
                prompt = self._create_explicit_prompt(text, target)
            else:
                # Implicit stance detection
                prompt = self._create_implicit_prompt(text)
            
            response = self.model.generate_content(prompt)
            result = self._parse_xml_response(response.text)
            print(result)
            return result
            
        except Exception as e:
            raise StanceDetectionError(f"Error detecting stance: {str(e)}")

class StanceDetectionError(Exception):
    """Custom exception for stance detection errors"""
    pass 