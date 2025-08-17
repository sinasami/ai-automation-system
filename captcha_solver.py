import cv2
import pytesseract
import numpy as np
import logging
from PIL import Image
import config

logger = logging.getLogger(__name__)

class CaptchaSolver:
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 8'
        self.preprocessing_methods = [
            self._preprocess_gray,
            self._preprocess_threshold,
            self._preprocess_adaptive,
            self._preprocess_morphology,
            self._preprocess_denoise
        ]
    
    def solve_captcha(self, image_path, captcha_type="text"):
        try:
            if captcha_type == "text":
                return self._solve_text_captcha(image_path)
            elif captcha_type == "math":
                return self._solve_math_captcha(image_path)
            elif captcha_type == "image":
                return self._solve_image_captcha(image_path)
            else:
                logger.warning(f"Unsupported captcha type: {captcha_type}")
                return None
        except Exception as e:
            logger.error(f"Error solving captcha: {e}")
            return None
    
    def _solve_text_captcha(self, image_path):
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return None
            
            best_result = None
            best_confidence = 0
            
            for preprocess_method in self.preprocessing_methods:
                try:
                    processed_image = preprocess_method(image)
                    text = pytesseract.image_to_string(
                        processed_image, 
                        config=self.tesseract_config
                    )
                    
                    confidence = self._calculate_confidence(text)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_result = text.strip()
                        
                except Exception as e:
                    logger.debug(f"Preprocessing method failed: {e}")
                    continue
            
            if best_result:
                logger.info(f"Solved text captcha: {best_result}")
                return best_result
            else:
                logger.warning("Could not solve text captcha")
                return None
                
        except Exception as e:
            logger.error(f"Error solving text captcha: {e}")
            return None
    
    def _solve_math_captcha(self, image_path):
        try:
            text_result = self._solve_text_captcha(image_path)
            if not text_result:
                return None
            
            math_expression = self._extract_math_expression(text_result)
            if math_expression:
                try:
                    result = eval(math_expression)
                    logger.info(f"Solved math captcha: {math_expression} = {result}")
                    return str(result)
                except:
                    logger.warning(f"Could not evaluate math expression: {math_expression}")
                    return None
            else:
                logger.warning("Could not extract math expression from captcha")
                return None
                
        except Exception as e:
            logger.error(f"Error solving math captcha: {e}")
            return None
    
    def _solve_image_captcha(self, image_path):
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            features = self._extract_image_features(image)
            if features:
                logger.info("Extracted image features for image captcha")
                return features
            else:
                logger.warning("Could not extract image features")
                return None
                
        except Exception as e:
            logger.error(f"Error solving image captcha: {e}")
            return None
    
    def _preprocess_gray(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _preprocess_threshold(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return threshold
    
    def _preprocess_adaptive(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return adaptive
    
    def _preprocess_morphology(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((1, 1), np.uint8)
        morphology = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        return morphology
    
    def _preprocess_denoise(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        return denoised
    
    def _calculate_confidence(self, text):
        if not text or len(text.strip()) == 0:
            return 0
        
        text = text.strip()
        confidence = len(text)
        
        if text.isalnum():
            confidence += 10
        
        if text.isdigit():
            confidence += 5
        
        if len(text) >= 3 and len(text) <= 8:
            confidence += 15
        
        return confidence
    
    def _extract_math_expression(self, text):
        import re
        
        math_patterns = [
            r'(\d+\s*[\+\-\*\/]\s*\d+)',
            r'(\d+\s*\+\s*\d+)',
            r'(\d+\s*\-\s*\d+)',
            r'(\d+\s*\*\s*\d+)',
            r'(\d+\s*\/\s*\d+)'
        ]
        
        for pattern in math_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_image_features(self, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            features = {}
            
            features['size'] = image.shape[:2]
            features['mean_color'] = np.mean(gray)
            features['std_color'] = np.std(gray)
            
            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'] = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
            if corners is not None:
                features['corner_count'] = len(corners)
            else:
                features['corner_count'] = 0
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting image features: {e}")
            return None
    
    def detect_captcha_presence(self, page_source):
        captcha_indicators = [
            'captcha', 'recaptcha', 'verify', 'robot', 'human',
            'security check', 'verification', 'challenge'
        ]
        
        page_lower = page_source.lower()
        for indicator in captcha_indicators:
            if indicator in page_lower:
                return True
        return False
    
    def detect_captcha_type(self, page_source):
        page_lower = page_source.lower()
        
        if 'recaptcha' in page_lower:
            return 'recaptcha'
        elif 'math' in page_lower or 'calculate' in page_lower:
            return 'math'
        elif 'image' in page_lower and 'select' in page_lower:
            return 'image'
        else:
            return 'text'
    
    def is_captcha_solved(self, page_source):
        success_indicators = [
            'success', 'verified', 'correct', 'passed',
            'completed', 'validated', 'approved'
        ]
        
        page_lower = page_source.lower()
        for indicator in success_indicators:
            if indicator in page_lower:
                return True
        return False
    
    def get_captcha_field_info(self, page_source):
        import re
        
        captcha_patterns = {
            'input': r'<input[^>]*captcha[^>]*>',
            'div': r'<div[^>]*captcha[^>]*>',
            'iframe': r'<iframe[^>]*recaptcha[^>]*>',
            'script': r'<script[^>]*recaptcha[^>]*>'
        }
        
        info = {}
        for field_type, pattern in captcha_patterns.items():
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                info[field_type] = len(matches)
        
        return info
    
    def estimate_solving_time(self, captcha_type, complexity="medium"):
        base_times = {
            'text': 2,
            'math': 3,
            'image': 5,
            'recaptcha': 10
        }
        
        complexity_multipliers = {
            'easy': 0.5,
            'medium': 1.0,
            'hard': 2.0
        }
        
        base_time = base_times.get(captcha_type, 5)
        multiplier = complexity_multipliers.get(complexity, 1.0)
        
        return base_time * multiplier
    
    def validate_captcha_solution(self, solution, expected_format=None):
        if not solution:
            return False
        
        if expected_format == "numeric":
            return solution.isdigit()
        elif expected_format == "alphanumeric":
            return solution.isalnum()
        elif expected_format == "email":
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_pattern, solution) is not None
        else:
            return len(solution.strip()) > 0


