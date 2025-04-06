# llm_service.py
import json
import re
import hashlib
import logging
import replicate
from config import REPLICATE_API_TOKEN

logging.basicConfig(level=logging.INFO)

class LLMService:
    """
    Service for generating product recommendations using Replicate's meta/meta-llama-3-8b-instruct model.
    This service builds a prompt from user preferences, browsing history, and the product catalog,
    calls the model using Replicate's run interface (with streaming enabled),
    and parses the returned text output into a JSON array of recommendations.
    It also caches responses based on a hash of the prompt.
    """
    def __init__(self):
        self.cache = {}
        # Replicate automatically uses REPLICATE_API_TOKEN from your environment.

    def _create_recommendation_prompt(self, preferences: dict, browsing_history: list, products: list) -> str:
        """
        Construct a prompt using preferences, browsing history, and a sample of products.
        """
        sample_products = products[:5]
        prompt = (
            "User Preferences:\n" + json.dumps(preferences, indent=2) + "\n\n"
            "Browsing History:\n" + json.dumps(browsing_history, indent=2) + "\n\n"
            "Available Products (sample):\n" + json.dumps(sample_products, indent=2) + "\n\n"
            "Please recommend between 3 to 5 products that best match these preferences and browsing history. "
            "For each recommendation, provide the product ID, a brief explanation, and a confidence score (1-10). "
            "Output only valid JSON in the following format:\n"
            '[{"id": "prodXYZ", "explanation": "Because...", "confidence_score": 8}, ...]'
        )
        return prompt.strip()

    def _call_llm(self, prompt: str, max_new_tokens: int = 512) -> str:
        """
        Call the Replicate API using the model "meta/meta-llama-3-8b-instruct" with the provided prompt.
        We use replicate.run with stream=True to accumulate text chunks.
        """
        input_data = {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "prompt_template": (
                "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
                "{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
                "{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            )
        }
        try:
            output = ""
            for chunk in replicate.run(
                "meta/meta-llama-3-8b-instruct",
                input=input_data,
                stream=True
            ):
                output += chunk
            return output
        except Exception as e:
            logging.error("Error calling Replicate model: %s", e)
            raise RuntimeError(f"Error calling Replicate model: {e}")

    def _parse_recommendation_response(self, raw_text: str, products: list) -> list:
        """
        Parse the JSON output from the Replicate model and map recommended product IDs to full product details.
        This function extracts the JSON array by finding the first '[' and the last ']' in the output.
        """
        recommendations = []
        try:
            start = raw_text.find('[')
            end = raw_text.rfind(']')
            if start == -1 or end == -1:
                logging.error("Could not find JSON array in the output.")
                return recommendations

            # Extract the substring that should be valid JSON
            json_text = raw_text[start:end+1]
            parsed = json.loads(json_text)

        except json.JSONDecodeError:
            logging.error("Failed to parse JSON from extracted text:\n%s", raw_text)
            return recommendations

        if not isinstance(parsed, list):
            logging.error("Parsed JSON is not a list:\n%s", parsed)
            return recommendations

        for item in parsed:
            pid = item.get("id")
            explanation = item.get("explanation", "")
            score = item.get("confidence_score", 5)
            product_data = next((p for p in products if p["id"] == pid), None)
            if product_data:
                recommendations.append({
                    "product": product_data,
                    "explanation": explanation,
                    "confidence_score": score
                })
            else:
                logging.warning("Unknown product ID recommended: %s", pid)
        return recommendations

    def generate_recommendations(self, preferences: dict, browsing_history: list, products: list) -> dict:
        """
        Generate product recommendations using the Replicate model and cache the response.
        """
        prompt = self._create_recommendation_prompt(preferences, browsing_history, products)
        key = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        if key in self.cache:
            logging.info("Using cached Replicate response.")
            return self.cache[key]

        try:
            raw_output = self._call_llm(prompt)
        except Exception as e:
            return {"recommendations": [], "count": 0, "error": str(e)}

        recommendations = self._parse_recommendation_response(raw_output, products)
        result = {"recommendations": recommendations, "count": len(recommendations)}
        self.cache[key] = result
        return result

# For independent testing:
if __name__ == "__main__":
    sample_products = [
        {
            "id": "prod001",
            "name": "Ultra-Comfort Running Shoes",
            "category": "Footwear",
            "price": 89.99,
            "brand": "SportsFlex",
            "tags": ["running", "athletic", "comfortable", "lightweight"]
        },
    ]
    sample_preferences = {
        "priceRange": "all",
        "categories": ["Footwear"],
        "brands": []
    }
    sample_history = ["prod001"]

    service = LLMService()
    recommendations = service.generate_recommendations(sample_preferences, sample_history, sample_products)
    print(json.dumps(recommendations, indent=2))
