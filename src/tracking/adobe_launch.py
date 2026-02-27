"""Adobe Launch (Adobe Experience Platform Tags) API Client."""
import httpx
from typing import Dict, Any
from src.config import settings


class AdobeLaunchClient:
    """
    Adobe Launch API client for automated pixel deployment.
    
    When CM360 generates a pixel, OmniTraffick automatically:
    1. Creates a new "Data Element" for the pixel URL
    2. Creates a "Rule" triggered on page load
    3. Adds an "Action" to inject the pixel
    4. Publishes to the Tag Manager environment
    
    This eliminates manual Tag Manager logins.
    """
    
    def __init__(
        self,
        api_key: str | None = None,
        org_id: str | None = None,
        property_id: str | None = None,
    ):
        """
        Initialize Adobe Launch client.
        
        Args:
            api_key: Adobe I/O API key
            org_id: Adobe Organization ID
            property_id: Launch property ID
        """
        self.api_key = api_key or getattr(settings, 'adobe_launch_api_key', None)
        self.org_id = org_id or getattr(settings, 'adobe_org_id', None)
        self.property_id = property_id or getattr(settings, 'adobe_launch_property_id', None)
        
        if not all([self.api_key, self.org_id, self.property_id]):
            raise ValueError("ADOBE_LAUNCH_API_KEY, ADOBE_ORG_ID, ADOBE_LAUNCH_PROPERTY_ID required")
        
        self.base_url = "https://reactor.adobe.io/properties"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.org_id,
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json;revision=1",
        }
    
    def create_data_element(self, name: str, value: str) -> Dict[str, Any]:
        """
        Create a Data Element in Launch.
        
        Args:
            name: Data element name (e.g., "CM360_DIS_US_META_2026")
            value: Pixel URL
            
        Returns:
            Data element object
        """
        url = f"{self.base_url}/{self.property_id}/data_elements"
        
        payload = {
            "data": {
                "type": "data_elements",
                "attributes": {
                    "name": name,
                    "delegate_descriptor_id": "core::dataElements::constant",
                    "settings": f'{{"value": "{value}"}}',
                    "enabled": True,
                }
            }
        }
        
        response = httpx.post(url, json=payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
    
    def create_rule(
        self,
        rule_name: str,
        data_element_id: str,
    ) -> Dict[str, Any]:
        """
        Create a Rule in Launch.
        
        Args:
            rule_name: Rule name (e.g., "Load CM360 Pixel - DIS Campaign")
            data_element_id: ID of the data element containing pixel URL
            
        Returns:
            Rule object
        """
        url = f"{self.base_url}/{self.property_id}/rules"
        
        payload = {
            "data": {
                "type": "rules",
                "attributes": {
                    "name": rule_name,
                    "enabled": True,
                }
            }
        }
        
        response = httpx.post(url, json=payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        rule = response.json()
        rule_id = rule["data"]["id"]
        
        # Add event (page load trigger)
        self._add_rule_event(rule_id)
        
        # Add action (inject pixel)
        self._add_rule_action(rule_id, data_element_id)
        
        return rule
    
    def _add_rule_event(self, rule_id: str) -> Dict[str, Any]:
        """
        Add "Page Bottom" event to rule (fires on page load).
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Event object
        """
        url = f"{self.base_url}/{self.property_id}/rules/{rule_id}/rule_components"
        
        payload = {
            "data": {
                "type": "rule_components",
                "attributes": {
                    "delegate_descriptor_id": "core::events::page-bottom",
                    "settings": "{}",
                    "order": 0,
                }
            }
        }
        
        response = httpx.post(url, json=payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
    
    def _add_rule_action(self, rule_id: str, data_element_id: str) -> Dict[str, Any]:
        """
        Add "Custom Code" action to inject pixel.
        
        Args:
            rule_id: Rule ID
            data_element_id: Data element ID with pixel URL
            
        Returns:
            Action object
        """
        url = f"{self.base_url}/{self.property_id}/rules/{rule_id}/rule_components"
        
        # JavaScript to inject 1x1 pixel
        js_code = f"""
        (function() {{
            var img = document.createElement('img');
            img.src = {{{{ {data_element_id} }}}};
            img.width = 1;
            img.height = 1;
            img.style.display = 'none';
            document.body.appendChild(img);
        }})();
        """
        
        payload = {
            "data": {
                "type": "rule_components",
                "attributes": {
                    "delegate_descriptor_id": "core::actions::custom-code",
                    "settings": f'{{"source": "{js_code}", "language": "javascript"}}',
                    "order": 0,
                }
            }
        }
        
        response = httpx.post(url, json=payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
    
    def publish_library(self, library_name: str) -> Dict[str, Any]:
        """
        Create and publish a library to deploy changes.
        
        Args:
            library_name: Library name
            
        Returns:
            Build object
        """
        # 1. Create library
        library_url = f"{self.base_url}/{self.property_id}/libraries"
        
        library_payload = {
            "data": {
                "type": "libraries",
                "attributes": {
                    "name": library_name,
                }
            }
        }
        
        response = httpx.post(library_url, json=library_payload, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        library = response.json()
        library_id = library["data"]["id"]
        
        # 2. Build library
        build_url = f"{self.base_url}/{self.property_id}/libraries/{library_id}/builds"
        
        response = httpx.post(build_url, headers=self.headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
    
    def deploy_cm360_pixel(
        self,
        campaign_name: str,
        cm360_pixel_url: str,
    ) -> Dict[str, Any]:
        """
        Full workflow: Create data element, rule, and publish.
        
        Args:
            campaign_name: Campaign name (taxonomy)
            cm360_pixel_url: CM360 impression pixel URL
            
        Returns:
            Dict with data_element_id, rule_id, build_id
        """
        # Step 1: Create data element
        data_element_name = f"CM360_{campaign_name.replace(' ', '_')}"
        data_element = self.create_data_element(data_element_name, cm360_pixel_url)
        data_element_id = data_element["data"]["id"]
        
        # Step 2: Create rule
        rule_name = f"Load CM360 Pixel - {campaign_name}"
        rule = self.create_rule(rule_name, data_element_id)
        rule_id = rule["data"]["id"]
        
        # Step 3: Publish
        library_name = f"Deploy {campaign_name} Tracking"
        build = self.publish_library(library_name)
        build_id = build["data"]["id"]
        
        return {
            "data_element_id": data_element_id,
            "rule_id": rule_id,
            "build_id": build_id,
            "status": "published",
        }
