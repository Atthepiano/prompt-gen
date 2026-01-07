from deep_translator import GoogleTranslator
import concurrent.futures

class TranslationManager:
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranslationManager, cls).__new__(cls)
            cls._instance.translator = GoogleTranslator(source='auto', target='en')
        return cls._instance

    def translate_text(self, text):
        """
        Translates text to English using Google Translator.
        Includes basic caching.
        """
        if not text:
            return ""
            
        if text in self._cache:
            return self._cache[text]
            
        try:
            translated = self.translator.translate(text)
            self._cache[text] = translated
            return translated
        except Exception as e:
            print(f"Translation Error for '{text}': {e}")
            return text

    def translate_list(self, text_list, max_workers=3):
        """
        Translates a list of strings concurrently.
        """
        if not text_list:
            return []
            
        # Identify what actually needs translation (not in cache)
        to_translate = []
        indices_to_translate = []
        
        results = [""] * len(text_list)
        
        for i, text in enumerate(text_list):
            if not text:
                results[i] = ""
            elif text in self._cache:
                results[i] = self._cache[text]
            else:
                to_translate.append(text)
                indices_to_translate.append(i)
        
        if not to_translate:
            return results
            
        # Execute concurrent requests for missing items
        # deep-translator's batch mode is sometimes just a loop, 
        # so using threads here gives us better control over concurrency.
        # CRITICAL FIX: Create a NEW translator instance for each thread to avoid race conditions
        # with internal state (which caused the "all ores = platinum_ore" bug).
        def _translate_worker(text):
            import time
            import random
            
            retries = 3
            last_error = None
            
            for attempt in range(retries):
                try:
                    # Add jitter delay to prevent thundering herd
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    # Create new instance for thread safety
                    t = GoogleTranslator(source='auto', target='en')
                    result = t.translate(text)
                    
                    # Validate result
                    if result:
                        lower_res = result.lower()
                        # Check for known error signatures returned as text
                        if "error" in lower_res and ("504" in lower_res or "server" in lower_res or "request" in lower_res):
                            raise Exception(f"Detected Error Message in response: {result}")
                            
                    return result
                    
                except Exception as e:
                    last_error = e
                    print(f"Translation attempt {attempt+1}/{retries} failed for '{text}': {e}")
                    # Exponential backoff + Jitter
                    time.sleep((2 ** attempt) + random.uniform(0, 1))
            
            raise last_error

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(_translate_worker, text): idx 
                for text, idx in zip(to_translate, indices_to_translate)
            }
            
            for future in concurrent.futures.as_completed(future_to_index):
                idx = future_to_index[future]
                original_text = text_list[idx]
                try:
                    translated = future.result()
                    self._cache[original_text] = translated
                    results[idx] = translated
                except Exception as e:
                    print(f"Batch Translation Error for '{original_text}': {e}")
                    results[idx] = original_text
                    
        return results

def translate_batch(texts):
    """
    Helper to translate a list of strings.
    """
    manager = TranslationManager()
    return manager.translate_list(texts)
